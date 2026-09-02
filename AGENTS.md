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

The project is managed with **mise** (`mise.toml`): it pins Python 3.11.11 and
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

python pipeline.py render --readme README.md   # Stage 3 -> injects the curated
#   Selection between the markers in README.md and writes the secondary
#   legacy-projects.md (dormant + to-refine). Omit --readme to only write the latter.

git show HEAD:classifications.csv | python pipeline.py check-classifications --base -
#   CI guard, see "Guarding the classification cache" below.
```

`--token` is optional; without it GitHub's unauthenticated rate limits apply.
`gh auth token` supplies one when the gh CLI is authenticated.

`mise run test` (alias `t`) runs the pytest suite in `tests/`, which covers
`csms.py` only: the controlled feature vocabulary, certificate derivation,
product/company identity, merge precedence, table rendering, the curated-CSV
validations and render determinism. It needs no network — the one GitHub call
`merge` can make is monkeypatched — and it also validates the committed CSVs, so
a bad curated row fails there as well as at render time. `tests/test_pipeline.py`
covers `pipeline.py`'s classification layer — the CI guard, the "is there
anything to classify" rule, the backends' failure contract and what `enrich`
writes to the durable cache — with the backend and the README fetch stubbed, so
it needs no network and spawns no LLM CLI. The rest of `pipeline.py` is
untested; its pure functions can be exercised by importing `pipeline` and
calling `build_repo_record` / `days_since_push` / `parse_categories` directly.

Markdown is linted by `npx markdownlint-cli2` (config in
`.markdownlint-cli2.jsonc`); `README.md` additionally by `npx awesome-lint`.

## pipeline.py architecture

A two-stage pipeline connected by a **CSV boundary** — ingestion (deterministic, GitHub-only) is deliberately separated from enrichment (the slow/flaky LLM step), so the CSV can be reviewed/curated in a spreadsheet and enrichment can be re-run without re-fetching.

**Stage 1 — `ingest` → `repos.csv`** (`ingest`, `collect_candidates`, `build_repo_record`):
`collect_candidates` merges four **discovery** sources by `full_name` — topic search (`search_topic_repo_names` across `TOPICS`), manual additions (`ADDITIONAL_REPOS`), GitHub links in the curated README (`readme_repo_names`), and curated GitHub Stars lists (`get_starred_list_repos` for each `(owner, slug)` in `STARRED_LISTS`, e.g. `juherr/ev`, `mateogreil/ev-mobility`). Stars lists are GraphQL-only and require a token, so ingest skips them (with a warning) when unauthenticated. Separately, the **full** star sets of `STARRED_USERS` (`get_starred_repos_for_user`) are read only as a **promotion signal** (`starred_by`), not as a discovery source. `build_repo_record` is the single record builder for **all** sources — it reads every field from the full `/repos` object, so `pushed_at` (hence the `dormant`/`days_since_push` signals) is present for every repo, not just manual ones. Signals in the CSV: `dormant` (no push ≥ `DORMANT_DAYS` OR archived), `stars`, `forks`, `open_issues`, `topic_matches`, `promoted`, `archived`, `is_fork`, plus `source` (the `+`-joined provenance, e.g. `readme+starred-list+topic`).

**Stage 2 — `enrich` → `repos.enriched.csv`** (`enrich`, `classify_with_*`):
Reads the CSV, fetches each README (cached), and appends a `categories` column. Classification runs through a **pluggable LLM-CLI backend** selected by `--classifier` (registry `CLASSIFIERS`, default `claude`):

- `claude` — `classify_with_claude` shells out to `claude -p --agent repo-classifier --strict-mcp-config --output-format text` (agent defined in `.claude/agents/repo-classifier.md`);
- `codex` — `classify_with_codex` runs `codex exec --sandbox read-only --ephemeral`, carrying the role/output contract in-prompt (`CLASSIFIER_INSTRUCTIONS`) since it has no agent file;
- `copilot` — `classify_with_copilot` runs `copilot -p --available-tools='' --silent` in an empty temp cwd, also using `CLASSIFIER_INSTRUCTIONS`. The GitHub Copilot CLI is natively authenticated inside a Copilot coding-agent environment. Elsewhere it reads a token from `COPILOT_GITHUB_TOKEN` → `GH_TOKEN` → `GITHUB_TOKEN` (in that precedence; classic `ghp_` PATs are ignored). **In GitHub Actions** (since 2026-07-02) no secret is needed: grant the job the `copilot-requests: write` permission and it authenticates with the built-in `GITHUB_TOKEN` — see `.github/workflows/refresh-metadata.yml`. **In any other CI runner** it needs a fine-grained PAT owned by a personal account with the **Copilot Requests** *account* permission (token Permissions → Account tab).

All backends emit the same `Description:` / `Categories:` text; `CATEGORY_TREE` is passed in the prompt (single source of truth) and output is parsed by `parse_classification` / `parse_categories` (`- Main > Sub` lines).

A backend is only skipped when there is **nothing to classify at all** (`has_classifiable_signal`): no README *and* no GitHub description *and* no topics. A repo can legitimately ship no README, and the prompt already carries the other two — bailing on a missing README alone left such repos permanently uncategorised.

Each backend returns `(description, categories)` on success, `("", [])` when there was no signal, and **`None` when the CLI itself failed** (non-zero exit, timeout, crash). `enrich` keeps the two apart: an empty result is cached (the emptiness *is* the answer, and caching it stops every run from re-asking), while a `None` leaves the cache entry untouched — so the next run retries instead of freezing the emptiness until the repo is pushed again — and reuses the stale categories for this run's output, so a classifier outage cannot blank the rendered listing.

Enrichment is **incremental**: it loads the committed `classifications.csv` and reuses a repo's categories while nothing the classifier reads has changed, so re-runs only pay the LLM cost for new or updated repos. The reuse key is `pushed_at` **plus** `classifier_signature` — a hash of the GitHub description, the topics and the README as truncated for the prompt, stored in the `signals` column. `pushed_at` alone was not enough: it only moves on a commit, so a description or topic list edited in the repository settings kept a stale classification indefinitely — and for a repo with no README those two are the *only* inputs. A cache entry written before the column existed carries no signature and is still reused (re-classifying all ~500 repos in one run would not fit the workflow's 30-minute timeout); every entry is stamped as it is rewritten, reused ones included, so the check is live for every repo from the next run on. A failed classification leaves that repo's cache entry unchanged, so the next run retries it on its own; `--refresh` ignores the cache and re-classifies every repo.

**Guarding the classification cache.** `python pipeline.py check-classifications --base -` (reading the baseline `classifications.csv` on stdin) is the monthly workflow's gate before it opens a PR. It compares **per repo, not by count**: a repo that *had* a category and comes back without one is a regression and exits non-zero; a newly discovered repo that arrives without one never had a category to lose, and only warns. Counting empty rows conflated the two and blocked the refresh every time a README-less repo entered the listing.

**Triaging a failed refresh run.** `gh run view <id> --log-failed` shows the tail of the failing step, which for this workflow is the guard reporting a symptom — the cause is in the `enrich` step, hundreds of lines earlier. `gh` does not resolve step names in `--log` output (every line reads `UNKNOWN STEP`), so filter on the message, not the columns:

```bash
run_id=33500786084                    # the failing run
log="/tmp/awesome-ev-charging-$run_id.log"
gh run view "$run_id" --log > "$log"
grep -E "\-> \(none\)" "$log"                       # repos that came back uncategorised
grep -E "readme|classifier (failed|error)" "$log"
```

A `⚠️ GitHub request failed: 404 …/readme` immediately above a `(none)` means the repo has no README, which is a fact about the repo; a `⚠️ classifier failed` means the CLI broke, which is a fact about the run.

Curation knobs are module-level constants: `TOPICS`, `STARRED_USERS`, `STARRED_LISTS`, `EXCLUDED_REPOS`, `ADDITIONAL_REPOS`, `CATEGORY_TREE`, `CATEGORY_OVERRIDES`, `REPO_OVERRIDES`, `DORMANT_DAYS`, `CLASSIFIER_AGENT`/`CLASSIFIER_MODEL`/`CLASSIFIER_COPILOT_MODEL`.

`CATEGORY_OVERRIDES` (keyed by lowercased `full_name`) replaces the classifier's category at render. `REPO_OVERRIDES` (same key → `{csv_column: value}` dict) overwrites arbitrary row fields at render — used mainly for a **repo that migrated off GitHub**: the GitHub repo is archived/dormant while active development continues elsewhere (e.g. `tandemdrive/ocpi-tariffs` moved to Codeberg), so the override points `html_url` at the new host and forces `dormant` back to `false`. Both are applied at render time (via `_apply_overrides` / `_row_categories`), so they survive `ingest` and `enrich --refresh`. Future evolution: instead of a static `REPO_OVERRIDES` entry, fetch live metadata from the new host's API (Codeberg runs Forgejo, Gitea-compatible: `GET https://codeberg.org/api/v1/repos/{owner}/{repo}` → `stars_count`, `updated_at`, `archived`, no auth) to keep the signals real and auto-refreshed.

**GitHub caching:** every read goes through `github_request_cached`, a filesystem cache in `cache_github/` keyed by MD5 of the URL, 24h TTL (`CACHE_TTL`). Delete cache files to force a refresh. Note: `get_starred_repos_for_user` and the search pagination call `requests.get` directly and are **not** cached.

## csms.py — the CSMS catalogue

A **deliberately separate script** from `pipeline.py`: that module is GitHub discovery, this one mirrors a non-GitHub registry. It `import pipeline` purely to reuse `auth_headers`, `get_repo_data`, `_inject_between_markers`, `CACHE_DIR` and `CACHE_TTL`. **Do not fold it back into `pipeline.py`.**

```bash
python csms.py fetch    # -> csms-certificates.csv (OCA registry mirror)
python csms.py render   # -> injects the tables into csms.md + csms-features.md
mise run csms           # both, with the gh token wired in
```

**The curated CSVs are canonical; the Markdown is only a view.** Nothing may
appear in `csms.md` / `csms-features.md` that cannot be reconstructed from
`csms-certificates.csv` + `csms.csv` + `csms-features.csv` and the rules in
`csms.py`.

**Stage 1 — `fetch`.** The OCA certified-products page renders client-side but is backed by a public JSON endpoint: `POST https://openchargealliance.org/wp-json/custom/v1/ajax-loader` with `{id: "299052", paged: N, posts_per_page: 50, post_type: "certificate", filters: [{field: "product-type", value: "Charging Station Management System"}]}`. The endpoint defaults to 6 items per page but honours `posts_per_page`, so asking for 50 turns the sweep into 6 requests instead of 49. `post_json_cached` is the POST counterpart of `github_request_cached` (which is GET-only and picks its cache extension from the `Accept` header), sharing `cache_github/`; its key hashes the payload as well as the URL, since one URL serves every page and filter. Values are whitespace-collapsed and pipe-escaped, dates converted to ISO. Aborts rather than writing a truncated mirror if a page fails.

**Stage 2 — `render`.** Five files, one rule each:

- `csms-certificates.csv` — generated, one row per certificate (~293). Never hand-edited.
- `csms.csv` — curated, one row per product (or per company): **the canonical dataset**. **No script ever writes it.** Every curated value needs a URL in its `sources` column. Keyed by a unique `slug`; `product_slugs` fails the render on a missing or duplicate one. It deliberately keeps columns the tables no longer show (HQ, founding year, pricing, licence, ISO 15118, Eichrecht, release history) — the view shrank, the dataset did not.
- `csms-features.csv` — curated, one row per `(slug, feature, source_url, note)`. Normalised rather than a list column, because the sourcing rule applies per feature. `read_features` fails the render on a feature outside `FEATURE_VOCAB`, a slug with no product row, or a missing `source_url`, reporting every problem in one pass.
- `csms.md` — the 9-column directory (`Product | Company | OCPP | OCA certificates | Source available | OCPI | API | Deployment | Status`) injected between `<!-- BEGIN/END GENERATED CSMS -->`; the surrounding prose (intro, four caveats, contributing pointer) is hand-authored. Detailed methodology lives in `docs/csms-methodology.md`, outside the deliverable.
- `csms-features.md` — the feature annex (`Product | Company | Certified (OCA) | Vendor-documented`) between `<!-- BEGIN/END GENERATED CSMS FEATURES -->`.

`canonical_product(company, designation)` decides product identity before grouping: it strips a trailing dotted version (`eBAB Server v1.6` / `v1.6.1` → one product; a dot is required so `MON-CSMS-V10` survives) and applies `PRODUCT_ALIASES`, a hand-maintained table for platforms the registry renamed between certificates (Driivz, NEC, KEPCO KDN, Elvo, I-Charge Solutions). `company_key` does the same job on the vendor side, dropping punctuation and parentheticals so `Shenzhen Infypower Co. Ltd` / `Co., Ltd` and `Instituto Tecnológico de la Energía` with and without `(ITE)` group as one company; legal suffixes are deliberately kept. Together they collapse 11 duplicates. `canonical_product` is applied to curated `oca_product` values too, so a contributor may cite either the raw OCA designation or the merged name. Only merge when the certificates clearly describe one platform — vendors do ship several CSMS, and some registry entries are hardware model numbers misfiled under the CSMS product type.

`merge` unions the three: certificates grouped by `(company, canonical product)` lowercased become certified entries; curated product rows matching via `oca_company`/`oca_product` are overlaid onto them; the rest are appended as non-certified; then curated features attach by `slug` (carried in `merge`'s `by_slug` map rather than stored on the entry, since the entry key is `(company, product)` and a curated row may rename either). So **certification and source availability are derived, never typed**, and `csms.csv` only needs rows that add information — not the ~193 certified products. A curated row that collides with a certified key merges into it rather than replacing it. `sort_entries` orders by `(display name, company)` — the company tiebreak is what keeps two homonymous products from reshuffling between renders.

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
- The `## Tools and Resources` project listing is **generated** — do not edit it by hand in `README.md`. To add/remove a repo there: it must be discoverable by `ingest` (via a `TOPICS` match, a curated stars-list entry in `STARRED_LISTS`, an `ADDITIONAL_REPOS` entry, or a GitHub link elsewhere in `README.md`), then `enrich` and `render --readme README.md`. Use `EXCLUDED_REPOS` to drop one. Promotion tier (which decides `Selection` vs `To refine`) is driven by the star lists / contributor status, not by manual ordering.
- **No AI attribution in commit messages.** No `Co-Authored-By:` trailer naming an assistant, and no mention of one in the body. Standing rule from the repo owner.
- **An empty cell means unknown, never "no".** This holds across both deliverables and is the reason curated values require a citable source: absence records what we could not verify, not a property of the thing. Do not "complete" a table by inferring a negative.

## Stage 3 — `render` → README (Selection) + legacy-projects.md

`render` (`python pipeline.py render`) builds a curated view from `repos.enriched.csv`, grouped by `category > subcategory` (Libraries additionally split by language). Rows are partitioned by a promotion score (both star lists `2` > juherr-only or a repo contributor `1` > mateogreil-only `0` > neither `-1`) and activity into three blocks: `Selection` = promotion ≥ 0 and active, `Dormant` = promotion ≥ 0 but dormant/deprecated, `To refine` = promotion < 0.

To satisfy the `sindresorhus/awesome` requirements (verified with `npx awesome-lint`), the **README publishes only `Selection`** — the awesome list must feature just maintained, curated items. `Dormant` + `To refine` go to a **secondary `legacy-projects.md`** (`--out`), which the README links in prose (not as a list item). Conformance details baked into the render:

- `_render_line` emits awesome-lint-clean items — `- [owner/name](url) - Description (⭐ N · versions · lang).`: plain (non-bold) link, real ` - ` hyphen separator, description auto-capitalised and period-terminated, metadata folded into the trailing parenthetical so the item still ends with a period.
- `_render_grouped` single-lists each repo under its **primary (first) category only** — the awesome format forbids duplicate links (`remark-lint:double-link`).
- `_build_toc` regenerates the **whole** `## Contents` list (between `README_TOC_BEGIN` / `README_TOC_END`) as one contiguous list with **one nesting level** (`##` sections → their `###` children; deeper levels omitted), skipping meta sections (Contributing/License/…). `_slugify` mirrors GitHub's anchor slugger (drops symbols like `³`).
- The generated project body has **no** H1/`## Selection` wrapper — top level is the per-protocol `### main` — so it slots straight under `## Tools and Resources`.
- With `--readme README.md`, `_inject_between_markers` replaces the `README_MARKER_BEGIN` / `README_MARKER_END` (projects) and `README_TOC_BEGIN` / `README_TOC_END` (Contents) regions; it aborts if a marker pair is missing or out of order.
- Not yet conformant: a CC0 `LICENSE` file is still required at the repo root (add via GitHub's "Add license" UI so `licensee` detects it); the AI-generated descriptions are a separate open question before any submission.
</content>
