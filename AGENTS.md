# AGENTS.md

Guidance for any coding agent working in this repository. **This file is the
shared source of truth** — everything an agent needs to work here is below,
regardless of which harness it runs in.

Harness-specific files complement it and must not restate it:

| File | Scope |
| --- | --- |
| `AGENTS.md` | Everything shared. Start here |
| `CLAUDE.md` | Claude Code specifics only — it imports this file |

Keep new project knowledge in this file. If a fact holds for every agent, it
belongs here even when you discovered it in one harness.

## What this repository is

A curated "awesome list" of EV charging protocol tools (OCPP, OCPI, ISO 15118, OICP, eMI³, OIOI, Eichrecht). Two distinct deliverables live here:

1. **`README.md`** — the published awesome list. Its prose (intro, Contents, `## Specifications`, `## Contributing`, `## Other Resources`) is hand-authored. The **project listing** inside `## Tools and Resources` — everything between the `<!-- BEGIN GENERATED PROJECTS -->` / `<!-- END GENERATED PROJECTS -->` markers — is **generated** by `python pipeline.py render --readme README.md` and injected in place. Do **not** hand-edit between those markers; edits are overwritten on the next render. To change what appears there, adjust the pipeline inputs (see Conventions) and re-render.
2. **`pipeline.py`** — a discovery pipeline that scrapes GitHub for candidate repositories, scores them with quality signals, AI-classifies them, and renders the curated project listing that populates the README's `## Tools and Resources` block.
3. **`csms.md` + `csms.py`** — a separate product-level catalogue of Charging Station Management Systems (see "csms.py" below). Independent of `pipeline.py`, which it only imports.

The repo also vendors protocol specifications as static assets under `ocpp/`, `ocpi/`, `oicp/`, `emi3/`, `eichrecht/` (PDFs, WSDLs, OCPP JSON schemas) — these are reference material linked from `README.md`.

## Commands

The project is managed with **mise** (`mise.toml`): it pins Python 3.11.16 and
auto-creates/activates a `.venv` — no manual `source .venv/bin/activate`. Run
`mise trust` once after cloning.

```bash
mise install          # install the pinned Python
mise run install      # (alias: mise run i) runtime deps into .venv
mise run install-dev  # runtime + pytest; `install` alone keeps the CI data job lean
#   A fresh .venv has no pytest — run this before `mise run test`, or the suite
#   fails with "No module named pytest" and it looks like a broken environment.
mise run test         # (alias: mise run t) pytest

mise run ingest       # Stage 1 -> repos.csv   (wires --token via `gh auth token`)
mise run enrich       # Stage 2 -> repos.enriched.csv

# Or call the script directly (mise auto-activates .venv for commands run in-dir):
python pipeline.py ingest --token <GITHUB_PAT> --out repos.csv
python pipeline.py enrich --in repos.csv --out repos.enriched.csv --token <GITHUB_PAT>
#   enrich flags: --limit N / --skip-forks / --skip-dormant / --refresh
#   / --restamp [--reask-category 'Main > Sub' ...] (after a prompt edit)

python pipeline.py render --readme README.md   # Stage 3 -> injects the curated
#   Selection between the markers in README.md and writes the secondary
#   legacy-projects.md (dormant + to-refine). Omit --readme to only write the latter.
#   Add --export-dir data to also write data/projects.json + its manifest entry.

git show HEAD:classifications.csv | python pipeline.py check-classifications --base -
#   CI guard, see "Guarding the classification cache" below. Optional:
#   --report report.md [--base-projects base.json [--projects data/projects.json]]
```

`--token` is optional; without it GitHub's unauthenticated rate limits apply.
`gh auth token` supplies one when the gh CLI is authenticated.

`mise run test` (alias `t`) runs the pytest suite in `tests/`.
`tests/test_csms.py` covers `csms.py`: the controlled feature vocabulary,
certificate derivation, product/company identity, merge precedence, table rendering, the curated-CSV
validations and render determinism. It needs no network — the one GitHub call
`merge` can make is monkeypatched — and it also validates the committed CSVs, so
a bad curated row fails there as well as at render time. `tests/test_pipeline.py`
covers `pipeline.py`'s classification layer — the CI guard, the "is there
anything to classify" rule, the backends' failure contract and what `enrich`
writes to the durable cache — with the backend and the README fetch stubbed, so
it needs no network and spawns no LLM CLI. Apart from that and the JSON
export below, `pipeline.py` is untested; its pure functions can be exercised by importing `pipeline` and
calling `build_repo_record` / `days_since_push` / `parse_categories` directly.
`tests/test_oscp_schemas.py` pins the vendored CC BY-ND files under
`oscp/OSCP-2.0/` with a SHA-256 manifest and proves each defect listed in
its README, and that the local patches suffice, with `jsonschema` in memory.
The public JSON export is covered by three test files: `tests/test_public_export.py`
(`projects.json` from fixture renders), `tests/test_csms_export.py`
(`csms.json`, plus the committed `data/csms.json` and its manifest entry
against a fresh export of the committed CSVs) and `tests/test_public_data.py`
(both payloads against `data/schema/*.json` with `jsonschema`, from
`requirements-dev.txt`, the export agreeing with the Markdown tiers, and a
committed `data/projects.json` matching its `projects` manifest entry — skipped
until #98 commits it, and exercised on a fixture render meanwhile).
`tests/test_markdown_links.py` checks that every relative link, and every
`https://github.com/juherr/awesome-ev-charging/(tree|blob)/main/…` link, in
every tracked Markdown file resolves to a path `git ls-files` lists — a
tracked file, or a directory holding one — compared case-sensitively as on the
Linux runner, so a link that only works on macOS fails. It reads Markdown links
and images, reference definitions, `href` / `src` in inline HTML and
`<https://…>` autolinks. Anchors are not checked, and links in code or in HTML
comments are skipped. The three verbatim OCA `ReadMe.md`
files are checked too, though markdownlint below skips them: a link that only
an edit of their bytes could fix goes in `VENDORED_LINK_EXCEPTIONS` as an exact
`(file, target)` pair (empty today), never by skipping the file.

Markdown is linted by `npx markdownlint-cli2` (config in
`.markdownlint-cli2.jsonc`): every tracked `*.md`, dot-directories and the
first-party files under the vendored directories included. Only the three
verbatim OCA files `ocpp/OCPP-2.0/ReadMe.md`, `ocpp/OCPP-2.0.1/ReadMe.md` and
`ocpp/OCPP-2.1/ReadMe.md` are exempt, by exact path: they are upstream bytes,
never reformatted. The exemption covers style only: they stay in the
provenance and licence inventory of `docs/third-party-assets.md`, and byte
pinning of vendored directories is tracked in
[#97](https://github.com/juherr/awesome-ev-charging/issues/97). The
live classifier prompt `.claude/agents/repo-classifier.md` keeps its bytes too,
with three rules relaxed for it alone. `README.md` is additionally checked by
`npx awesome-lint`.

## pipeline.py architecture

A two-stage pipeline connected by a **CSV boundary** — ingestion (deterministic, GitHub-only) is deliberately separated from enrichment (the slow/flaky LLM step), so the CSV can be reviewed/curated in a spreadsheet and enrichment can be re-run without re-fetching.

**Stage 1 — `ingest` → `repos.csv`** (`ingest`, `collect_candidates`, `build_repo_record`):
`collect_candidates` merges four **discovery** sources by `full_name` — topic search (`search_topic_repo_names` across `TOPICS`), manual additions (`ADDITIONAL_REPOS`), GitHub links in the curated README (`readme_repo_names`), and curated GitHub Stars lists (`get_starred_list_repos` for each `(owner, slug)` in `STARRED_LISTS`, e.g. `juherr/ev`, `mateogreil/ev-mobility`). Stars lists are GraphQL-only and require a token, so ingest skips them (with a warning) when unauthenticated. `readme_repo_names` only reads `github.com` links. Separately, the **full** star sets of `STARRED_USERS` (`get_starred_repos_for_user`) are read only as a **promotion signal** (`starred_by`), not as a discovery source. `build_repo_record` is the single record builder for **all** sources — it reads every field from the full `/repos` object, so `pushed_at` (hence the `dormant`/`days_since_push` signals) is present for every repo, not just manual ones. Signals in the CSV: `dormant` (no push ≥ `DORMANT_DAYS` OR archived), `stars`, `forks`, `open_issues`, `topic_matches`, `promoted`, `archived`, `is_fork`, `updated_at` (the last known modification, metadata edits included; recorded, never used for dormancy, which reads `pushed_at`), plus `source` (the `+`-joined provenance, e.g. `readme+starred-list+topic`).

**Codeberg.** A repository that lives on Codeberg alone goes in `CODEBERG_REPOS`. `ingest` reads it from Codeberg's Forgejo API (`codeberg_record`, `source=codeberg`), and `forgejo_repo_as_github` maps the response onto the fields `build_repo_record` reads. Forgejo has no `pushed_at`, and its repository `updated_at` is not one: it also moves on a description or topic edit, so it is the last known modification, not the last commit. `codeberg_record` therefore reads the default branch (`/branches/{default_branch}`, `codeberg_last_commit`) and takes `pushed_at` from its `commit.timestamp`; `updated_at` lands in its own column. Both are converted to the UTC `…Z` form that `days_since_push` parses, and only `pushed_at` decides dormancy. The branch read follows the repository read's contract: an empty repository or a 404 leaves `pushed_at` empty (no `days_since_push`, and not dormant unless archived), any other failure aborts `ingest` before it writes the CSV. The licence reads `N/A`. `enrich` reads the README there too: `fetch_readme_content` dispatches on the row's `html_url`, and `fetch_codeberg_readme` lists the root (Forgejo has no README endpoint) and reads the first `README*` file. The contract is the same as GitHub's: `""` absent, `None` unreadable. Codeberg requests always go out with empty headers, so the GitHub token never leaves for another host. No Stars list can hold a Codeberg repo, so `_promotion` scores a `codeberg` source at least 1: listing it is the curation. A GitHub `ADDITIONAL_REPOS` entry still needs a star. `starred_by` stays empty, because nobody starred it. A name in `CODEBERG_REPOS` wins over a GitHub repo of the same name: `collect_candidates` and `ingest` drop the GitHub candidate, which is the mirror a project leaves behind when it moves (`tandemdrive/ocpi-tariffs`), and would otherwise claim the same `classifications.csv` key. A `CODEBERG_REPOS` entry that Codeberg answers 404 for is skipped with a warning, but any other failure to read it (5xx, rate limit, network error) makes `ingest` exit non-zero before it writes the CSV, since that mirror is excluded and the repo would otherwise silently drop out of the listing.

**Stage 2 — `enrich` → `repos.enriched.csv`** (`enrich`, `classify_with_*`):
Reads the CSV, fetches each README (cached), and appends a `categories` column. Classification runs through a **pluggable LLM-CLI backend** selected by `--classifier` (registry `CLASSIFIERS`, default `claude`):

- `claude` — `classify_with_claude` shells out to `claude -p --agent repo-classifier --strict-mcp-config --output-format text` (agent defined in `.claude/agents/repo-classifier.md`);
- `codex` — `classify_with_codex` runs `codex exec --sandbox read-only --ephemeral`, carrying the role/output contract in-prompt (`CLASSIFIER_INSTRUCTIONS`) since it has no agent file;
- `copilot` — `classify_with_copilot` runs `copilot -p --available-tools='' --silent` in an empty temp cwd, also using `CLASSIFIER_INSTRUCTIONS`. The GitHub Copilot CLI is natively authenticated inside a Copilot coding-agent environment. Elsewhere it reads a token from `COPILOT_GITHUB_TOKEN` → `GH_TOKEN` → `GITHUB_TOKEN` (in that precedence; classic `ghp_` PATs are ignored). **In GitHub Actions** (since 2026-07-02) no secret is needed: grant the job the `copilot-requests: write` permission and it authenticates with the built-in `GITHUB_TOKEN` — see `.github/workflows/refresh-metadata.yml`. **In any other CI runner** it needs a fine-grained PAT owned by a personal account with the **Copilot Requests** *account* permission (token Permissions → Account tab).

All backends emit the same `Description:` / `Categories:` text; `CATEGORY_TREE` is passed in the prompt (single source of truth) and output is parsed by `parse_classification` / `parse_categories` (`- Main > Sub` lines).

**Every main category carries a subcategory, `Other` included.** `CATEGORY_TREE["Other"]` is a closed list; the contract tells the model to pick from it and propose a new label only when none fits, and never to return a bare `Main`. Left empty, it showed the model a bare `- Other`, and the answer was a bare `Other` (68 of 606 rows) or a fresh one-repo label (over 100 of them), varying between runs. `SUBCATEGORY_ALIASES` folds the remaining stray labels onto the list at render time — **under `Other` only**, since keys such as `simulator` and `libraries` are protocol subcategories too — and every target must be spelled exactly as in `CATEGORY_TREE`, which `tests/test_pipeline.py` checks. The parser still accepts a bare main: dropping it would empty the category and fail the guard below. The list order is the README's section order, so keep it alphabetical.

**A protocol category comes first, and `Other` never replaces it.** A repo gets a protocol main when it *speaks* the protocol — implements, simulates or tests it, or is built specifically for it — not when it mentions it: a client of a vendor API, or of a server that happens to use OCPP, does not qualify. `Other` adds what the protocol categories cannot say (a Home Assistant integration, charger firmware, a security tool). The contract states both, because the closed `Other` list made the model swap protocols out for an `Other` facet — 55 repos lost `OCPP` in the first #59 run, about a third of them wrongly. The README lists a repo under its **first** category only, so `_row_categories` also sorts protocol categories ahead of `Other` at render, whatever order the classifier used. `render` warns (`::warning::`, never fails) about every `Main > Sub` outside `CATEGORY_TREE` once aliases and overrides apply, since each one opens a new README section — alias it, add it to the taxonomy, or override the repo.

A backend is only skipped when there is **nothing to classify at all** (`has_classifiable_signal`): no README *and* no GitHub description *and* no topics. A repo can legitimately ship no README, and the prompt already carries the other two — bailing on a missing README alone left such repos permanently uncategorised.

Each backend returns `(description, categories)` on success, `("", [])` when there was no signal, and **`None` when the CLI itself failed** (non-zero exit, timeout, crash). `enrich` keeps the two apart: an empty result is cached (the emptiness *is* the answer, and caching it stops every run from re-asking), while a `None` leaves the cache entry untouched — so the next run retries instead of freezing the emptiness until the repo is pushed again — and reuses the stale categories for this run's output, so a classifier outage cannot blank the rendered listing.

Enrichment is **incremental**: it loads the committed `classifications.csv` and reuses a repo's categories while nothing the classifier reads has changed, so re-runs only pay the LLM cost for new or updated repos. The reuse key is `classifier_signature` alone — a hash of the whole prompt: the GitHub description, the topics and the README as truncated for the prompt, plus `CATEGORY_TREE_TEXT` and `CLASSIFIER_INSTRUCTIONS`, stored in the `signals` column. It replaced `pushed_at`, which failed in both directions: it only moves on a commit, so a description or topic list edited in the repository settings kept a stale classification indefinitely (and for a repo with no README those two are the *only* inputs); and it moves on *every* commit, so a code-only push — most pushes — paid for an answer that could not have changed. That second half cost 188 of 533 repos in the 2026-09 run. The signature is the exact fingerprint of what the model is shown, so it is both stricter and cheaper than the date. The taxonomy and the contract are hashed with the repo because they are as much a part of the prompt as the README, and since a push no longer invalidates anything, nothing else would ever re-ask — editing either re-classifies the whole listing, which is exactly when every cached answer is stale. The backend and its model are deliberately **not** hashed: they are who answers, not what was asked, and keying on them would make local `claude` runs and CI `copilot` runs thrash each other's cache. `enrich` exits non-zero when every attempt it made failed — a retired model id or an unauthenticated CLI fails every repo identically, each one keeps its cached category, and the regression guard downstream would see nothing wrong and open a PR claiming a refresh that never happened. One flaky repo among several is not that, and stays a warning. A cache entry written before the column existed carries no signature and is still reused; every entry is stamped as it is rewritten, reused ones included, so the check is live for every repo from the next run on. `classifications.csv` is saved after every fresh answer, through a temp file and an atomic rename, so a run killed mid-way (a full re-classification outlives a 2-hour job limit) keeps every answer it paid for and the next run resumes from there. A failed classification leaves that repo's cache entry unchanged, so the next run retries it on its own; `--refresh` ignores the cache and re-classifies every repo. After an edit to `CATEGORY_TREE` or `CLASSIFIER_INSTRUCTIONS`, run `enrich --restamp` instead: every signature is stale, but most answers cannot have moved, so a stale entry is adopted as the answer to the current prompt and stamped with its signature, without a call (`restamped: N` in the summary). Name each catch-all bucket the edit splits with `--reask-category 'Main > Sub'` (repeatable): a stale entry holding one of those labels is asked again, unless `CATEGORY_OVERRIDES` pins the repo, since it renders from the override anyway. A matching signature, a repo missing from the cache, an empty category with something to read and an unreadable README follow the usual rules. In CI, run `refresh-metadata.yml` by hand with its `restamp` and `reask_categories` inputs (buckets `;`-separated); the scheduled run leaves both empty. `--restamp` refuses `--refresh`, and `--reask-category` requires `--restamp`. Three more rules keep the cache honest. An **empty** cached category is reused only when `has_classifiable_signal` says there is nothing to read — otherwise it is a leftover of an older failure and is asked again. A README that **could not be read** (rate limit, 5xx — anything but a 404) is a failure like a CLI failure: the entry is left untouched for the next run, and `enrich` exits non-zero if even one README could not be read — the protocol versions come from the README alone and are cached nowhere, so carrying on would publish that repo with empty versions. The cache is matched **case-insensitively**, like GitHub names, so an owner recasing its name reuses the entry instead of paying for a new one. And `cache_github/` round-trips text byte for byte (`newline=""`): the signature hashes the README, so a CRLF README must fingerprint the same fetched or cached.

The content taxonomy also includes `OpenADR` and `OSCP` protocol mains. OCPP and ISO 15118 tooling distinguish message inspection, developer conformance tests and security tests; ISO 15118 additionally separates EXI codecs and SLAC. These labels do not imply certification. Cross-cutting discovery guides and official legal references are hand-authored outside the generated README markers. See `docs/content-taxonomy-audit.md` for the editorial rationale and evidence.

**Guarding the classification cache.** `python pipeline.py check-classifications --base -` (reading the baseline `classifications.csv` on stdin) is the monthly workflow's gate before it opens a PR. It compares **per repo, not by count**: a repo that *had* a category and comes back without one is a regression and exits non-zero; a newly discovered repo that arrives without one never had a category to lose, and only warns. Counting empty rows conflated the two and blocked the refresh every time a README-less repo entered the listing. It also warns, without failing, about every repo with a bare main category (`bare_main_categories`), whatever its history — a re-run that drifted, a newcomer filed directly under `Other`, or a repo already bare all break the contract; the category is not empty, so the regression check cannot see them. Names are matched **case-insensitively** on both sides, as `enrich` does, so an owner recasing its name is neither a regression nor a newcomer.

Protocol losses are judged on the **effective** categories, the ones the README renders. `classification_diff` passes both sides through `_effective_categories` with the current `CATEGORY_OVERRIDES` and `SUBCATEGORY_ALIASES`, keeps the raw cached categories next to them for diagnosis, and returns structured per-repo results (added and removed `Main > Sub` labels, the primary category before and after, and each protocol loss with its status); `check_classifications` only prints them. A protocol is any main but `Other`, and an emptied category stays the lost-category check's business. A repo that loses a protocol on the page, with no reviewed reason, is an **unexplained loss**: `::error::` and exit 1, even when no category was emptied — fix it with a `CATEGORY_OVERRIDES` entry when the classifier is wrong, or with an `ACCEPTED_PROTOCOL_LOSSES` entry (`{"owner/name": {"OCPP": "reason"}}`, lowercased key) when the non-protocol result is right. That exception excuses the named protocol for the named repo only, so a later loss of another protocol still blocks. A raw loss that an override keeps on the page (masked), an accepted loss with its reason, added and removed categories, primary-category changes and stale exceptions (the repo is gone, or carries the protocol again) are printed as plain lines rather than annotations, so the only annotations left are the ones to act on; the final line counts each class.

`--report <path>` also writes the findings as Markdown (`classification_report`): a count per class, then one table per non-empty class with the raw and effective categories side by side, sorted and without a timestamp so two runs on the same inputs are byte-identical. The report is published unescaped, and its cells carry untrusted text (classifier output, GitHub names, the export), so every data cell goes through `_cell`: one inline code span, its fence longer than any backtick run in the value, line breaks turned into spaces and `|` escaped as `\|`, so no link, image, HTML or @mention renders. A category label stays plain (flattened to one line) only when `CATEGORY_TREE` knows it once aliases apply; any other reads `(unknown label)` followed by the quoted value. Empty cells read `(none)`. It is written **before** the guard exits, so a blocked run still has it. `--base-projects <path>` adds the selection / dormant / to_refine movements between that `projects.json` export and `--projects` (default `data/projects.json`), plus the projects that entered or left the export (`curation_movements`, per `id`). They come from fresh metadata, not classification, and never fail the guard: the exit code is decided by the classification checks alone. When the baseline is absent, or `--base-projects` is not given, the report says in one line that there is no baseline — that is the case until #98 commits `data/projects.json`. A fresh export missing next to a baseline, or a file that is present but is not an export (invalid JSON, no `projects` list, a record without a string `id` or a `curation`, a duplicate `id`), is a `::warning::` and the same explanation as a line in the report: it points at a broken render, a broken baseline or an export schema change, none of which may block the monthly refresh. In `refresh-metadata.yml` the guard step runs under `set -o pipefail`, so a failing `git show` cannot feed an empty baseline that would read every repo as a newcomer, passes `--report`, and `--base-projects` only when `HEAD` holds `data/projects.json` and `git show` can read it (otherwise a `::warning::` and the guard runs without it); a step with `if: always()` appends the report to the job summary, and the PR body is the static text plus the report (`body-path`; `create-pull-request` truncates a body past GitHub's 65,536 characters itself).

**Triaging a failed refresh run.** `gh run view <id> --log-failed` shows the tail of the failing step, which for this workflow is the guard reporting a symptom — the cause is in the `enrich` step, hundreds of lines earlier. `gh` does not resolve step names in `--log` output (every line reads `UNKNOWN STEP`), so filter on the message, not the columns:

```bash
run_id=33500786084                    # the failing run
log="/tmp/awesome-ev-charging-$run_id.log"
gh run view "$run_id" --log > "$log"
grep -E "\-> \(none\)" "$log"                       # repos that came back uncategorised
grep -E "readme|classifier (failed|error)" "$log"
```

A `⚠️ GitHub request failed: 404 …/readme` immediately above a `(none)` means the repo has no README, which is a fact about the repo; a `⚠️ classifier failed` means the CLI broke, and a `⚠️  README unreadable` that GitHub refused the README, both facts about the run.

Curation knobs are module-level constants: `TOPICS`, `STARRED_USERS`, `STARRED_LISTS`, `EXCLUDED_REPOS`, `ADDITIONAL_REPOS`, `CODEBERG_REPOS`, `CATEGORY_TREE`, `SUBCATEGORY_ALIASES`, `CATEGORY_OVERRIDES`, `ACCEPTED_PROTOCOL_LOSSES`, `REPO_OVERRIDES`, `DORMANT_DAYS`, `CLASSIFIER_AGENT`/`CLASSIFIER_MODEL`/`CLASSIFIER_COPILOT_MODEL`.

`CATEGORY_OVERRIDES` (keyed by lowercased `full_name`) replaces the classifier's category at render. `REPO_OVERRIDES` (same key → `{csv_column: value}` dict) overwrites arbitrary row fields at render — a curated description, or a **repo that migrated off GitHub to a host the pipeline cannot read** (GitLab, self-hosted): the GitHub repo is archived/dormant while active development continues elsewhere, so the override points `html_url` at the new host and forces `dormant` back to `false`. Both are applied at render time (via `_apply_overrides` / `_row_categories`), so they survive `ingest` and `enrich --refresh`. A repo on Codeberg goes in `CODEBERG_REPOS` instead, which reads live metadata and drops the GitHub mirror.

**GitHub caching:** every read goes through `github_request_cached`, a filesystem cache in `cache_github/` keyed by MD5 of the URL, 24h TTL (`CACHE_TTL`). Delete cache files to force a refresh. Note: `get_starred_repos_for_user` and the search pagination call `requests.get` directly and are **not** cached.

## csms.py — the CSMS catalogue

A **deliberately separate script** from `pipeline.py`: that module is GitHub discovery, this one mirrors a non-GitHub registry. It `import pipeline` purely to reuse `auth_headers`, `get_repo_data`, `_inject_between_markers`, `CACHE_DIR` and `CACHE_TTL`. **Do not fold it back into `pipeline.py`.**

```bash
python csms.py fetch    # -> csms-certificates.csv (OCA registry mirror)
python csms.py render   # -> injects the tables into csms.md + csms-features.md
python csms.py render --export-dir data   # ... and writes data/csms.json + its manifest entry
mise run csms           # fetch + render --export-dir data, with the gh token wired in
```

**The curated CSVs are canonical; the Markdown is only a view.** Nothing may
appear in `csms.md` / `csms-features.md` / `data/csms.json` that cannot be reconstructed from
`csms-certificates.csv` + `csms.csv` + `csms-features.csv` and the rules in
`csms.py`.

**Stage 1 — `fetch`.** The OCA certified-products page renders client-side but is backed by a public JSON endpoint: `POST https://openchargealliance.org/wp-json/custom/v1/ajax-loader` with `{id: "299052", paged: N, posts_per_page: 50, post_type: "certificate", filters: [{field: "product-type", value: "Charging Station Management System"}]}`. The endpoint defaults to 6 items per page but honours `posts_per_page`, so asking for 50 turns the sweep into 6 requests instead of 49. `post_json_cached` is the POST counterpart of `github_request_cached` (which is GET-only and picks its cache extension from the `Accept` header), sharing `cache_github/`; its key hashes the payload as well as the URL, since one URL serves every page and filter. Values are whitespace-collapsed and pipe-escaped, dates converted to ISO. Aborts rather than writing a truncated mirror if a page fails.

**Stage 2 — `render`.** Five files, one rule each, plus `data/csms.json` with `--export-dir data` (see "Public JSON export" below):

- `csms-certificates.csv` — generated, one row per certificate (~293). Never hand-edited.
- `csms.csv` — curated, one row per product (or per company): **the canonical dataset**. **No script ever writes it.** Every curated value needs a URL in its `sources` column. Keyed by a unique `slug`; `product_slugs` fails the render on a missing or duplicate one. It deliberately keeps columns the tables no longer show (HQ, founding year, pricing, licence, ISO 15118, Eichrecht, release history) — the view shrank, the dataset did not.
- `csms-features.csv` — curated, one row per `(slug, feature, source_url, note)`. Normalised rather than a list column, because the sourcing rule applies per feature. `read_features` fails the render on a feature outside `FEATURE_VOCAB`, a slug with no product row, or a missing `source_url`, reporting every problem in one pass.
- `csms.md` — the 9-column directory (`Product | Company | OCPP | OCA certificates | Source available | OCPI | API | Deployment | Status`) injected between `<!-- BEGIN/END GENERATED CSMS -->`; the surrounding prose (intro, four caveats, contributing pointer) is hand-authored. Detailed methodology lives in `docs/csms-methodology.md`, outside the deliverable.
- `csms-features.md` — the feature annex (`Product | Company | Certified (OCA) | Vendor-documented`) between `<!-- BEGIN/END GENERATED CSMS FEATURES -->`.

`canonical_product(company, designation)` decides product identity before grouping: it strips a trailing dotted version (`eBAB Server v1.6` / `v1.6.1` → one product; a dot is required so `MON-CSMS-V10` survives) and applies `PRODUCT_ALIASES`, a hand-maintained table for platforms the registry renamed between certificates (Driivz, NEC, KEPCO KDN, Elvo, I-Charge Solutions). `company_key` does the same job on the vendor side, dropping punctuation and parentheticals so `Shenzhen Infypower Co. Ltd` / `Co., Ltd` and `Instituto Tecnológico de la Energía` with and without `(ITE)` group as one company; legal suffixes are deliberately kept. Together they collapse 11 duplicates. `canonical_product` is applied to curated `oca_product` values too, so a contributor may cite either the raw OCA designation or the merged name. Only merge when the certificates clearly describe one platform — vendors do ship several CSMS, and some registry entries are hardware model numbers misfiled under the CSMS product type.

`merge` unions the three: certificates grouped by `(company, canonical product)` lowercased become certified entries; curated product rows matching via `oca_company`/`oca_product` are overlaid onto them; the rest are appended as non-certified; then curated features attach by `slug` through `merge`'s `by_slug` map, since the entry key is `(company, product)` and a curated row may rename either. The slug is also stored on the entry, as the public `id` of `data/csms.json`, so two curated rows landing on one entry fail the render (`_apply_product_row`) rather than let the second take over the first one's id and features. So **certification and source availability are derived, never typed**, and `csms.csv` only needs rows that add information — not the ~193 certified products. A curated row that collides with a certified key merges into it rather than replacing it. `sort_entries` orders by `(display name, company)` — the company tiebreak is what keeps two homonymous products from reshuffling between renders.

**Two kinds of feature evidence, never merged.** `entry["features_certified"]` (a set) is what an OCA certificate proves; `entry["features_claimed"]` (name → source URLs) is what the vendor documents. `csms-features.md` renders them in separate columns, and a feature legitimately appears in both — the reverse promotion never happens.

`derive_features` expands the OCA certificate type into the certified set. `CERT_LETTERS` is the verbatim legend from the registry's own `Certificate type` filter (`S` Advanced Security, `L` Local Authorization List Management, `C` Smart Charging, `D` Advanced Device Management, `R` Reservation, `U` Advanced User Interface, `I` ISO 15118 Support). `OCPP16_FULL` — the expansion of `Full` on OCPP 1.6 into the six OCPP 1.6 feature profiles — is **our inference, not an OCA statement**, and `docs/csms-methodology.md` says so. `Subset`/`Family` are scope qualifiers and yield no features. Unknown tokens are collected and make `render` exit non-zero rather than silently emitting an empty cell; the monthly workflow also fails if the mirror drops below 250 rows.

`FEATURE_VOCAB` is the single controlled vocabulary (canonical name → short label, insertion order = display order), shared by both kinds of evidence so they stay comparable; `FEATURE_RANK` derives from it. Curated names outside it fail the render. `vocabulary_gaps()` guards the other direction: `CERT_LETTERS` and `OCPP16_FULL` are edited independently, and a name they emit that the vocabulary lacks would surface as a mid-render `KeyError` instead of an actionable message.

Features are derived at render, never stored — `certificate_type` stays raw in the CSV, so fixing the mapping fixes the whole file.

Column semantics worth not re-deriving: **`Product`** carries the link to the vendor site (or the repo) — there is no separate `Website` column. **`Source available`** is `Y` or empty, **never `N`**: we check whether a repository exists, not whether one is absent. **`API`** separates two facts — `api` means a reliable source attests an API exists (login-gated documentation included), `api_docs` means that documentation is public, so a documented-but-gated API is an unlinked `Y` and an empty cell is *unverified*. **`OCPI`** is `Y` when the `ocpi` column says so or a curated `OCPI Roaming` feature exists, linked to the feature's source. `pricing`, `changelog`, `latest_version` and the rest stay in the CSV without a column — and are curated only: `enrich_from_github` no longer derives them, since nothing rendered what it produced.

A curated row with `oca_company` set and `oca_product` **empty** carries company-level facts (`COMPANY_FIELDS`: website, founding year, HQ, API, pricing…) and is applied to every entry of that company, certified or not — one row instead of one per listing. `fill_only=True`, so it only fills gaps a product row left empty.

Two traps this design exists to avoid: a commercial product built on an open-source project does not make that project certified (`steve` vs `powerfill` rows), and `enrich_from_github` deliberately ignores the repo's `homepage` field because projects point it at a hosted commercial offering.

Scope for non-certified rows: companies publishing a **named, OCPP-based management platform**. CPO networks, roaming hubs and unnamed vendor portals are out — `docs/csms-methodology.md` states this so the omissions read as a choice.

## Agent configuration

Each harness keeps its own copy of the same two things, and they drift silently
if only one is edited:

| Path | Used by | Holds |
| --- | --- | --- |
| `.claude/agents/repo-classifier.md` | Claude Code, and `enrich --classifier claude` | The classifier role + output contract |
| `.codex/agents/repo-classifier.toml` | Codex | The same contract, in TOML |
| `CLASSIFIER_INSTRUCTIONS` in `pipeline.py` | `codex` and `copilot` backends | The same contract, in-prompt |
| `.claude/skills/` | Claude Code (`/add-project`, `/refresh-metadata`) | The two maintenance workflows |
| `.agents/skills/` | Any other harness | Harness-neutral copies of the same two |

Change the classifier's role or output shape in one place and you must change
it in the other three — `parse_classification` parses one format for all of
them.

## Conventions

- `repos.csv` / `repos.enriched.csv` are generated artifacts (git-ignored). `classifications.csv` is the durable, committed LLM cache. `cache_github/` is regenerable API-response cache — treat it as disposable, not source.
- The `## Tools and Resources` project listing is **generated** — do not edit it by hand in `README.md`. To add/remove a repo there: it must be discoverable by `ingest` (via a `TOPICS` match, a curated stars-list entry in `STARRED_LISTS`, an `ADDITIONAL_REPOS` entry, a `CODEBERG_REPOS` entry for a Codeberg-only repo, or a GitHub link elsewhere in `README.md`), then `enrich` and `render --readme README.md`. Use `EXCLUDED_REPOS` to drop one. Promotion tier (which decides `Selection` vs `To refine`) is driven by the star lists / contributor status, not by manual ordering.
- `data/` (`projects.json`, `csms.json`, `manifest.json`) is generated by the two renders with `--export-dir data`, committed, and **never hand-edited**; `data/schema/` holds the hand-written JSON Schemas versioned with it. A change to canonical data regenerates `data/` in the same PR.
- **No AI attribution in commit messages.** No `Co-Authored-By:` trailer naming an assistant, and no mention of one in the body. Standing rule from the repo owner.
- **An empty cell means unknown, never "no".** This holds across both deliverables and is the reason curated values require a citable source: absence records what we could not verify, not a property of the thing. Do not "complete" a table by inferring a negative.

## Stage 3 — `render` → README (Selection) + legacy-projects.md

`render` (`python pipeline.py render`) builds a curated view from `repos.enriched.csv`, grouped by `category > subcategory` (Libraries additionally split by language). Rows are partitioned by a promotion score (both star lists `2` > juherr-only or a repo contributor `1` > mateogreil-only `0` > neither `-1`) and activity into three blocks: `Selection` = promotion ≥ 0 and active, `Dormant` = promotion ≥ 0 but dormant/deprecated, `To refine` = promotion < 0. `_curation` is that partition, and both the Markdown and the `curation` field of `data/projects.json` read it.

To satisfy the `sindresorhus/awesome` requirements (verified with `npx awesome-lint`), the **README publishes only `Selection`** — the awesome list must feature just maintained, curated items. `Dormant` + `To refine` go to a **secondary `legacy-projects.md`** (`--out`), which the README links in prose (not as a list item). Conformance details baked into the render:

- `_render_line` emits awesome-lint-clean items — `- [owner/name](url) - Description (⭐ N · versions · lang).`: plain (non-bold) link, real ` - ` hyphen separator, description auto-capitalised and period-terminated, metadata folded into the trailing parenthetical so the item still ends with a period.
- `_render_grouped` single-lists each repo under its **primary (first) category only** — the awesome format forbids duplicate links (`remark-lint:double-link`).
- `_build_toc` regenerates the **whole** `## Contents` list (between `README_TOC_BEGIN` / `README_TOC_END`) as one contiguous list with **one nesting level** (`##` sections → their `###` children; deeper levels omitted), skipping meta sections (Contributing/License/…). `_slugify` mirrors GitHub's anchor slugger (drops symbols like `³`).
- The generated project body has **no** H1/`## Selection` wrapper — top level is the per-protocol `### main` — so it slots straight under `## Tools and Resources`.
- With `--readme README.md`, `_inject_between_markers` replaces the `README_MARKER_BEGIN` / `README_MARKER_END` (projects) and `README_TOC_BEGIN` / `README_TOC_END` (Contents) regions; it aborts if a marker pair is missing or out of order.
- Not yet conformant: a CC0 `LICENSE` file is still required at the repo root (add via GitHub's "Add license" UI so `licensee` detects it); the AI-generated descriptions are a separate open question before any submission.

## Public JSON export — `data/`

`render --export-dir data` (both scripts) writes a public JSON view of the same data; `docs/public-data.md` is the consumer contract (fields, `null` = unknown, versioning, sample queries). `pipeline.py` writes `projects.json` (`projects_payload`, from the rendered rows, overrides applied) and `csms.py` writes `csms.json` (`csms_payload`, from the three CSVs only — `repo_url` is built from the curated `repo`, never from GitHub's answer, so the export reproduces offline). Each payload is built before any file is written and fails on a duplicate `id`. Before overwriting `data/csms.json`, `csms.py` prints one warning listing the ids the previous file had and the new one drops (`disappeared_ids`), since those break consumer URLs; a missing or unparseable previous file is skipped silently. Both go through `pipeline.dump_public_json` (sorted keys, indent 2, trailing newline) and refresh their own entry in `data/manifest.json` through `pipeline.write_manifest` (checksum, record count, input checksums, no timestamp). `PUBLIC_SCHEMA_VERSION` must match the `const` in `data/schema/*.schema.json`. `data/projects.json` is not committed yet (issue #98): it needs `repos.enriched.csv`, so the monthly refresh writes it. In `refresh-metadata.yml` the CSMS steps run before the project render, because the CSMS drop step restores `data/manifest.json` from HEAD and would otherwise erase the `projects` entry.
