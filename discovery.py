"""Discovery of candidate resources from external awesome lists and forks.

Reads the sources configured in `discovery-sources.toml`, extracts the GitHub
repositories and external URLs they link, and produces a review report. It
never writes curated data: discovery stays separate from curation.

Deliberately a separate script from pipeline.py, like csms.py. It imports
pipeline only to reuse the HTTP cache, the README fetch and the README scan.

The functions that extract, normalize, classify and render take data in and
return data out; only a thin layer does I/O: `fetch_source` / `fetch_sources`,
`load_tracked` (the catalogue files), `run` (repo lookups) and `main` (the
report).

    python discovery.py --sources discovery-sources.toml --report report.md [--token T]
"""

import argparse
import os
import pathlib
import re
import sys
import tomllib
from dataclasses import dataclass, field
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests

import pipeline

# --- Configuration ------------------------------------------------------------

_REPO_RE = re.compile(r"[\w.-]+/[\w.-]+")
# Source names land in a Markdown table and in code spans of the report.
_NAME_RE = re.compile(r"[\w./ -]+")


class ConfigError(Exception):
  """The sources configuration is missing or invalid."""


@dataclass(frozen=True)
class Source:
  """One configured source: a GitHub repo (its README) or a raw Markdown URL."""
  name: str
  repo: str | None = None
  url: str | None = None


def load_sources(path):
  """Read and validate the `[[sources]]` tables of a TOML file, in file order."""
  try:
    with open(path, "rb") as f:
      config = tomllib.load(f)
  except (OSError, tomllib.TOMLDecodeError) as e:
    raise ConfigError(f"{path}: {e}") from e
  entries = config.get("sources")
  if not isinstance(entries, list) or not entries:
    raise ConfigError(f"{path}: no [[sources]] configured")
  sources, seen = [], set()
  for i, entry in enumerate(entries, 1):
    where = f"{path}: source #{i}"
    unknown = set(entry) - {"name", "repo", "url"}
    if unknown:
      raise ConfigError(f"{where}: unknown key(s) {', '.join(sorted(unknown))}")
    name = entry.get("name")
    if not isinstance(name, str) or not name.strip():
      raise ConfigError(f"{where}: `name` is required")
    if not _NAME_RE.fullmatch(name):
      raise ConfigError(f"{where}: `name` may hold only letters, digits, `_`, `.`, `/`, `-`"
                        " and spaces")
    if name in seen:
      raise ConfigError(f"{where}: duplicate name {name!r}")
    seen.add(name)
    repo, url = entry.get("repo"), entry.get("url")
    if (repo is None) == (url is None):
      raise ConfigError(f"{where} ({name}): set exactly one of `repo` or `url`")
    if repo is not None and not (isinstance(repo, str) and _REPO_RE.fullmatch(repo)):
      raise ConfigError(f"{where} ({name}): `repo` must be owner/name")
    if url is not None and not (isinstance(url, str) and re.match(r"https?://", url)):
      raise ConfigError(f"{where} ({name}): `url` must be an http(s) URL")
    sources.append(Source(name, repo=repo, url=url))
  return sources


# --- Fetching -----------------------------------------------------------------

# Seconds before an unresponsive `url` source counts as a failed fetch.
URL_TIMEOUT = 30


def _fetch_url(url):
  """Body of a `url` source, `""` on a 404, None on any other failure.

  Fetched directly, without the HTTP cache or any header, and bounded by
  `URL_TIMEOUT`: an arbitrary host must not hang the run.
  """
  try:
    response = requests.get(url, timeout=URL_TIMEOUT)
  except requests.RequestException:
    return None
  if response.status_code == 404:
    return ""
  return response.text if response.status_code < 400 else None


def fetch_source(source, headers):
  """Return `(markdown, None)`, or `(None, reason)` when the source is unread.

  `not found` for a deleted source (a 404, or a repo without README) and
  `fetch failed` for a failed run (rate limit, 5xx, network, timeout): a source
  that could not be read must never read as one that links nothing. Only the
  GitHub API request carries `headers`; a `url` source goes out with none.
  """
  if source.repo:
    text = pipeline.fetch_readme_content(source.repo, headers)
  else:
    text = _fetch_url(source.url)
  if text is None:
    return None, "fetch failed"
  if not text:
    return None, "not found"
  return text, None


def fetch_sources(sources, headers):
  """Fetch every source; return `({name: markdown}, {name: failure reason})`."""
  texts, failures = {}, {}
  for source in sources:
    text, reason = fetch_source(source, headers)
    if reason:
      failures[source.name] = reason
    else:
      texts[source.name] = text
  return texts, failures


# --- Extraction and normalization ---------------------------------------------

_URL_RE = re.compile(r"""https?://[^\s<>()\[\]"'`]+""")
_IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)|<img\b[^>]*>", re.IGNORECASE)
_TRACKING_PARAMS = {"fbclid", "gclid", "mc_cid", "mc_eid", "ref", "ref_src"}
# Badge services: their links decorate a project, they are not one.
BADGE_HOSTS = {"img.shields.io", "badge.fury.io", "badgen.net", "travis-ci.org",
               "travis-ci.com", "codecov.io", "coveralls.io", "app.codacy.com"}


def _is_github_host(host):
  return (host == "github.com" or host.endswith(".github.com")
          or host.endswith("githubusercontent.com") or host.endswith("githubassets.com"))


def normalize_url(url):
  """Canonical form of an external URL, used to dedupe and to compare.

  Lowercases scheme and host, drops the fragment and tracking parameters
  (`utm_*`, `fbclid`, ...), sorts the other parameters, strips one trailing
  `/` and the punctuation Markdown leaves after a link.
  """
  parts = urlsplit(url.rstrip(").,;"))
  query = sorted((k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
                 if not (k.lower().startswith("utm_") or k.lower() in _TRACKING_PARAMS))
  path = parts.path[:-1] if parts.path.endswith("/") else parts.path
  return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, urlencode(query), ""))


def _external_urls(line):
  """Normalized non-GitHub, non-badge URLs of one line, images skipped."""
  urls = []
  for raw in _URL_RE.findall(_IMAGE_RE.sub("", line)):
    url = normalize_url(raw)
    host = urlsplit(url).hostname or ""
    if host and not _is_github_host(host) and host not in BADGE_HOSTS:
      urls.append(url)
  return urls


_GIST_RE = re.compile(r"""gist\.github\.com/[^\s<>()\[\]"'`]*""", re.IGNORECASE)
# GitHub owners whose paths are uploads, not repositories.
_NON_REPO_OWNERS = {"user-attachments"}


def _repo_names(text):
  """`pipeline.repo_names_from_text`, minus images, gists and uploads."""
  names = pipeline.repo_names_from_text(_GIST_RE.sub("", _IMAGE_RE.sub("", text)))
  return [n for n in names if n.split("/")[0].lower() not in _NON_REPO_OWNERS]


def extract_links(text):
  """Return `({owner/repo: line}, {normalized url: line})` for one source.

  Repos come from `pipeline.repo_names_from_text`, so the same rules as the
  README scan apply, except that images, gists and `user-attachments`
  uploads are skipped. Each value is the first source line (trimmed) that
  links the candidate: the list's own words about it.
  """
  repos, urls = {}, {}
  lines = [line.strip() for line in text.splitlines()]
  names = _repo_names(text)
  for line in lines:
    for name in _repo_names(line):
      repos.setdefault(name.lower(), line)
    for url in _external_urls(line):
      urls.setdefault(url, line)
  return {name: repos[name.lower()] for name in names}, urls


@dataclass
class Candidate:
  """A resource linked by one or more sources.

  `key` is the dedupe key (case-folded owner/repo, or the normalized URL),
  `name` the form first linked, `sources` the sorted names of the sources
  that link it, `context` the line that links it, per source.
  """
  key: str
  name: str
  sources: list = field(default_factory=list)
  context: dict = field(default_factory=dict)


def _merge(found, source, name, key, line):
  candidate = found.setdefault(key, Candidate(key, name))
  candidate.sources.append(source)
  candidate.context[source] = line


def collect_candidates(texts):
  """Dedupe the links of `{source name: markdown}` across sources.

  Returns `(repo candidates, url candidates)`, each sorted by key. Sources
  are read in sorted name order, so the output never depends on dict order.
  """
  repos, urls = {}, {}
  for source in sorted(texts):
    repo_links, url_links = extract_links(texts[source])
    for name, line in repo_links.items():
      _merge(repos, source, name, name.lower(), line)
    for url, line in url_links.items():
      _merge(urls, source, url, url, line)
  return ([repos[k] for k in sorted(repos)], [urls[k] for k in sorted(urls)])


# --- Catalogue: what is already tracked ---------------------------------------

CATALOGUE_FILES = (pipeline.README_PATH, "legacy-projects.md", "csms.md")
# A 404 on a repo lookup, told apart from a transient failure (None).
NOT_FOUND = object()


@dataclass(frozen=True)
class Tracked:
  """The catalogue as discovery compares against it.

  `names` maps each tracked repo, case-folded, to its catalogue spelling;
  `rows` holds the classification rows by folded name; `urls` the normalized
  URLs the catalogue files link.
  """
  names: dict
  rows: dict
  urls: frozenset

  @property
  def repos(self):
    return set(self.names)


def build_tracked(classifications, texts, additional=(), codeberg=()):
  """Tracked sets from a classifications cache and the catalogue Markdown texts."""
  folded = pipeline._fold_case(classifications)
  names = {key: full_name for key, (full_name, _) in folded.items()}
  linked = [n for text in texts for n in pipeline.repo_names_from_text(text)]
  for name in [*linked, *sorted(additional), *sorted(codeberg)]:
    names.setdefault(name.lower(), name)
  urls = {normalize_url(u) for text in texts for u in _URL_RE.findall(text)}
  urls |= {normalize_url(pipeline.CODEBERG_WEB + name) for name in codeberg}
  return Tracked(names, {k: row for k, (_, row) in folded.items()}, frozenset(urls))


def load_tracked(root="."):
  """Read the catalogue datasets of the repository at `root`."""
  for name in (pipeline.CLASSIFICATIONS_PATH, *CATALOGUE_FILES):
    path = os.path.join(root, name)
    if not os.path.exists(path):
      raise ConfigError(f"{path}: catalogue file not found (run from the repo root)")
  texts = [pathlib.Path(root, name).read_text(encoding="utf-8") for name in CATALOGUE_FILES]
  classifications = pipeline.load_classifications(os.path.join(root, pipeline.CLASSIFICATIONS_PATH))
  return build_tracked(classifications, texts, pipeline.ADDITIONAL_REPOS, pipeline.CODEBERG_REPOS)


# --- Resolution and statuses --------------------------------------------------

STATUSES = ("new", "changed", "unavailable", "excluded", "existing")


@dataclass
class Result:
  """One classified candidate; `kind` is `repo` or `url`.

  For a repo, `aliases` are the names the sources link, `data` the
  `/repos/{name}` object, `old` the stale names of a `changed` one and
  `stale` the side holding them (`source` / `catalogue`).
  """
  status: str
  kind: str
  name: str
  sources: list
  context: dict
  reason: str = ""
  aliases: list = field(default_factory=list)
  stale: str = ""
  old: list = field(default_factory=list)
  data: dict | None = None
  related: list = field(default_factory=list)


def _merge_by_canonical(candidates, lookups):
  """Group repo candidates by the canonical name their lookup resolved to."""
  groups = {}
  for c in candidates:
    data = lookups.get(c.key)
    resolved = isinstance(data, dict) and data.get("full_name")
    group = groups.setdefault(data["full_name"].lower() if resolved else c.key,
                              {"aliases": set(), "sources": set(), "context": {},
                               "data": None, "missing": True})
    group["aliases"].add(c.name)
    group["sources"].update(c.sources)
    for source in sorted(c.context):
      group["context"].setdefault(source, c.context[source])
    if resolved:
      group["data"] = data
    group["missing"] = group["missing"] and data is NOT_FOUND
  return groups


def _related(name, tracked):
  """Tracked repos with the same short name as `name` under another owner."""
  short = name.lower().split("/")[1]
  return sorted((n for k, n in tracked.names.items()
                 if k.split("/")[1] == short and k != name.lower()), key=str.lower)


def _repo_status(group, tracked, source_repos, lookups, related):
  """`(status, reason, stale, old)` by the ordered rules of the design."""
  aliases = {a.lower() for a in group["aliases"]}
  canonical = group["data"]["full_name"].lower() if group["data"] else None
  names = aliases | ({canonical} if canonical else set())
  if names & {r.lower() for r in pipeline.EXCLUDED_REPOS}:
    return "excluded", "EXCLUDED_REPOS", "", []
  if names & {r.lower() for r in source_repos}:
    return "excluded", "discovery source", "", []
  if any(pipeline._is_deprecated(tracked.rows[n]) for n in sorted(names & set(tracked.rows))):
    return "excluded", "deprecated", "", []
  known = aliases & tracked.repos
  if canonical is None:
    if group["missing"]:
      return "unavailable", "not found (tracked)" if known else "not found", "", []
    return ("existing", "", "", []) if known else ("unavailable", "lookup failed", "", [])
  if canonical in tracked.repos:
    stale = sorted((a for a in group["aliases"] if a.lower() != canonical), key=str.lower)
    return ("changed", "", "source", stale) if stale else ("existing", "", "", [])
  if known:
    return "changed", "", "catalogue", sorted((tracked.names[k] for k in known), key=str.lower)
  # The catalogue may hold an old name the source no longer links: a related
  # tracked name that resolves to this repository is stale in the catalogue.
  renamed = [n for n in related if isinstance(lookups.get(n.lower()), dict)
             and lookups[n.lower()].get("full_name", "").lower() == canonical]
  if renamed:
    return "changed", "", "catalogue", renamed
  return "new", "", "", []


def classify(repo_candidates, url_candidates, lookups, tracked, source_repos=()):
  """Classify candidates against the catalogue, sorted by status then name.

  `lookups` maps each repo candidate key to its `/repos/{name}` object,
  `NOT_FOUND` (404) or None (transient failure). It may also hold the
  case-folded related tracked names of a candidate (see `related_names`): one
  that resolves to the candidate makes it `changed` instead of `new`.
  """
  results = []
  for key, group in _merge_by_canonical(repo_candidates, lookups).items():
    aliases = sorted(group["aliases"], key=str.lower)
    data = group["data"]
    name = data["full_name"] if data else aliases[0]
    related = _related(name, tracked)
    status, reason, stale, old = _repo_status(group, tracked, source_repos, lookups, related)
    results.append(Result(status, "repo", name, sorted(group["sources"]), group["context"],
                          reason, aliases, stale, old, data,
                          related if status == "new" else []))
  for c in url_candidates:
    status = "existing" if c.key in tracked.urls else "new"
    results.append(Result(status, "url", c.name, list(c.sources), c.context))
  return sorted(results, key=lambda r: (STATUSES.index(r.status), r.kind, r.name.lower(), r.name))


def related_names(results, lookups):
  """Sorted related tracked names of the `new` repos, not looked up yet.

  Only renames and transfers that keep the short name are caught this way.
  """
  return sorted({n for r in results if r.kind == "repo" and r.status == "new"
                 for n in r.related if n.lower() not in lookups}, key=str.lower)


# --- Report -------------------------------------------------------------------

# `@` or `#` followed by a letter or digit: a mention or an issue reference on GitHub.
_PING_RE = re.compile(r"([@#])(?=[^\W_])")


def _text(value):
  """A metadata value as report text: blank when unknown, no raw HTML, and no
  mention or issue reference (a zero-width space after `@` / `#`), so the
  rolling issue pings no one with text taken from external repositories.
  """
  if value is None:
    return ""
  return _PING_RE.sub("\\1\u200b", " ".join(str(value).split()).replace("<", "&lt;"))


def _code(line):
  """A source line as a code span, its list marker dropped, link syntax kept."""
  line = re.sub(r"^(?:[-*+]|\d+\.)\s+", "", line)
  ticks = "`" * (max((len(m) for m in re.findall(r"`+", line)), default=0) + 1)
  pad = " " if line.startswith("`") or line.endswith("`") else ""
  return f"{ticks}{pad}{line}{pad}{ticks}"


def _field(label, value):
  return f"- {label}: {_text(value)}".rstrip()


def _new_repo(r):
  data = r.data or {}
  archived = data.get("archived")
  lines = [f"#### [{r.name}]({data.get('html_url') or 'https://github.com/' + r.name})", "",
           _field("Sources", ", ".join(r.sources)),
           _field("Description", data.get("description")),
           _field("Archived", None if archived is None else ("yes" if archived else "no")),
           _field("Last push", data.get("pushed_at")),
           _field("Licence", (data.get("license") or {}).get("spdx_id")),
           _field("Related tracked projects", ", ".join(r.related))]
  lines += [f"- Context ({s}): {_code(r.context[s])}" for s in sorted(r.context)]
  return lines + [""]


def _section(title, lines):
  return [f"## {title}", "", *(lines or ["None."]), ""]


def render_report(results, source_names, failures):
  """The Markdown review report: deterministic, so identical inputs give identical bytes."""
  by = {s: [r for r in results if r.status == s] for s in STATUSES}
  out = ["# Discovery report", "",
         "Candidates linked by external lists, compared with the catalogue.",
         "Nothing here is added to the catalogue without a review.", "",
         "## Summary", "", "| Status | GitHub repos | Other URLs |", "| --- | --- | --- |"]
  out += [f"| {s} | {sum(r.kind == 'repo' for r in by[s])} | {sum(r.kind == 'url' for r in by[s])} |"
          for s in STATUSES]
  out += ["", f"| Source | {' | '.join(STATUSES)} |", "| --- |" + " --- |" * len(STATUSES)]
  out += [f"| {n} | " + " | ".join(str(sum(n in r.sources for r in by[s])) for s in STATUSES) + " |"
          for n in sorted(source_names) if n not in failures]
  out.append("")
  out += _section("Failed sources", [f"- `{n}`: {failures[n]}" for n in sorted(failures)])
  out += ["## New", "", "### GitHub repositories", ""]
  out += [line for r in by["new"] if r.kind == "repo" for line in _new_repo(r)] or ["None.", ""]
  out += ["### Other URLs", ""]
  urls = [f"- <{r.name}> (sources: {', '.join(r.sources)})" for r in by["new"] if r.kind == "url"]
  out += [*(urls or ["None."]), ""]
  out += _section("Changed", [
      f"- {', '.join(r.old)} -> {r.name}, stale in the {r.stale} (sources: {', '.join(r.sources)})"
      for r in by["changed"]])
  for status in ("unavailable", "excluded"):
    out += _section(status.capitalize(), [
        f"- {r.name}: {r.reason} (sources: {', '.join(r.sources)})" for r in by[status]])
  repos = sum(r.kind == "repo" for r in by["existing"])
  out += _section("Existing", [
      f"Already tracked: {repos} GitHub repositories, {len(by['existing']) - repos} other URLs."])
  return "\n".join(out).rstrip("\n") + "\n"


# --- Rolling issue ------------------------------------------------------------

ISSUE_MARKER = "<!-- discovery-report -->"
ISSUE_BODY_LIMIT = 65536  # GitHub's maximum issue body length, in characters
# Kept, in this order, when the whole report does not fit in the issue body.
ISSUE_SECTIONS = ("Summary", "New", "Changed", "Unavailable")


def _report_sections(report):
  """The report split at its `## ` headings: `(title, text)` pairs, preamble first."""
  sections = [("", [])]
  for line in report.splitlines(keepends=True):
    if line.startswith("## "):
      sections.append((line[3:].strip(), []))
    sections[-1][1].append(line)
  return [(title, "".join(lines)) for title, lines in sections]


def issue_body(report, workflow_url, limit=ISSUE_BODY_LIMIT):
  """The rolling issue's body: marker, workflow link, then the report, within `limit` characters.

  Depends only on its arguments, and `workflow_url` is the same for every run,
  so an unchanged report gives an unchanged body. When the whole report does
  not fit, keep its preamble, the counts and the actionable sections
  (`ISSUE_SECTIONS`), whole while they fit; the first one that does not fit is
  cut on a line boundary, the rest dropped, and a closing line points at the
  workflow's artifacts.
  """
  head = (f"{ISSUE_MARKER}\n"
          f"Latest report of the [weekly discovery workflow]({workflow_url}); each run's "
          "`discovery-report` artifact holds the full report.\n\n")
  body = head + report
  if len(body) <= limit:
    return body
  note = (f"\n_Truncated to fit an issue: the full report is the `discovery-report` "
          f"artifact of the latest run of the [workflow]({workflow_url})._\n")
  budget = limit - len(note)
  if len(head) > budget:
    raise ValueError(f"an issue body limit of {limit} cannot hold the marker and the note")
  sections = dict(_report_sections(report))
  kept = head
  for title in ("", *ISSUE_SECTIONS):
    text = sections.get(title, "")
    if len(kept) + len(text) <= budget:
      kept += text
      continue
    for line in text.splitlines(keepends=True):
      if len(kept) + len(line) > budget:
        break
      kept += line
    break
  return kept.rstrip("\n") + "\n" + note


# --- Run and CLI --------------------------------------------------------------

def _source_repos(sources, headers):
  """The configured source repos plus the current name each resolves to.

  A renamed or transferred list may link itself under its new name. A failed
  lookup keeps only the configured name.
  """
  names = set()
  for s in sources:
    if s.repo:
      names.add(s.repo)
      data = pipeline.get_repo_data(s.repo, headers, missing=NOT_FOUND)
      if isinstance(data, dict) and data.get("full_name"):
        names.add(data["full_name"])
  return names


def run(sources, tracked, headers):
  """Fetch, resolve and classify; return `(report, whether any source was read)`."""
  texts, failures = fetch_sources(sources, headers)
  repos, urls = collect_candidates(texts)
  source_repos = _source_repos(sources, headers)
  lookups = {c.key: pipeline.get_repo_data(c.name, headers, missing=NOT_FOUND) for c in repos}
  results = classify(repos, urls, lookups, tracked, source_repos)
  related = related_names(results, lookups)
  if related:
    lookups.update({n.lower(): pipeline.get_repo_data(n, headers, missing=NOT_FOUND)
                    for n in related})
    results = classify(repos, urls, lookups, tracked, source_repos)
  return render_report(results, [s.name for s in sources], failures), bool(texts)


def main(argv=None):
  """CLI entry point. Writes only `--report`, `--issue-body` when given, and the
  disposable HTTP cache.

  Exit 0 when at least one source was read, 1 when every source failed (the
  report still lists the failures), 2 on a configuration error.
  """
  parser = argparse.ArgumentParser(description="Discover candidates from external lists.")
  parser.add_argument("--sources", required=True, help="TOML file of [[sources]]")
  parser.add_argument("--report", required=True, help="Markdown report to write")
  parser.add_argument("--token", help="GitHub token")
  parser.add_argument("--issue-body", help="also write the rolling issue's body here")
  parser.add_argument("--workflow-url", help="the workflow whose runs' artifacts hold the full report")
  args = parser.parse_args(argv)
  if bool(args.issue_body) != bool(args.workflow_url):
    parser.error("--issue-body and --workflow-url go together")
  try:
    sources = load_sources(args.sources)
    tracked = load_tracked()
  except ConfigError as e:
    print(f"error: {e}", file=sys.stderr)
    return 2
  report, read = run(sources, tracked, pipeline.auth_headers(args.token))
  os.makedirs(os.path.dirname(args.report) or ".", exist_ok=True)
  with open(args.report, "w", encoding="utf-8", newline="") as f:
    f.write(report)
  if args.issue_body:
    os.makedirs(os.path.dirname(args.issue_body) or ".", exist_ok=True)
    with open(args.issue_body, "w", encoding="utf-8", newline="") as f:
      f.write(issue_body(report, args.workflow_url))
  return 0 if read else 1


if __name__ == "__main__":
  sys.exit(main())
