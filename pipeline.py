"""EV-charging repository discovery pipeline.

Two stages, connected by a reviewable CSV:

    ingest  -> repos.csv           GitHub raw data + quality signals (no LLM)
    enrich  -> repos.enriched.csv  category classification via an LLM CLI (claude/codex/copilot)

Run `python pipeline.py <stage> --help` for stage options.
"""

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from collections import defaultdict
from datetime import datetime

import requests

# --- Cache -------------------------------------------------------------------

CACHE_DIR = "cache_github"
CACHE_TTL = 24 * 3600  # 1 day (in seconds)

os.makedirs(CACHE_DIR, exist_ok=True)

# --- Discovery configuration -------------------------------------------------

BASE_URL = "https://api.github.com"
MAX_PAGES = 10
DORMANT_DAYS = 365  # no push in >= 1 year => dormant

TOPICS = {"ocpp", "ocpi", "emobility", "e-mobility", "iso15118"}
STARRED_USERS = {"juherr", "mateogreil"}
# Curated GitHub Stars lists sourced for discovery, as (owner, list-slug). Their
# repos become candidates (like ADDITIONAL_REPOS); distinct from STARRED_USERS,
# whose full star sets are only a promotion signal. GraphQL-only, so ingest needs
# a token to reach these (see get_starred_list_repos).
STARRED_LISTS = {
  ("juherr", "ev"),
  ("mateogreil", "ev-mobility"),
}
SELF_REPO = "juherr/awesome-ev-charging"  # its contributors' own repos get a promotion
EXCLUDED_REPOS = {
  SELF_REPO,
  "ocpi/ocpi",     # the OCPI spec itself — already linked in the Specifications section
  "hubject/oicp",  # the OICP spec itself — already linked in the Specifications section
}
README_PATH = "README.md"  # the curated list; its GitHub links seed a 4th ingest source
# `render --readme` replaces the text between these HTML comment markers in README:
# one pair wraps the project listing, one pair wraps its entries in the Contents.
README_MARKER_BEGIN = "<!-- BEGIN GENERATED PROJECTS -->"
README_MARKER_END = "<!-- END GENERATED PROJECTS -->"
README_TOC_BEGIN = "<!-- BEGIN GENERATED TOC -->"
README_TOC_END = "<!-- END GENERATED TOC -->"
# Durable, committed LLM cache: full_name -> pushed_at, categories, description.
# Keeps expensive classifications across clones so only new/updated repos re-hit
# the model. The bulky repos*.csv stay git-ignored.
CLASSIFICATIONS_PATH = "classifications.csv"
ADDITIONAL_REPOS = {
  "SAFE-eV/OCMF-Open-Charge-Metering-Format",
  "SAFE-eV/transparenzsoftware",
  "hubject/oicp",
  "solidstudiosh/ocpi-schema",
  "NOWUM/pyOCPI",
  "gaia-charge/ocpi-types",
  "TECHS-Technological-Solutions/ocpi",
  "ChargeMap/ocpi-protocol",
  "ChargeMap/autocharge-vehicles-database"
}
CATEGORY_TREE = {
  "OCPP": ["Server", "Simulator", "Libraries", "Misc"],
  "OCPI": ["Server", "Simulator", "Libraries", "Misc"],
  "iso15118": ["Plug&Charge", "Misc"],
  "OICP": ["Server", "Simulator", "Libraries", "Misc"],
  "EMIP": ["Server", "Simulator", "Libraries", "Misc"],
  "OIOI": ["Server", "Simulator", "Libraries", "Misc"],
  "Eichrecht": ["Misc"],
  "Other": []
}

# The classifier invents free-form subcategories under "Other", which fragments
# near-synonyms into 1-repo buckets. This map folds variants into a canonical
# label at render time (matched case-insensitively, so pure case dups also merge).
SUBCATEGORY_ALIASES = {
  # Maps, station finders, route planners, Open Charge Map client libraries
  "charging station finder": "Maps & route planning",
  "charging station map": "Maps & route planning",
  "route planner": "Maps & route planning",
  "open charge map library": "Maps & route planning",
  "open charge map sdk": "Maps & route planning",
  # EVSE firmware
  "evse controller": "EVSE firmware",
  "evse firmware": "EVSE firmware",
  "evse gateway firmware": "EVSE firmware",
  # Home Assistant
  "home assistant integration": "Home Assistant integration",
  "home assistant automation": "Home Assistant integration",
  # EEBUS libraries
  "eebus libraries": "EEBUS Libraries",
  "eebus library": "EEBUS Libraries",
  # Mobile app (also folds the "Mobile App" case variant)
  "mobile app": "Mobile app",
  # Charging management
  "charging management platform": "Charging management system",
  "charging management system": "Charging management system",
  # Energy management (generic only; home/DER kept separate)
  "energy management": "Energy management",
  "energy management system": "Energy management",
  # Security
  "security / intrusion detection": "Security",
  "security testing": "Security",
  "pki/security": "Security",
  # Smart home
  "smart home integration": "Smart home integration",
  "smart home adapter": "Smart home integration",
  "home automation adapter": "Smart home integration",
}

# Manual per-repo category overrides for repos the classifier mis-files (e.g.
# under a bare "Other" with no subcategory). full_name (lowercased) -> the
# category string that replaces the classifier's, in the same "Main > Sub"
# (pipe-joined) form. Applied at render time, so it survives re-classification
# and `enrich --refresh`.
CATEGORY_OVERRIDES = {
  "dalathegreat/battery-emulator": "Other > Battery",
  "mnh-jansson/open-battery-information": "Other > Battery",
  "remontsuri/ev-qa-framework": "Other > Battery",
  "izivia/ocpp-toolkit": "OCPP > Libraries",  # a Kotlin library, not a simulator
}

# Skill agent used by the `enrich --classifier claude` backend (see .claude/agents/).
CLASSIFIER_AGENT = "repo-classifier"
CLASSIFIER_MODEL = "claude-haiku-4-5-20251001"
# Optional model for the `enrich --classifier copilot` backend; empty = copilot's
# default (auto). Override via the constant if a specific model is desired.
CLASSIFIER_COPILOT_MODEL = ""

# The Claude backend gets role + output format from the agent file; the codex
# and copilot backends have no agent definition, so they carry the same contract
# in-prompt.
CLASSIFIER_INSTRUCTIONS = (
  "You analyze a GitHub repository related to EV charging, using its own "
  "description and its README. Produce two things:\n"
  "1) a concise, factual one-sentence description (English, no marketing) of what "
  "the project is and does;\n"
  "2) its categories from the taxonomy below — one or more main categories, each "
  "with an existing subcategory or a short proposed one.\n"
  "Do not run any commands or tools — everything you need is below. Respond with "
  "ONLY, no preamble:\n"
  "Description: <one sentence>\n"
  "Categories:\n- Main > Sub\n- Main"
)

# Known protocol versions — used to keep only real version mentions from READMEs.
OCPP_VERSIONS = ["1.2", "1.5", "1.6", "2.0", "2.0.1", "2.1"]
OCPI_VERSIONS = ["2.0", "2.1", "2.1.1", "2.2", "2.2.1", "2.3", "2.3.0"]

CSV_FIELDS = [
  "full_name", "html_url", "description", "language", "license",
  "stars", "forks", "open_issues",
  "topics", "topic_matches",
  "pushed_at", "days_since_push", "dormant", "archived", "created_at",
  "is_fork", "parent_full_name",
  "starred_by", "promoted", "by_contributor", "source",
]


# --- GitHub HTTP with on-disk cache ------------------------------------------

def github_request_cached(url, headers=None, ttl=CACHE_TTL):
  """Fetch a GitHub API URL, caching the raw response on disk.

  Returns the JSON-decoded body (or raw text when Accept requests raw), or
  None on error.
  """
  key = hashlib.md5(url.encode()).hexdigest()
  ext = ".json" if "raw" not in (headers or {}).get("Accept", "") else ".txt"
  cache_path = os.path.join(CACHE_DIR, key + ext)

  if os.path.exists(cache_path) and (time.time() - os.path.getmtime(cache_path) < ttl):
    with open(cache_path, "r", encoding="utf-8") as f:
      return json.load(f) if ext == ".json" else f.read()

  try:
    r = requests.get(url, headers=headers or {})
    r.raise_for_status()
    content = r.text
    with open(cache_path, "w", encoding="utf-8") as f:
      f.write(content)
    return json.loads(content) if ext == ".json" else content
  except Exception as e:
    print(f"⚠️ GitHub request failed: {e}")
    return None


def auth_headers(token):
  """Build the GitHub auth headers, or empty headers when no token is given."""
  return {"Authorization": f"token {token}"} if token else {}


def get_repo_data(full_name, headers):
  """Return the full repository object from /repos/{owner}/{repo}."""
  return github_request_cached(f"{BASE_URL}/repos/{full_name}", headers=headers)


def fetch_readme_content(repo_full_name, headers):
  """Fetch the raw Markdown README of a repository (cached)."""
  url = f"{BASE_URL}/repos/{repo_full_name}/readme"
  headers = dict(headers or {})
  headers["Accept"] = "application/vnd.github.v3.raw"
  return github_request_cached(url, headers)


def paginate(url, headers, params=None, cap=None, throttle=0):
  """Yield items from a paginated GitHub endpoint (a bare list or {"items": [...]})."""
  page = 1
  while cap is None or page <= cap:
    query = dict(params or {}, per_page=100, page=page)
    response = requests.get(url, headers=headers, params=query)
    if response.status_code != 200:
      print(f"⚠️  {url}: HTTP {response.status_code}")
      break
    body = response.json()
    items = body.get("items", []) if isinstance(body, dict) else body
    if not items:
      break
    yield from items
    if len(items) < 100:
      break
    page += 1
    if not headers and throttle:
      time.sleep(throttle)


def get_starred_repos_for_user(user, headers):
  """Return the set of full_names starred by a user."""
  url = f"{BASE_URL}/users/{user}/starred"
  return {item["full_name"] for item in paginate(url, headers, throttle=1)}


GRAPHQL_URL = f"{BASE_URL}/graphql"


def _graphql(query, variables, headers):
  """POST a GraphQL query; return the `data` object or None on error."""
  try:
    r = requests.post(GRAPHQL_URL, json={"query": query, "variables": variables},
                      headers=headers)
    r.raise_for_status()
    payload = r.json()
    if payload.get("errors"):
      print(f"⚠️  GraphQL errors: {payload['errors']}")
    return payload.get("data")
  except (requests.RequestException, ValueError) as e:
    print(f"⚠️  GraphQL request failed: {e}")
    return None


def _dig(obj, *keys):
  """Walk nested dict keys, tolerating a None (GraphQL null) at any level."""
  for key in keys:
    obj = (obj or {}).get(key)
  return obj


def get_starred_list_repos(user, slug, headers):
  """Return the set of repo full_names in a user's public GitHub Stars list.

  Stars lists are exposed only via GraphQL (no REST endpoint) and require
  authentication, so this is skipped with a warning when no token is set.
  There is no `user.list(slug:)` field, so we resolve the list's node id via
  `user.lists`, then page its items through `node(id:)`.
  """
  if not headers.get("Authorization"):
    print(f"⚠️  no token; skipping starred list {user}/{slug}")
    return set()

  data = _graphql("query($l:String!){user(login:$l){lists(first:50){nodes{id slug}}}}",
                  {"l": user}, headers)
  nodes = _dig(data, "user", "lists", "nodes") or []
  list_id = next((n["id"] for n in nodes if n.get("slug") == slug), None)
  if not list_id:
    print(f"⚠️  starred list {user}/{slug} not found")
    return set()

  items_query = """query($id:ID!,$after:String){
    node(id:$id){... on UserList{items(first:100, after:$after){
      pageInfo{hasNextPage endCursor}
      nodes{... on Repository{nameWithOwner}}}}}}"""
  names, after = set(), None
  while True:
    data = _graphql(items_query, {"id": list_id, "after": after}, headers)
    conn = _dig(data, "node", "items") or {}
    for n in conn.get("nodes") or []:
      if n.get("nameWithOwner"):
        names.add(n["nameWithOwner"])
    page = conn.get("pageInfo") or {}
    if not page.get("hasNextPage"):
      break
    after = page.get("endCursor")
  return names


def get_contributors(full_name, headers):
  """Return the set of (lowercased) contributor logins of a repository."""
  data = github_request_cached(f"{BASE_URL}/repos/{full_name}/contributors?per_page=100", headers=headers)
  return {u["login"].lower() for u in (data or []) if u.get("login")}


_README_NON_REPO = {"orgs", "stars", "sponsors", "topics", "search", "about",
                    "features", "marketplace", "settings", "apps", "collections"}
_README_PATH_KW = {"tree", "blob", "releases", "wiki", "issues", "pull", "raw",
                   "actions", "commits", "graphs"}


def readme_repo_names(path=README_PATH):
  """Extract distinct owner/repo names from the GitHub links in the curated README."""
  try:
    with open(path, "r", encoding="utf-8") as f:
      text = f.read()
  except OSError:
    print(f"⚠️  {path} not found; skipping readme source")
    return []
  names = {}
  for owner, repo in re.findall(r"github\.com/([\w.-]+)/([\w.-]+)", text):
    if owner.lower() in _README_NON_REPO:
      continue
    repo = repo.rstrip(".")
    if repo.endswith(".git"):
      repo = repo[:-4]
    if not repo or repo.lower() in _README_PATH_KW:
      continue
    names[f"{owner}/{repo}".lower()] = f"{owner}/{repo}"  # dedupe case-insensitively
  return list(names.values())


def search_topic_repo_names(topic, headers):
  """Return the full_names of repositories tagged with a GitHub topic."""
  print(f"🔍 Searching topic '{topic}'...")
  url = f"{BASE_URL}/search/repositories"
  params = {"q": f"topic:{topic}", "sort": "stars", "order": "desc"}
  return [item["full_name"] for item in paginate(url, headers, params=params, cap=MAX_PAGES, throttle=2)]


# --- Signals -----------------------------------------------------------------

def days_since_push(pushed_at):
  """Whole days between a GitHub timestamp and now (UTC), or None."""
  if not pushed_at:
    return None
  try:
    dt = datetime.strptime(pushed_at, "%Y-%m-%dT%H:%M:%SZ")
    return (datetime.utcnow() - dt).days
  except ValueError:
    return None


# --- Ingestion ---------------------------------------------------------------

def _b(value):
  """Render a bool as a spreadsheet-friendly lowercase string."""
  return "true" if value else "false"


def build_repo_record(obj, source, matched_topics, starred_by, contributors):
  """Build one flat CSV record from a full GitHub repository object.

  Reads every field from `obj` (the /repos response) so topic-sourced and
  manual repos share the exact same shape — including `pushed_at`, which the
  previous code only stored for manual repos.
  """
  repo_topics = set(obj.get("topics") or [])
  all_topics = repo_topics | set(matched_topics)

  pushed_at = obj.get("pushed_at")
  dsp = days_since_push(pushed_at)
  archived = bool(obj.get("archived"))
  dormant = archived or (dsp is not None and dsp >= DORMANT_DAYS)

  is_fork = bool(obj.get("fork"))
  parent = obj.get("parent") or {}
  parent_full_name = parent.get("full_name", "") if is_fork else ""

  license_name = (obj.get("license") or {}).get("name") or "N/A"

  owner = obj.get("full_name", "").split("/", 1)[0].lower()

  return {
    "full_name": obj.get("full_name", ""),
    "html_url": obj.get("html_url", ""),
    "description": obj.get("description") or "",
    "language": obj.get("language") or "",
    "license": license_name,
    "stars": obj.get("stargazers_count", 0),
    "forks": obj.get("forks_count", 0),
    "open_issues": obj.get("open_issues_count", 0),
    "topics": "|".join(sorted(all_topics)),
    "topic_matches": len(all_topics & TOPICS),
    "pushed_at": pushed_at or "",
    "days_since_push": dsp if dsp is not None else "",
    "dormant": _b(dormant),
    "archived": _b(archived),
    "created_at": obj.get("created_at") or "",
    "is_fork": _b(is_fork),
    "parent_full_name": parent_full_name,
    "starred_by": "|".join(sorted(starred_by)),
    "promoted": len(starred_by),
    "by_contributor": _b(owner in contributors),
    "source": source,
  }


def collect_candidates(headers):
  """Discover candidate repos and their provenance/matched topics.

  Keyed case-insensitively so the same repo surfaced by several sources (topic
  search, manual list, curated README) is fetched once. Returns
  {lower_full_name: {"full_name": str, "sources": set, "matched_topics": set}}.
  """
  excluded = {r.lower() for r in EXCLUDED_REPOS}
  candidates = {}

  def add(full_name, source, topic=None):
    key = full_name.lower()
    if key in excluded:
      return
    meta = candidates.setdefault(key, {"full_name": full_name, "sources": set(), "matched_topics": set()})
    meta["sources"].add(source)
    if topic:
      meta["matched_topics"].add(topic)

  for topic in sorted(TOPICS):
    for full_name in search_topic_repo_names(topic, headers):
      add(full_name, "topic", topic)

  for full_name in ADDITIONAL_REPOS:
    add(full_name, "manual")

  for full_name in readme_repo_names():
    add(full_name, "readme")

  for user, slug in sorted(STARRED_LISTS):
    for full_name in get_starred_list_repos(user, slug, headers):
      add(full_name, "starred-list")

  return candidates


def ingest(args):
  headers = auth_headers(args.token)

  user_starred = {}
  for user in sorted(STARRED_USERS):
    print(f"⭐ Fetching starred repos for {user}...")
    user_starred[user] = get_starred_repos_for_user(user, headers)

  contributors = get_contributors(SELF_REPO, headers)
  print(f"👥 {len(contributors)} contributors of {SELF_REPO}")

  candidates = collect_candidates(headers)
  print(f"\n📥 Building records for {len(candidates)} candidate repositories...")

  excluded = {r.lower() for r in EXCLUDED_REPOS}
  records = []
  seen = set()
  for meta in candidates.values():
    obj = get_repo_data(meta["full_name"], headers)
    if not obj:
      continue
    canonical = obj["full_name"]  # follows renames/redirects
    if canonical.lower() in excluded or canonical.lower() in seen:
      continue
    seen.add(canonical.lower())
    starred_by = {u for u, starred in user_starred.items() if canonical in starred}
    source = "+".join(sorted(meta["sources"]))
    records.append(build_repo_record(obj, source, meta["matched_topics"], starred_by, contributors))

  records.sort(key=lambda r: (-int(r["promoted"]), -int(r["topic_matches"]), -int(r["stars"])))

  with open(args.out, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
    writer.writeheader()
    writer.writerows(records)

  dormant = sum(1 for r in records if r["dormant"] == "true")
  promoted = sum(1 for r in records if int(r["promoted"]) > 0)
  print(f"\n✅ Wrote {len(records)} repositories to {args.out}")
  print(f"   dormant: {dormant} — promoted: {promoted}")


# --- Enrichment (classification via Claude skill agent) ----------------------

# Rendered once; the taxonomy is fixed for a run. The classifier's task and
# output format live in .claude/agents/repo-classifier.md, so the per-repo
# message below carries only the data (taxonomy + topics + README).
CATEGORY_TREE_TEXT = "\n".join(
  f"- {main}: {', '.join(subs)}" if subs else f"- {main}"
  for main, subs in CATEGORY_TREE.items()
)


def build_classifier_prompt(row, readme):
  """Per-repo data handed to the classifier skill agent."""
  topics = row.get("topics", "")
  topic_hint = f"\nGitHub topics: {topics.replace('|', ', ')}" if topics else ""
  return (
    f"Taxonomy:\n{CATEGORY_TREE_TEXT}\n"
    f"{topic_hint}\n"
    f"Repository description: {row.get('description') or '(none)'}\n\n"
    f"README:\n{(readme or '')[:4000]}"
  )


def extract_versions(text, keyword, known):
  """Find supported protocol versions mentioned near `keyword` in a README."""
  found = set()
  pattern = rf"{keyword}[\s\-_/:]*[js]?[\s\-_/:]*v?\.?\s*(\d+\.\d+(?:\.\d+)?)"
  for m in re.finditer(pattern, text or "", re.I):
    if m.group(1) in known:
      found.add(m.group(1))
  return ",".join(sorted(found, key=lambda v: [int(x) for x in v.split(".")]))


def parse_classification(text):
  """Split classifier output into (description, [(main, sub), ...])."""
  description = ""
  cat_lines = []
  for line in (text or "").splitlines():
    if not description and line.strip().lower().startswith("description:"):
      description = line.split(":", 1)[1].strip()
    else:
      cat_lines.append(line)
  return description, parse_categories("\n".join(cat_lines))


def parse_categories(text):
  """Parse category lines into (main, sub) tuples.

  Tolerant of backend formatting: the leading `- ` bullet is optional (codex
  sometimes drops it), the `Categories:` header is skipped, and a bare line is
  only taken as a main-only category when it is a known taxonomy key — so prose
  lines are ignored rather than mistaken for categories.
  """
  parsed = []
  for line in (text or "").splitlines():
    line = line.strip()
    if not line or line.lower().rstrip(":") == "categories":
      continue
    bulleted = line.startswith("- ")
    if bulleted:
      line = line[2:].strip()
    if ">" in line:
      main, sub = map(str.strip, line.split(">", 1))
      parsed.append((main, sub))
    elif bulleted and line:
      parsed.append((line, None))
    elif line in CATEGORY_TREE:
      parsed.append((line, None))
  return parsed


def classify_with_claude(row, readme):
  """Classify a repo by invoking the `repo-classifier` skill agent headless.

  Returns (description, [(main, sub), ...]).
  """
  if not readme:
    return "", []
  prompt = build_classifier_prompt(row, readme)
  cmd = [
    "claude", "-p",
    "--agent", CLASSIFIER_AGENT,
    "--model", CLASSIFIER_MODEL,
    "--strict-mcp-config",
    "--output-format", "text",
  ]
  try:
    result = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=180)
    if result.returncode != 0:
      print(f"⚠️  classifier failed for {row['full_name']}: {result.stderr.strip()[:200]}")
      return "", []
    return parse_classification(result.stdout)
  except Exception as e:
    print(f"⚠️  classifier error for {row['full_name']}: {e}")
    return "", []


def classify_with_codex(row, readme):
  """Classify a repo via `codex exec` non-interactively. Returns (description, cats)."""
  if not readme:
    return "", []
  prompt = f"{CLASSIFIER_INSTRUCTIONS}\n\n{build_classifier_prompt(row, readme)}"
  out_fd, out_path = tempfile.mkstemp(suffix=".txt")
  os.close(out_fd)
  cmd = [
    "codex", "exec",
    "--sandbox", "read-only",
    "--ephemeral",
    "--color", "never",
    "--skip-git-repo-check",
    "-o", out_path,
    "-",  # read the prompt from stdin
  ]
  try:
    result = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
      print(f"⚠️  classifier failed for {row['full_name']}: {result.stderr.strip()[:200]}")
      return "", []
    with open(out_path, "r", encoding="utf-8") as f:
      return parse_classification(f.read())
  except Exception as e:
    print(f"⚠️  classifier error for {row['full_name']}: {e}")
    return "", []
  finally:
    if os.path.exists(out_path):
      os.remove(out_path)


def classify_with_copilot(row, readme):
  """Classify a repo via `copilot -p` non-interactively. Returns (description, cats).

  Uses the GitHub Copilot CLI, which is natively authenticated inside a GitHub
  Copilot coding-agent environment (no extra API secret). Runs in an empty temp
  cwd so the agent's tools have no repo files in reach; the prompt is
  self-contained and instructs the model not to use any tools.
  """
  if not readme:
    return "", []
  prompt = f"{CLASSIFIER_INSTRUCTIONS}\n\n{build_classifier_prompt(row, readme)}"
  cmd = [
    "copilot", "-p", prompt,
    "--allow-all-tools",   # required to run non-interactively
    "--no-ask-user",       # never block waiting for interactive input
    "--silent",            # print only the agent's answer on stdout
    "--no-color",
    "--log-level", "none",
  ]
  if CLASSIFIER_COPILOT_MODEL:
    cmd += ["--model", CLASSIFIER_COPILOT_MODEL]
  workdir = tempfile.mkdtemp()
  try:
    result = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
      print(f"⚠️  classifier failed for {row['full_name']}: {result.stderr.strip()[:200]}")
      return "", []
    return parse_classification(result.stdout)
  except Exception as e:
    print(f"⚠️  classifier error for {row['full_name']}: {e}")
    return "", []
  finally:
    shutil.rmtree(workdir, ignore_errors=True)


CLASSIFIERS = {
  "claude": classify_with_claude,
  "codex": classify_with_codex,
  "copilot": classify_with_copilot,
}


CLASSIFICATION_FIELDS = ["full_name", "pushed_at", "categories", "description"]


def load_classifications(path):
  """Load the committed LLM cache as {full_name: {pushed_at, categories, description}}."""
  if not os.path.exists(path):
    return {}
  with open(path, "r", encoding="utf-8", newline="") as f:
    return {r["full_name"]: r for r in csv.DictReader(f)}


def save_classifications(path, cache):
  """Persist the LLM cache, sorted by full_name for stable, minimal git diffs."""
  with open(path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=CLASSIFICATION_FIELDS)
    writer.writeheader()
    for full_name in sorted(cache, key=str.lower):
      writer.writerow({k: cache[full_name].get(k, "") for k in CLASSIFICATION_FIELDS})


def enrich(args):
  headers = auth_headers(args.token)

  with open(args.infile, "r", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))

  if args.skip_forks:
    rows = [r for r in rows if r.get("is_fork") != "true"]
  if args.skip_dormant:
    rows = [r for r in rows if r.get("dormant") != "true"]
  if args.limit:
    rows = rows[:args.limit]

  # Durable committed cache: reuse a repo's classification (categories +
  # synthesized description) while its pushed_at is unchanged. Merge-write it so
  # entries for repos not in this run (e.g. under --limit) are preserved.
  # `--refresh` re-runs the model for every repo.
  cache = load_classifications(args.cache)
  reuse = {} if args.refresh else cache

  classify = CLASSIFIERS[args.classifier]
  print(f"🏷️  Classifying {len(rows)} repositories via the '{args.classifier}' backend...")

  # Stream each row to disk as it is finalized (with a flush) so a long batch is
  # crash-safe and resumable: a re-run reuses everything already in the cache.
  reused = classified = 0
  with open(args.out, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=CSV_FIELDS + ["categories", "ocpp_versions", "ocpi_versions"])
    writer.writeheader()
    for i, row in enumerate(rows, 1):
      # README is fetched for every repo (cached, so cheap) to extract supported
      # protocol versions; only the model call is skipped on a cache hit.
      readme = fetch_readme_content(row["full_name"], headers)
      row["ocpp_versions"] = extract_versions(readme, "ocpp", OCPP_VERSIONS)
      row["ocpi_versions"] = extract_versions(readme, "ocpi", OCPI_VERSIONS)
      prev = reuse.get(row["full_name"])
      if prev and prev.get("pushed_at") == row["pushed_at"]:
        row["categories"] = prev.get("categories", "")
        description = prev.get("description", "")
        reused += 1
        tag = "♻️  reused"
      else:
        description, cats = classify(row, readme)
        row["categories"] = "|".join(f"{m} > {s}" if s else m for m, s in cats)
        classified += 1
        tag = "🏷️  classified"
      row["description"] = description or row.get("description", "")  # synthesized wins
      cache[row["full_name"]] = {
        "full_name": row["full_name"], "pushed_at": row["pushed_at"],
        "categories": row["categories"], "description": row["description"],
      }
      writer.writerow(row)
      f.flush()
      print(f"  [{i}/{len(rows)}] {tag}: {row['full_name']} -> {row['categories'] or '(none)'}")

  save_classifications(args.cache, cache)
  print(f"\n✅ Wrote {len(rows)} enriched repositories to {args.out}")
  print(f"   classified: {classified} — reused: {reused} — cache: {args.cache} ({len(cache)} entries)")


# --- Rendering ---------------------------------------------------------------

# The curated view is driven by the two personal star lists. `juherr` is the
# anchor; a repo's promotion score decides both its section and its rank:
#    2  starred by juherr AND mateogreil            -> top of the selection
#    1  starred by juherr only, OR owned by a
#       contributor of this repo                    -> selection
#    0  starred by mateogreil only                  -> bottom of the selection
#   -1  in neither list (topic discovery)           -> collapsed "To refine"
ANCHOR_USER = "juherr"
SECOND_USER = "mateogreil"


def _promotion(row):
  """Promotion score: both=2, juherr-or-contributor=1, mateogreil only=0, neither=-1."""
  starred = set(filter(None, row.get("starred_by", "").split("|")))
  if ANCHOR_USER in starred:
    base = 2 if SECOND_USER in starred else 1
  elif SECOND_USER in starred:
    base = 0
  else:
    base = -1
  if row.get("by_contributor") == "true":
    base = max(base, 1)  # a contributor's own project is worth at least 1
  return base


def _stars(row):
  return int(row.get("stars") or 0)


def _canon_sub(sub):
  """Fold a free-form subcategory onto its canonical label (case-insensitive)."""
  if not sub:
    return sub
  return SUBCATEGORY_ALIASES.get(sub.lower(), sub)


def _row_categories(row):
  """Parse the pipe-joined `categories` column into [(main, sub), ...].

  A CATEGORY_OVERRIDES entry (keyed by full_name) replaces the classifier's value.
  """
  raw = CATEGORY_OVERRIDES.get((row.get("full_name") or "").lower())
  if raw is None:
    raw = row.get("categories") or ""
  out = []
  for chunk in raw.split("|"):
    chunk = chunk.strip()
    if not chunk:
      continue
    if ">" in chunk:
      main, sub = map(str.strip, chunk.split(">", 1))
      out.append((main, _canon_sub(sub) or None))
    else:
      out.append((chunk, None))
  # Dedup (aliasing can collapse two distinct subs onto the same canonical label,
  # e.g. "Route planner" + "Charging station map" -> one bucket) while preserving order.
  seen = set()
  out = [p for p in out if not (p in seen or seen.add(p))]
  return out or [("Uncategorized", None)]


_MAIN_INDEX = {main: i for i, main in enumerate(CATEGORY_TREE)}


def _main_key(main):
  # Known categories keep their taxonomy order; unknowns then "Uncategorized" last.
  return (_MAIN_INDEX.get(main, len(CATEGORY_TREE) + (1 if main == "Uncategorized" else 0)), main)


def _sub_key(main, sub):
  subs = CATEGORY_TREE.get(main, [])
  if sub is None:
    return (-1, "")  # main-only entries first
  return (subs.index(sub) if sub in subs else len(subs), sub)


def _sort_key(row):
  """Rank within a subsection: promotion score first, then stars."""
  return (-_promotion(row), -_stars(row))


_DEPRECATED_RE = re.compile(
  r"\b(deprecated|discontinued|unmaintained|abandoned|superseded|no longer maintained)\b", re.I)


def _is_deprecated(row):
  """A project the synthesized description flags as deprecated/unmaintained."""
  return bool(_DEPRECATED_RE.search(row.get("description", "")))


def _inactive(row):
  """Belongs in the Dormant section: stale/archived (dormant) or deprecated."""
  return row.get("dormant") == "true" or _is_deprecated(row)


def _render_line(row, main=None, show_language=True):
  parts = [f"- **[{row['full_name']}]({row['html_url']})**", f"— ⭐ {row['stars']}"]
  versions = {"OCPP": row.get("ocpp_versions"), "OCPI": row.get("ocpi_versions")}.get(main)
  if versions:
    parts.append(f"— {main} {versions.replace(',', ', ')}")
  if _is_deprecated(row):
    parts.append("— 🚫 deprecated")
  if row.get("dormant") == "true":  # dormant anywhere shows the last-update date
    parts.append(f"— 💤 {row.get('pushed_at', '')[:10]}")
  if row.get("description"):
    parts.append(f"— {row['description']}")
  if show_language and row.get("language"):
    parts.append(f"_({row['language']})_")
  return " ".join(parts)


def _render_grouped(rows, lines):
  """Emit `### main` / `#### sub` subsections; a repo appears under each of its categories.

  Under a `Libraries` subcategory the technology becomes an extra `##### language`
  level (and is dropped from the line).
  """
  groups = defaultdict(lambda: defaultdict(list))
  for row in rows:
    for main, sub in _row_categories(row):
      groups[main][sub].append(row)
  for main in sorted(groups, key=_main_key):
    lines += [f"### {main}", ""]
    subs = groups[main]
    for sub in sorted(subs, key=lambda s: _sub_key(main, s)):
      if sub:
        lines += [f"#### {sub}", ""]
      if sub == "Libraries":
        by_lang = defaultdict(list)
        for row in subs[sub]:
          by_lang[row.get("language") or "Other"].append(row)
        for lang in sorted(by_lang, key=lambda l: (l == "Other", l.lower())):
          lines += [f"##### {lang}", ""]
          for row in sorted(by_lang[lang], key=_sort_key):
            lines.append(_render_line(row, main=main, show_language=False))
          lines.append("")
      else:
        for row in sorted(subs[sub], key=_sort_key):
          lines.append(_render_line(row, main=main))
        lines.append("")


def _inject_between_markers(path, body, begin_marker, end_marker):
  """Replace the text between `begin_marker` and `end_marker` in `path` with `body`."""
  with open(path, "r", encoding="utf-8") as f:
    content = f.read()
  begin = content.find(begin_marker)
  end = content.find(end_marker)
  if begin == -1 or end == -1 or end < begin:
    raise SystemExit(
      f"Injection markers not found (or out of order) in {path}: "
      f"expected {begin_marker!r} … {end_marker!r}")
  updated = (content[:begin + len(begin_marker)]
             + "\n" + body + "\n"
             + content[end:])
  with open(path, "w", encoding="utf-8") as f:
    f.write(updated)


_SLUG_STRIP = re.compile(r"[^\w\s-]")


def _slugify(text, seen):
  """GitHub-style heading anchor, deduplicated in document order via `seen`."""
  slug = _SLUG_STRIP.sub("", text.strip().lower()).replace(" ", "-")
  n = seen.get(slug, 0)
  seen[slug] = n + 1
  return slug if n == 0 else f"{slug}-{n}"


def _headings_before(path, marker):
  """ATX heading texts appearing before `marker` in `path`, in document order.

  Used to seed the slugger so anchors into the generated block account for the
  hand-authored headings (Contents, Specifications) that precede it.
  """
  try:
    with open(path, "r", encoding="utf-8") as f:
      content = f.read()
  except FileNotFoundError:
    return []
  head = content.split(marker, 1)[0]
  return re.findall(r"^#{1,6}\s+(.*?)\s*$", head, re.M)


def _build_toc(selection_lines, readme_path):
  """Generate the Contents sub-tree (level-1 protocols, level-2 subcategories)
  for the Selection block, with anchors matching GitHub's slugger."""
  seen = {}
  for heading in _headings_before(readme_path, README_MARKER_BEGIN):
    _slugify(heading, seen)  # seed with the headings that precede the block
  # `## Tools and Resources` is among the seeded headings, so link it directly
  # rather than re-slugging it (which would return a deduped `-1` anchor).
  toc = ["- [Tools and Resources](#tools-and-resources)"]
  for line in selection_lines:
    if line.startswith("### "):
      title = line[4:].strip()
      toc.append(f"  - [{title}](#{_slugify(title, seen)})")
    elif line.startswith("#### "):
      title = line[5:].strip()
      toc.append(f"    - [{title}](#{_slugify(title, seen)})")
    elif line.startswith("##### "):
      _slugify(line[6:].strip(), seen)  # consume to keep dedup aligned (not linked)
  return "\n".join(toc)


def render(args):
  with open(args.infile, "r", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))

  # Honor EXCLUDED_REPOS here too (not just at ingest), so the published list
  # never shows an excluded repo even from a stale enriched CSV.
  excluded = {r.lower() for r in EXCLUDED_REPOS}
  rows = [r for r in rows if r["full_name"].lower() not in excluded]

  in_list = [r for r in rows if _promotion(r) >= 0]
  selection = [r for r in in_list if not _inactive(r)]
  dormant = [r for r in in_list if _inactive(r)]
  refine = [r for r in rows if _promotion(r) < 0]

  # No H1/`## Selection` wrapper: the body slots straight under an existing
  # heading (e.g. README's `## Tools and Resources`), so the top level is the
  # per-protocol `### main` emitted by _render_grouped. The Selection block is
  # built on its own first so its headings can seed the generated Contents TOC.
  sel_lines = []
  _render_grouped(selection, sel_lines)

  lines = list(sel_lines)

  def collapsed(title, group):
    lines.extend(["<details>", f"<summary>{title}</summary>", ""])
    _render_grouped(group, lines)
    lines.extend(["</details>", ""])

  collapsed(f"Dormant ({len(dormant)})", dormant)
  collapsed(f"To refine ({len(refine)} projects)", refine)

  body = "\n".join(lines).strip() + "\n"

  with open(args.out, "w", encoding="utf-8") as f:
    f.write(body)
  if getattr(args, "readme", None):
    _inject_between_markers(args.readme, body, README_MARKER_BEGIN, README_MARKER_END)
    _inject_between_markers(args.readme, _build_toc(sel_lines, args.readme),
                            README_TOC_BEGIN, README_TOC_END)

  promoted = sum(1 for r in selection if _promotion(r) == 2)
  print(f"✅ Wrote {args.out}" + (f" + injected into {args.readme}" if getattr(args, "readme", None) else ""))
  print(f"   selection: {len(selection)} (promoted {promoted}) — dormant: {len(dormant)} — to refine: {len(refine)}")


# --- CLI ---------------------------------------------------------------------

def main():
  parser = argparse.ArgumentParser(description="EV-charging repository discovery pipeline.")
  sub = parser.add_subparsers(dest="stage", required=True)

  p_ingest = sub.add_parser("ingest", help="Fetch candidate repos + signals into a CSV.")
  p_ingest.add_argument("--token", help="GitHub personal access token (optional).")
  p_ingest.add_argument("--out", default="repos.csv", help="Output CSV path.")
  p_ingest.set_defaults(func=ingest)

  p_enrich = sub.add_parser("enrich", help="Classify repos from a CSV via the skill agent.")
  p_enrich.add_argument("--in", dest="infile", default="repos.csv", help="Input CSV path.")
  p_enrich.add_argument("--out", default="repos.enriched.csv", help="Output CSV path.")
  p_enrich.add_argument("--cache", default=CLASSIFICATIONS_PATH,
                        help="Durable LLM cache path (committed).")
  p_enrich.add_argument("--token", help="GitHub personal access token (optional).")
  p_enrich.add_argument("--limit", type=int, help="Only classify the first N rows.")
  p_enrich.add_argument("--classifier", choices=sorted(CLASSIFIERS), default="claude",
                        help="Classification backend (default: claude).")
  p_enrich.add_argument("--skip-forks", action="store_true", help="Skip forked repos.")
  p_enrich.add_argument("--skip-dormant", action="store_true", help="Skip dormant repos.")
  p_enrich.add_argument("--refresh", action="store_true",
                        help="Re-classify everything, ignoring the previous enriched CSV.")
  p_enrich.set_defaults(func=enrich)

  p_render = sub.add_parser("render", help="Render a curated Markdown view from the enriched CSV.")
  p_render.add_argument("--in", dest="infile", default="repos.enriched.csv", help="Input CSV path.")
  p_render.add_argument("--out", default="awesome-ev-charging-projects.md", help="Output Markdown path.")
  p_render.add_argument("--readme", help="Also inject the rendered body between the "
                        "markers in this file (e.g. README.md).")
  p_render.set_defaults(func=render)

  args = parser.parse_args()
  args.func(args)


if __name__ == "__main__":
  main()
