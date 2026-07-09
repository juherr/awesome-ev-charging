---
name: refresh-metadata
description: >-
  Refresh the awesome-ev-charging project listing's metadata (stars, forks,
  pushed_at, dormant/archived signals) and re-render it into README.md — the
  periodic maintenance pass, with no new repo to add and no issue to close. Use
  this whenever the user wants to "refresh the metadata", "update the stars",
  "re-run the pipeline", "mets à jour la liste / les métadonnées", "rafraîchis
  le README", or otherwise bring the generated listing up to date with GitHub.
  Handles the cache-vs-TTL decision (whether to clear cache_github/ before
  re-fetching) that a plain re-run gets wrong. For ADDING or REMOVING a specific
  repo, use add-project instead. Never hand-edit README.md between the generated
  markers.
---

# Refresh the awesome-ev-charging listing metadata

The published project listing (`## Tools and Resources` in `README.md`, between
`<!-- BEGIN GENERATED PROJECTS -->` / `<!-- END GENERATED PROJECTS -->`) is
**generated** from `repos.enriched.csv` by `pipeline.py`. Over time the upstream
GitHub numbers drift — repos gain stars, get archived, or cross the
`DORMANT_DAYS` threshold — so the listing needs a periodic refresh. This skill
is that maintenance pass: re-fetch GitHub, re-classify only what changed, and
re-render, in the correct order with one clean commit.

This is **not** `add-project`. There is no repo to make discoverable, no
category to pin, no issue to close. If the goal is to add or remove one specific
repo, use `add-project` instead — it handles the discovery + reconciliation
steps this skill deliberately skips.

Read `CLAUDE.md` in the repo root for the authoritative "why" behind the
pipeline; this skill is the executable "how" for the refresh case.

## Preconditions

- `mise trust` has been run (mise pins Python 3.11 and auto-activates `.venv`).
- `gh auth token` works — the mise tasks wire it in for the GitHub API and the
  GraphQL-only Stars lists (`STARRED_LISTS`), which are **skipped when
  unauthenticated**. Check with `gh auth token >/dev/null && echo OK`.

## The cache decision (do this first — it's the whole point)

Every GitHub read goes through a filesystem cache in `cache_github/` with a
**24h TTL** (`CACHE_TTL` in `pipeline.py`). This is the step a naive re-run gets
wrong: if the cache is fresh, `ingest` reads it and the metadata **does not
change** — you'd just re-derive identical docs.

So decide based on **why** you're refreshing:

- **You want fresh GitHub numbers** (stars, `pushed_at`, newly-archived repos) —
  the cache must be older than the data you want, or cleared. Check its age:

  ```bash
  find cache_github -type f -printf '%T@\n' 2>/dev/null | sort -rn | head -1 \
    | awk -v now="$(date +%s)" '{ printf "newest cache file: %.1fh old (TTL 24h)\n", (now-$1)/3600 }'
  ```

  If the newest file is **< 24h old** and you need genuinely fresh numbers,
  clear the cache before ingesting:

  ```bash
  rm -rf cache_github/
  ```

  If it's already **> 24h old**, the TTL has expired — `ingest` will re-fetch on
  its own, no need to clear.

- **You only need to re-derive the docs** from CSVs you (or a prior run) already
  produced — e.g. after hand-editing `classifications.csv`, or tweaking render
  logic — then **do not touch the cache** and you can often skip straight to
  render (Step 3).

**Don't clear a fresh cache reflexively.** Clearing forces ~900 API calls and a
longer run; only do it when you actually want newer-than-cache data. When in
doubt, tell the user the cache age and let them choose.

## Workflow

### 1. Ingest → `repos.csv`

Re-collects candidates from all four discovery sources and rebuilds every record
(so `stars`, `pushed_at`, `dormant`, etc. reflect current GitHub — or the cache,
per the decision above).

```bash
mise run ingest
```

### 2. Enrich → `repos.enriched.csv`

```bash
mise run enrich
```

- Enrichment is **incremental**: it reuses cached classifications keyed by
  `pushed_at`, so only repos whose upstream changed since the last run pay the
  LLM cost. A metadata refresh therefore re-classifies **few** repos, not all.
- **Never pass `--refresh`** — it re-classifies everything and would blow away
  any hand-pinned `classifications.csv` cells. `--refresh` is only for retrying a
  specific repo whose classification came back empty from a transient failure.
- This iterates all repos fetching READMEs and can take a few minutes. Run it in
  the background and wait for it to finish rather than polling tightly.

### 3. Render → inject into README + standalone

```bash
python pipeline.py render --readme README.md
```

This replaces the text between the `GENERATED` markers in `README.md` and also
rewrites the standalone `legacy-projects.md`. It aborts if the
markers are missing or out of order.

### 4. Review the diff — expect broad drift

A refresh is *expected* to touch many rows: any repo whose `pushed_at` moved
gets re-classified, and star/dormant changes reshuffle which block
(`Selection` / collapsed `Dormant` / collapsed `To refine`) a repo lands in. So
a large diff is normal, not a bug. Sanity-check that nothing regressed to an
empty category unexpectedly and that the block moves look plausible:

```bash
git --no-pager diff --stat
git --no-pager diff classifications.csv | grep -E '^\+' | grep -iE ',$|,\s*$' # rows that lost their category
```

If a repo unexpectedly went dormant or lost its classification, investigate
before committing rather than baking a regression into the listing.

### 5. Commit — one `chore(data)` commit

Unlike `add-project`, there's no source change to split out — a pure refresh
touches only generated, committed artifacts. **The regenerable artifacts
`repos.csv`, `repos.enriched.csv`, `cache_github/`, `list.txt` are git-ignored —
never commit them.** Commit only the durable, published files:

```bash
git add classifications.csv README.md legacy-projects.md
git commit -m "chore(data): refresh project listing

Re-ran ingest + enrich + render. Refreshes N repos whose upstream metadata
(stars, pushed_at, dormant/archived) changed since the last run."
```

Fill in `N` from the diff. If the refresh also pulled in `pipeline.py` changes
(e.g. you cleared cache *and* bumped a curation constant), that's really an
`add-project`-shaped change — commit the code separately.

Conventions to honor:

- **Conventional Commits**, in **English**.
- **No AI/Claude attribution** — do not add a `Co-Authored-By: Claude` trailer
  or any Claude reference. Standing preference for this user.

### 6. Push only if authorized

Pushing to the default branch republishes the awesome list. Ask the user before
pushing if they haven't clearly authorized it — outward-facing actions need
confirmation.

## Golden rules

- ✅ Decide the cache question *first* — a fresh cache means "no real refresh".
- ✅ Never edit `README.md` between the `GENERATED` markers by hand.
- ✅ Never pass `--refresh` to `enrich` during a routine refresh — it destroys
  hand-pinned classifications.
- ✅ Only commit `classifications.csv`, `README.md`,
  `legacy-projects.md` (+ `pipeline.py` if you changed a constant).
- ✅ No Claude/AI references in commit messages.
