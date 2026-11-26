"""Discovery of candidate resources from external awesome lists and forks.

Reads the sources configured in `discovery-sources.toml`, extracts the GitHub
repositories and external URLs they link, and produces a review report. It
never writes curated data: discovery stays separate from curation.

Deliberately a separate script from pipeline.py, like csms.py. It imports
pipeline only to reuse the HTTP cache, the README fetch and the README scan.

The functions that extract, normalize and dedupe take data in and return data
out; only `fetch_source` / `fetch_sources` do I/O.
"""

import re
import tomllib
from dataclasses import dataclass, field
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import pipeline

# --- Configuration ------------------------------------------------------------

_REPO_RE = re.compile(r"[\w.-]+/[\w.-]+")


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

def fetch_source(source, headers):
  """Return `(markdown, None)`, or `(None, reason)` when the source is unread.

  `not found` for a deleted source (a 404, or a repo without README) and
  `fetch failed` for a failed run (rate limit, 5xx, network): a source that
  could not be read must never read as one that links nothing. Only the GitHub
  API request carries `headers`; a `url` source goes out with none.
  """
  if source.repo:
    text = pipeline.fetch_readme_content(source.repo, headers)
  else:
    text = pipeline.github_request_cached(source.url, headers={}, missing="", raw=True)
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


def extract_links(text):
  """Return `({owner/repo: line}, {normalized url: line})` for one source.

  Repos come from `pipeline.repo_names_from_text`, so the same rules as the
  README scan apply. Each value is the first source line (trimmed) that
  links the candidate: the list's own words about it.
  """
  repos, urls = {}, {}
  lines = [line.strip() for line in text.splitlines()]
  names = pipeline.repo_names_from_text(text)
  for line in lines:
    for name in pipeline.repo_names_from_text(line):
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
