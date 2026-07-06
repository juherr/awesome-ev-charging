# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A curated "awesome list" of EV charging protocol tools (OCPP, OCPI, ISO 15118, OICP, eMI³, OIOI, Eichrecht). Two distinct deliverables live here:

1. **`README.md`** — the published awesome list. Its prose (intro, Contents, `## Specifications`, `## Contributing`, `## Other Resources`) is hand-authored. The **project listing** inside `## Tools and Resources` — everything between the `<!-- BEGIN GENERATED PROJECTS -->` / `<!-- END GENERATED PROJECTS -->` markers — is **generated** by `python pipeline.py render --readme README.md` and injected in place. Do **not** hand-edit between those markers; edits are overwritten on the next render. To change what appears there, adjust the pipeline inputs (see Conventions) and re-render.
2. **`pipeline.py`** — a discovery pipeline that scrapes GitHub for candidate repositories, scores them with quality signals, AI-classifies them, and renders the curated project listing that populates the README's `## Tools and Resources` block.

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

python pipeline.py render --readme README.md   # Stage 3 -> injects the project
#   listing between the markers in README.md (also writes the standalone
#   awesome-ev-charging-projects.md). Omit --readme to only write the standalone file.
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
- `copilot` — `classify_with_copilot` runs `copilot -p --allow-all-tools --silent` in an empty temp cwd, also using `CLASSIFIER_INSTRUCTIONS`. The GitHub Copilot CLI is natively authenticated inside a Copilot coding-agent environment; in a plain CI runner it needs `GH_TOKEN`/`GITHUB_TOKEN` set to a fine-grained PAT with the **Copilot Requests** permission.

All backends emit the same `Description:` / `Categories:` text; `CATEGORY_TREE` is passed in the prompt (single source of truth) and output is parsed by `parse_classification` / `parse_categories` (`- Main > Sub` lines).

Enrichment is **incremental**: it loads the previous `repos.enriched.csv` and reuses a repo's categories when its `pushed_at` is unchanged (README unchanged ⇒ classification stable), so re-runs only pay the LLM cost for new or updated repos. The reuse key is `pushed_at` alone; `--refresh` forces a full re-classification (e.g. to retry a repo whose classification came back empty from a transient failure).

Curation knobs are module-level constants: `TOPICS`, `STARRED_USERS`, `STARRED_LISTS`, `EXCLUDED_REPOS`, `ADDITIONAL_REPOS`, `CATEGORY_TREE`, `DORMANT_DAYS`, `CLASSIFIER_AGENT`/`CLASSIFIER_MODEL`/`CLASSIFIER_COPILOT_MODEL`.

**GitHub caching:** every read goes through `github_request_cached`, a filesystem cache in `cache_github/` keyed by MD5 of the URL, 24h TTL (`CACHE_TTL`). Delete cache files to force a refresh. Note: `get_starred_repos_for_user` and the search pagination call `requests.get` directly and are **not** cached.

## Conventions

- `repos.csv` / `repos.enriched.csv` are generated artifacts (git-ignored). `classifications.csv` is the durable, committed LLM cache. `cache_github/` is regenerable API-response cache — treat it as disposable, not source.
- The `## Tools and Resources` project listing is **generated** — do not edit it by hand in `README.md`. To add/remove a repo there: it must be discoverable by `ingest` (via a `TOPICS` match, a curated stars-list entry in `STARRED_LISTS`, an `ADDITIONAL_REPOS` entry, or a GitHub link elsewhere in `README.md`), then `enrich` and `render --readme README.md`. Use `EXCLUDED_REPOS` to drop one. Promotion tier (which decides `Selection` vs `To refine`) is driven by the star lists / contributor status, not by manual ordering.

## Stage 3 — `render` → README + standalone

`render` (`python pipeline.py render`) builds a curated view from `repos.enriched.csv`, grouped by `category > subcategory` (Libraries additionally split by language), with three blocks: `Selection`, collapsible `Dormant`, and collapsible `To refine`. Blocks are ranked by a promotion score (both star lists `2` > juherr-only or a repo contributor `1` > mateogreil-only `0` > neither `-1`; `Selection` = promotion ≥ 0 and active, `Dormant` = promotion ≥ 0 but dormant/deprecated, `To refine` = promotion < 0). The rendered body has **no** H1 or `## Selection` wrapper — its top level is the per-protocol `### main` — so it slots straight under `## Tools and Resources`.

- Always writes the standalone `awesome-ev-charging-projects.md` (`--out`).
- With `--readme README.md` it also replaces the text between `README_MARKER_BEGIN` / `README_MARKER_END` via `_inject_between_markers` (which aborts if the markers are missing or out of order).
- The older `awesome-ev-charging.md` / `-grouped.md` artifacts were removed.
</content>
