---
name: add-project
description: >-
  Add a project/tool/repository to the awesome-ev-charging generated listing.
  Use this whenever the user wants to add, list, or feature a GitHub repo in the
  awesome list — including handling an "Add a link" GitHub issue (e.g. "traite
  l'ajout de l'issue #27", "add ocpp-debugkit to the list", "ajoute ce repo à la
  liste"). Covers the full pipeline: make the repo discoverable, ingest → enrich
  → render, pin the requested category if the classifier diverges, commit the
  right files, and close the issue. Do NOT hand-edit README.md between the
  generated markers — always go through this workflow. For a plain periodic
  refresh of the whole listing's metadata (no repo to add/remove), use
  refresh-metadata instead.
---

# Add a project to the awesome-ev-charging list

The published project listing (`## Tools and Resources` in `README.md`, between
`<!-- BEGIN GENERATED PROJECTS -->` / `<!-- END GENERATED PROJECTS -->`) is
**generated** by `pipeline.py`. You never edit it by hand — you change the
pipeline inputs and re-render. This skill walks the full, correct sequence so a
new entry lands in the right section with a clean commit history.

Read `CONTRIBUTING.md` and `CLAUDE.md` in the repo root for the authoritative
"why" behind each step; this skill is the executable "how".

**Scope check.** This skill is for adding (or removing) a *specific* repo. If the
task is just a periodic metadata refresh of the whole listing — re-run the
pipeline to pick up new stars / dormant status, with no repo to add — use the
`refresh-metadata` skill instead: it handles the cache-vs-TTL decision and lands
a single `chore(data)` commit rather than the source+data split below.

## Inputs to gather first

From the request (often a GitHub issue opened with the "Add a link" template),
extract three things:

- **URL / `owner/repo`** — the GitHub repo to add.
- **Requested category** — as `Main > Sub` (e.g. `OCPP > Misc`). Valid main
  categories live in `CATEGORY_TREE` in `pipeline.py`; subcategories are free-form.
- **Description** — a one-line factual summary (the enrich classifier will
  produce its own; the issue's is a sanity check).

If the request is a bare URL, still resolve `owner/repo` and confirm the repo
exists before touching anything:

```bash
gh api repos/<owner>/<repo> --jq '{full_name, description, stars: .stargazers_count, pushed_at, archived, fork: .fork}'
```

If it's archived or a fork, mention that to the user — it may still be added but
will land in the `Dormant` / `To refine` blocks.

## Preconditions

- `mise trust` has been run (mise pins Python 3.11 and auto-activates `.venv`).
- `gh auth token` works — the mise tasks wire it in for GitHub API + the
  GraphQL-only Stars lists. Check with `gh auth token >/dev/null && echo OK`.

## Workflow

### 1. Make the repo discoverable by `ingest`

`ingest` only builds records for repos it can discover. The repo qualifies if
**any** of these is true — check in this order and do the least invasive thing:

- it already matches a `TOPICS` GitHub topic (e.g. tagged `ocpp`), or
- it's in a curated Stars list in `STARRED_LISTS` (`juherr/ev`,
  `mateogreil/ev-mobility`), or
- it's linked somewhere in `README.md`, or
- **default action** — add its `owner/repo` to `ADDITIONAL_REPOS` in
  `pipeline.py`.

When unsure, just add it to `ADDITIONAL_REPOS` — it's idempotent and explicit.
A repo can be discovered by several sources at once (the CSV `source` column
shows the `+`-joined provenance); that's fine.

To **remove** instead, add its `full_name` to `EXCLUDED_REPOS` and skip to render.

### 2. Ingest → `repos.csv`

```bash
mise run ingest
```

Confirm the repo is present:

```bash
grep "<owner>/<repo>" repos.csv
```

### 3. Enrich → classifies the new repo

```bash
mise run enrich
```

- Enrichment is **incremental**: it reuses cached classifications keyed by
  `pushed_at`, so only new/changed repos hit the LLM. **Never pass `--refresh`**
  here — it re-classifies everything and would overwrite any hand-pinned cells.
- This can take a few minutes (it iterates all repos, fetching READMEs). Run it
  in the background and wait for it to finish rather than polling tightly.

Then check what category the classifier assigned:

```bash
grep "<owner>/<repo>" classifications.csv
```

### 4. Reconcile category with the request

- If the classifier's `Main > Sub` **matches** the requested category → good,
  nothing to do.
- If it **diverges** and the user's requested category is authoritative → pin it
  by editing that repo's `categories` cell in `classifications.csv` (leave
  `pushed_at` untouched — it's the cache key), then re-run `mise run enrich`
  (cache reuse, no LLM call) so the edit flows into `repos.enriched.csv`. A repo
  can hold several categories separated by `|`.
- Alternatively, for a robust code-level override that survives `--refresh`, add
  an entry to `CATEGORY_OVERRIDES` in `pipeline.py` (key is the **lowercased**
  `owner/repo`, e.g. `"owner/repo": "Main > Sub"`); this applies at render time
  and needs no enrich.

### 5. Render → inject into README + standalone

```bash
python pipeline.py render --readme README.md
```

Verify the entry landed:

```bash
grep -n "<owner>/<repo>" README.md legacy-projects.md
```

The block a repo lands in (`Selection` vs collapsed `Dormant` / `To refine`) is
decided by a promotion score (star lists / contributor status), not by you — so
a low-star repo showing up under `To refine` is expected, not a bug.

### 6. Review the diff — expect drift

Re-running `ingest`/`enrich` commonly **re-discovers and re-classifies other
repos** whose upstream `pushed_at` changed since the last run (the cache reuse
key is `pushed_at`). So the diff on `README.md` / `classifications.csv` is often
much larger than your single addition. This is normal pipeline drift, not a bug.
Sanity-check that nothing regressed to an empty category unexpectedly:

```bash
git --no-pager diff --stat
```

### 7. Commit

Commit only the meaningful files. **Generated artifacts `repos.csv`,
`repos.enriched.csv`, `cache_github/`, `list.txt` are git-ignored — never commit
them.** Split into two commits so the issue's actual source change is traceable
and the data refresh is separate:

```bash
# 1) the source change for the issue
git add pipeline.py
git commit -m "feat(data): add <repo> to ADDITIONAL_REPOS

Requested in issue #<N>. <one-line description>. Classified as <Main > Sub>.

Closes #<N>"

# 2) the regenerated listing (includes unrelated refresh drift)
git add classifications.csv README.md legacy-projects.md
git commit -m "chore(data): refresh project listing (adds <repo>)

Re-ran enrich + render. Injects <repo> (<Main > Sub>) and refreshes N
repos whose upstream pushed_at changed since the last enrichment."
```

Conventions to honor:

- **Conventional Commits**, in **English**.
- **No AI/Claude attribution** in commit messages — do not add a
  `Co-Authored-By: Claude` trailer or any Claude reference. This is a standing
  preference for this user.
- If the change is only the code override path (no data refresh), one `feat`
  commit on `pipeline.py` + `README.md` is enough.

### 8. Close the issue

`Closes #<N>` in the commit auto-closes it on push to the default branch. If you
only committed locally or want to comment, do it explicitly:

```bash
gh issue close <N> --repo juherr/awesome-ev-charging \
  --comment "Added — see <commit sha>. It now appears under <Main > Sub>."
```

Ask the user before pushing/closing if they haven't clearly authorized it —
outward-facing actions need confirmation.

## Golden rules

- ✅ Never edit `README.md` between the `GENERATED` markers by hand.
- ✅ Only commit `classifications.csv`, `README.md`,
  `legacy-projects.md`, and (if changed) `pipeline.py`.
- ✅ Never pass `--refresh` when you want to keep hand-pinned classifications.
- ✅ No Claude/AI references in commit messages.
