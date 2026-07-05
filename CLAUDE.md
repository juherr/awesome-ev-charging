# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A curated "awesome list" of EV charging protocol tools (OCPP, OCPI, ISO 15118, OICP, eMI³, OIOI, Eichrecht). Two distinct deliverables live here:

1. **`README.md`** — the hand-curated, published awesome list. This is the human-authored source of truth and is edited manually.
2. **`pipeline.py`** — a discovery pipeline that scrapes GitHub for candidate repositories, scores them with quality signals, and AI-classifies them. Its CSV/Markdown outputs are a *research aid* used to find repos worth adding to `README.md`, not a replacement for it.

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
```

`--token` is optional; without it GitHub's unauthenticated rate limits apply.
`gh auth token` supplies one when the gh CLI is authenticated.

There are no tests, linters, or build steps. Pure functions can be exercised by
importing `pipeline` and calling `build_repo_record` / `days_since_push` /
`parse_categories` directly.

## pipeline.py architecture

A two-stage pipeline connected by a **CSV boundary** — ingestion (deterministic, GitHub-only) is deliberately separated from enrichment (the slow/flaky LLM step), so the CSV can be reviewed/curated in a spreadsheet and enrichment can be re-run without re-fetching.

**Stage 1 — `ingest` → `repos.csv`** (`ingest`, `collect_candidates`, `build_repo_record`):
Merges three sources by `full_name` — topic search (`search_topic_repo_names` across `TOPICS`), starred repos (`get_starred_repos_for_user` for `STARRED_USERS`, used as a promotion signal), and manual additions (`ADDITIONAL_REPOS`). `build_repo_record` is the single record builder for **all** sources — it reads every field from the full `/repos` object, so `pushed_at` (hence the `dormant`/`days_since_push` signals) is present for every repo, not just manual ones. Signals in the CSV: `dormant` (no push ≥ `DORMANT_DAYS` OR archived), `stars`, `forks`, `open_issues`, `topic_matches`, `promoted`, `archived`, `is_fork`.

**Stage 2 — `enrich` → `repos.enriched.csv`** (`enrich`, `classify_with_claude`):
Reads the CSV, fetches each README (cached), and appends a `categories` column. Classification is done by a **Claude skill agent** — `classify_with_claude` shells out to `claude -p --agent repo-classifier --strict-mcp-config --output-format text` (agent defined in `.claude/agents/repo-classifier.md`), replacing the former local-Ollama call. `CATEGORY_TREE` is passed in the prompt (single source of truth); output is parsed by `parse_categories` (`- Main > Sub` lines).

Enrichment is **incremental**: it loads the previous `repos.enriched.csv` and reuses a repo's categories when its `pushed_at` is unchanged (README unchanged ⇒ classification stable), so re-runs only pay the LLM cost for new or updated repos. The reuse key is `pushed_at` alone; `--refresh` forces a full re-classification (e.g. to retry a repo whose classification came back empty from a transient failure).

Curation knobs are module-level constants: `TOPICS`, `STARRED_USERS`, `EXCLUDED_REPOS`, `ADDITIONAL_REPOS`, `CATEGORY_TREE`, `DORMANT_DAYS`, `CLASSIFIER_AGENT`/`CLASSIFIER_MODEL`.

**GitHub caching:** every read goes through `github_request_cached`, a filesystem cache in `cache_github/` keyed by MD5 of the URL, 24h TTL (`CACHE_TTL`). Delete cache files to force a refresh. Note: `get_starred_repos_for_user` and the search pagination call `requests.get` directly and are **not** cached.

## Conventions

- `repos.csv` / `repos.enriched.csv` are generated artifacts (git-ignored). `cache_github/` is regenerable API-response cache — treat it as disposable, not source.
- When adding a repo to the published list, edit `README.md` directly; the pipeline output is only an input to that decision.

## Follow-ups / not yet implemented

- `render` now exists (`python pipeline.py render`) and writes `awesome-ev-charging-projects.md`: a curated view grouped by category/subcategory, with `Selection` / `Dormant` / `To refine` sections ranked by a promotion score (both star lists > juherr or a repo contributor > mateogreil > neither). The older `awesome-ev-charging.md` / `-grouped.md` artifacts were removed.
</content>
