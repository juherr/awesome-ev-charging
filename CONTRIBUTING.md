# Contributing

Thanks for helping improve **Awesome Electric Vehicle**! Contributions of new
tools, fixes to descriptions, and better categorization are all welcome.

> **Important:** the project listing under `## Tools and Resources` in
> `README.md` is **generated**. It lives between the
> `<!-- BEGIN GENERATED PROJECTS -->` / `<!-- END GENERATED PROJECTS -->`
> markers and is overwritten on every render. **Never edit it by hand** — change
> the pipeline inputs instead (see below).

There are two ways to contribute, depending on how hands-on you want to be.

## 1. The easy way — open an issue

If you just want to suggest a tool or report a wrong description/category, open an
issue with the **"Add a link"** template:

👉 https://github.com/juherr/awesome-ev-charging/issues/new/choose

The template asks for three things:

- **Link** — the GitHub (or project) URL.
- **Description** — a short, factual one-liner.
- **Category** — where it belongs, as `Main > Sub` (e.g. `OCPP > Libraries`).

A maintainer will run it through the pipeline for you. This is the recommended
path if you don't want to set up the tooling.

## 2. The hands-on way — edit the data and re-render

If you're comfortable running the pipeline, you can prepare the change yourself
and open a pull request.

### Where the data lives

Descriptions and categories are stored in **`classifications.csv`** — the durable,
**committed** source of truth. Its columns are:

| Column        | Meaning                                                                 |
| ------------- | ----------------------------------------------------------------------- |
| `full_name`   | `owner/repo`                                                            |
| `pushed_at`   | last push timestamp (cache key — leave it alone)                        |
| `categories`  | one or more `Main > Sub` entries, pipe-separated (e.g. `Other > Battery`) |
| `description` | the factual one-sentence description shown in the list                  |

- Valid **main** categories come from `CATEGORY_TREE` in `pipeline.py`: `OCPP`,
  `OCPI`, `iso15118`, `OICP`, `EMIP`, `OIOI`, `Eichrecht`, `Other`. **Sub**categories
  are free-form.
- A repo can belong to several categories: separate them with `|`, e.g.
  `Other > Open Charge Map SDK|Other > MCP Server`.

**Do not commit** the generated artifacts `repos.csv`, `repos.enriched.csv`,
`cache_github/`, or `list.txt` — they're git-ignored. Only `classifications.csv`,
`README.md`, and `awesome-ev-charging-projects.md` are meant to be committed.

### Setup

The project is managed with [mise](https://mise.jdx.dev/) (pins Python 3.11.11 and
auto-creates a `.venv`):

```bash
mise trust        # once, after cloning
mise run install  # alias: mise run i
```

A GitHub token is optional; the mise tasks wire one in via `gh auth token` when
the `gh` CLI is authenticated. Without a token, GitHub's unauthenticated rate
limits apply.

### ⚠️ The one thing to remember

`render` reads **`repos.enriched.csv`**, *not* `classifications.csv`. So after
editing the committed CSV you must **re-run `enrich` (without `--refresh`)** to
copy your edits into the enriched CSV, then `render`.

`--refresh` re-runs the classifier for **every** repo and would overwrite your
hand-edited cells — never use it when you want to keep manual edits.

### Common workflows

**Fix a description**

1. Edit the `description` cell for that repo's row in `classifications.csv`.
2. `mise run enrich` — reuses the cache (no LLM call) since `pushed_at` is unchanged.
3. `python pipeline.py render --readme README.md`
4. Commit `classifications.csv` and `README.md`.

**Change or move a category (section)**

- *Option A — edit the data:* change the `categories` cell in
  `classifications.csv`, then `mise run enrich` → `render`.
- *Option B — code override (most robust):* add an entry to `CATEGORY_OVERRIDES`
  in `pipeline.py`, e.g. `"owner/repo": "Other > Battery"`, then just
  `python pipeline.py render --readme README.md`. This is applied at render time,
  needs no `enrich`, and survives `--refresh`.
- To merge near-duplicate subcategory names, add them to `SUBCATEGORY_ALIASES`
  in `pipeline.py` and re-render.

**Add a project**

1. Make it discoverable by `ingest`, via any one of:
   - it already matches one of the `TOPICS` GitHub topics, or
   - it's in one of the curated GitHub Stars lists in `STARRED_LISTS`
     (e.g. `juherr/ev`, `mateogreil/ev-mobility`), or
   - add its `owner/repo` to `ADDITIONAL_REPOS` in `pipeline.py`, or
   - add a GitHub link to it anywhere in `README.md`.
2. `mise run ingest`
3. `mise run enrich` — classifies the new repo and appends it to
   `classifications.csv`.
4. `python pipeline.py render --readme README.md`
5. Commit `classifications.csv` and `README.md`.

Whether a repo lands in the **Selection** block or the collapsed **To refine**
block is decided by a promotion score (the star lists / contributor status), not
by manual ordering.

**Remove a project**

1. Add its `full_name` to `EXCLUDED_REPOS` in `pipeline.py`.
2. `python pipeline.py render --readme README.md` — re-rendering is enough to drop
   it from the README (it's excluded at both ingest and render).
3. Optionally delete its row from `classifications.csv` to keep the cache clean.

## How classification works

New repos — and repos whose upstream `pushed_at` has changed — are classified
automatically by a pluggable LLM-CLI backend, selected with `enrich --classifier`
(`claude` — the default, using the skill agent
[`.claude/agents/repo-classifier.md`](.claude/agents/repo-classifier.md); `codex`;
or `copilot`). It reads the repo's own description and README and produces the
one-line description plus the `Main > Sub` categories. Editing `classifications.csv`
by hand is exactly how you correct or pin that result.

## Golden rules

- ✅ Never edit between the `GENERATED` markers in `README.md`.
- ✅ Only commit `classifications.csv` (plus `README.md` and
  `awesome-ev-charging-projects.md`).
- ✅ Don't pass `--refresh` if you want to keep manual edits.

Hand-authored prose sections of the README (intro, `## Specifications`,
`## Contributing`) are the only parts you may edit directly.
