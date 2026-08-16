# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
mise run install      # (alias: mise run i) uv pip install -r requirements.txt into .venv

mise run ingest       # Stage 1 -> repos.csv   (wires --token via `gh auth token`)
mise run enrich       # Stage 2 -> repos.enriched.csv

# Or call the script directly (mise auto-activates .venv for commands run in-dir):
python pipeline.py ingest --token <GITHUB_PAT> --out repos.csv
python pipeline.py enrich --in repos.csv --out repos.enriched.csv --token <GITHUB_PAT>
#   enrich flags: --limit N / --skip-forks / --skip-dormant / --refresh

python pipeline.py render --readme README.md   # Stage 3 -> injects the curated
#   Selection between the markers in README.md and writes the secondary
#   legacy-projects.md (dormant + to-refine). Omit --readme to only write the latter.
```

`--token` is optional; without it GitHub's unauthenticated rate limits apply.
`gh auth token` supplies one when the gh CLI is authenticated.

There are no tests, linters, or build steps. Pure functions can be exercised by
importing `pipeline` and calling `build_repo_record` / `days_since_push` /
`parse_categories` directly.

## pipeline.py architecture

A two-stage pipeline connected by a **CSV boundary** — ingestion (deterministic, GitHub-only) is deliberately separated from enrichment (the slow/flaky LLM step), so the CSV can be reviewed/curated in a spreadsheet and enrichment can be re-run without re-fetching.

**Stage 1 — `ingest` → `repos.csv`** (`ingest`, `collect_candidates`, `build_repo_record`):
`collect_candidates` merges four **discovery** sources by `full_name` — topic search (`search_topic_repo_names` across `TOPICS`), manual additions (`ADDITIONAL_REPOS`), GitHub links in the curated README (`readme_repo_names`), and curated GitHub Stars lists (`get_starred_list_repos` for each `(owner, slug)` in `STARRED_LISTS`, e.g. `juherr/ev`, `mateogreil/ev-mobility`). Stars lists are GraphQL-only and require a token, so ingest skips them (with a warning) when unauthenticated. Separately, the **full** star sets of `STARRED_USERS` (`get_starred_repos_for_user`) are read only as a **promotion signal** (`starred_by`), not as a discovery source. `build_repo_record` is the single record builder for **all** sources — it reads every field from the full `/repos` object, so `pushed_at` (hence the `dormant`/`days_since_push` signals) is present for every repo, not just manual ones. Signals in the CSV: `dormant` (no push ≥ `DORMANT_DAYS` OR archived), `stars`, `forks`, `open_issues`, `topic_matches`, `promoted`, `archived`, `is_fork`, plus `source` (the `+`-joined provenance, e.g. `readme+starred-list+topic`).

**Stage 2 — `enrich` → `repos.enriched.csv`** (`enrich`, `classify_with_*`):
Reads the CSV, fetches each README (cached), and appends a `categories` column. Classification runs through a **pluggable LLM-CLI backend** selected by `--classifier` (registry `CLASSIFIERS`, default `claude`):

- `claude` — `classify_with_claude` shells out to `claude -p --agent repo-classifier --strict-mcp-config --output-format text` (agent defined in `.claude/agents/repo-classifier.md`);
- `codex` — `classify_with_codex` runs `codex exec --sandbox read-only --ephemeral`, carrying the role/output contract in-prompt (`CLASSIFIER_INSTRUCTIONS`) since it has no agent file;
- `copilot` — `classify_with_copilot` runs `copilot -p --allow-all-tools --silent` in an empty temp cwd, also using `CLASSIFIER_INSTRUCTIONS`. The GitHub Copilot CLI is natively authenticated inside a Copilot coding-agent environment. Elsewhere it reads a token from `COPILOT_GITHUB_TOKEN` → `GH_TOKEN` → `GITHUB_TOKEN` (in that precedence; classic `ghp_` PATs are ignored). **In GitHub Actions** (since 2026-07-02) no secret is needed: grant the job the `copilot-requests: write` permission and it authenticates with the built-in `GITHUB_TOKEN` — see `.github/workflows/refresh-metadata.yml`. **In any other CI runner** it needs a fine-grained PAT owned by a personal account with the **Copilot Requests** *account* permission (token Permissions → Account tab).

All backends emit the same `Description:` / `Categories:` text; `CATEGORY_TREE` is passed in the prompt (single source of truth) and output is parsed by `parse_classification` / `parse_categories` (`- Main > Sub` lines).

Enrichment is **incremental**: it loads the previous `repos.enriched.csv` and reuses a repo's categories when its `pushed_at` is unchanged (README unchanged ⇒ classification stable), so re-runs only pay the LLM cost for new or updated repos. The reuse key is `pushed_at` alone; `--refresh` forces a full re-classification (e.g. to retry a repo whose classification came back empty from a transient failure).

Curation knobs are module-level constants: `TOPICS`, `STARRED_USERS`, `STARRED_LISTS`, `EXCLUDED_REPOS`, `ADDITIONAL_REPOS`, `CATEGORY_TREE`, `CATEGORY_OVERRIDES`, `REPO_OVERRIDES`, `DORMANT_DAYS`, `CLASSIFIER_AGENT`/`CLASSIFIER_MODEL`/`CLASSIFIER_COPILOT_MODEL`.

`CATEGORY_OVERRIDES` (keyed by lowercased `full_name`) replaces the classifier's category at render. `REPO_OVERRIDES` (same key → `{csv_column: value}` dict) overwrites arbitrary row fields at render — used mainly for a **repo that migrated off GitHub**: the GitHub repo is archived/dormant while active development continues elsewhere (e.g. `tandemdrive/ocpi-tariffs` moved to Codeberg), so the override points `html_url` at the new host and forces `dormant` back to `false`. Both are applied at render time (via `_apply_overrides` / `_row_categories`), so they survive `ingest` and `enrich --refresh`. Future evolution: instead of a static `REPO_OVERRIDES` entry, fetch live metadata from the new host's API (Codeberg runs Forgejo, Gitea-compatible: `GET https://codeberg.org/api/v1/repos/{owner}/{repo}` → `stars_count`, `updated_at`, `archived`, no auth) to keep the signals real and auto-refreshed.

**GitHub caching:** every read goes through `github_request_cached`, a filesystem cache in `cache_github/` keyed by MD5 of the URL, 24h TTL (`CACHE_TTL`). Delete cache files to force a refresh. Note: `get_starred_repos_for_user` and the search pagination call `requests.get` directly and are **not** cached.

## csms.py — the CSMS catalogue

A **deliberately separate script** from `pipeline.py`: that module is GitHub discovery, this one mirrors a non-GitHub registry. It `import pipeline` purely to reuse `github_request_cached`, `auth_headers`, `get_repo_data`, `_inject_between_markers` and `CACHE_DIR`. **Do not fold it back into `pipeline.py`.**

```bash
python csms.py fetch    # -> csms-certificates.csv (OCA registry mirror)
python csms.py render   # -> injects the table into csms.md
mise run csms           # both, with the gh token wired in
```

**Stage 1 — `fetch`.** The OCA certified-products page renders client-side but is backed by a public JSON endpoint: `POST https://openchargealliance.org/wp-json/custom/v1/ajax-loader` with `{id: "299052", paged: N, post_type: "certificate", filters: [{field: "product-type", value: "Charging Station Management System"}]}`, 6 items/page. `post_json_cached` is the POST counterpart of `github_request_cached` (which is GET-only and picks its cache extension from the `Accept` header), sharing `cache_github/`. Values are whitespace-collapsed and pipe-escaped, dates converted to ISO. Aborts rather than writing a truncated mirror if a page fails.

**Stage 2 — `render`.** Three files, one rule each:

- `csms-certificates.csv` — generated, one row per certificate (~293). Never hand-edited.
- `csms.csv` — curated, one row per product. **No script ever writes it.** Every curated value needs a URL in its `sources` column.
- `csms.md` — the table is injected between `<!-- BEGIN/END GENERATED CSMS -->`; the surrounding prose (methodology, feature legend, caveats) is hand-authored and survives regeneration.

`canonical_product(company, designation)` decides product identity before grouping: it strips a trailing dotted version (`eBAB Server v1.6` / `v1.6.1` → one product; a dot is required so `MON-CSMS-V10` survives) and applies `PRODUCT_ALIASES`, a hand-maintained table for platforms the registry renamed between certificates (Driivz, NEC, KEPCO KDN, Elvo, I-Charge Solutions). It collapses 9 duplicates. It is applied to curated `oca_product` values too, so a contributor may cite either the raw OCA designation or the merged name. Only merge when the certificates clearly describe one platform — vendors do ship several CSMS, and some registry entries are hardware model numbers misfiled under the CSMS product type.

`merge` unions the two: certificates grouped by `(company, canonical product)` lowercased become certified entries; curated rows matching via `oca_company`/`oca_product` are overlaid onto them; the rest are appended as non-certified. So **`OCA-certified` and `Open-source` are derived, never typed**, and `csms.csv` only needs rows that add information — not the ~203 certified products. A curated row that collides with a certified key merges into it rather than replacing it.

**Feature derivation** (`derive_features`) expands the OCA certificate type into feature names. `CERT_LETTERS` is the verbatim legend from the registry's own `Certificate type` filter (`S` Advanced Security, `L` Local Authorization List Management, `C` Smart Charging, `D` Advanced Device Management, `R` Reservation, `U` Advanced User Interface, `I` ISO 15118 Support). `OCPP16_FULL` — the expansion of `Full` on OCPP 1.6 into the six OCPP 1.6 feature profiles — is **our inference, not an OCA statement**, and `csms.md` says so. `Subset`/`Family` are scope qualifiers and yield no features. Unknown tokens are collected and make `render` exit non-zero rather than silently emitting an empty cell; the monthly workflow also fails if the mirror drops below 250 rows.

Features are derived at render, never stored — `certificate_type` stays raw in the CSV, so fixing the mapping fixes the whole file.

The rendered table carries `API` (`Y` + link, only when the spec is reachable without an account), `Pricing` (`Price list` / `On request` / `Published` / `Free (self-hosted)`, linked to the page) and `Website` (domain, or `owner/repo` for GitHub via `_host`). `Latest version` links to the product's `changelog`; open-source rows get `github.com/<repo>/releases` automatically, so no separate column is needed.

A curated row with `oca_company` set and `oca_product` **empty** carries company-level facts (`COMPANY_FIELDS`: website, founding year, HQ, API, pricing…) and is applied to every product that company certified — one row instead of one per listing.

Two traps this design exists to avoid: a commercial product built on an open-source project does not make that project certified (`steve` vs `powerfill` rows), and `enrich_from_github` deliberately ignores the repo's `homepage` field because projects point it at a hosted commercial offering.

Scope for non-certified rows: companies publishing a **named, OCPP-based management platform**. CPO networks, roaming hubs and unnamed vendor portals are out — `csms.md` states this so the omissions read as a choice.

## Conventions

- `repos.csv` / `repos.enriched.csv` are generated artifacts (git-ignored). `classifications.csv` is the durable, committed LLM cache. `cache_github/` is regenerable API-response cache — treat it as disposable, not source.
- The `## Tools and Resources` project listing is **generated** — do not edit it by hand in `README.md`. To add/remove a repo there: it must be discoverable by `ingest` (via a `TOPICS` match, a curated stars-list entry in `STARRED_LISTS`, an `ADDITIONAL_REPOS` entry, or a GitHub link elsewhere in `README.md`), then `enrich` and `render --readme README.md`. Use `EXCLUDED_REPOS` to drop one. Promotion tier (which decides `Selection` vs `To refine`) is driven by the star lists / contributor status, not by manual ordering.

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
