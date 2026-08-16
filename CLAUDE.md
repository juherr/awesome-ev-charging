# CLAUDE.md

@AGENTS.md

The import above is the shared guidance — repository layout, commands,
`pipeline.py` and `csms.py` architecture, conventions. **Read it first.** This
file adds only what is specific to Claude Code, so anything you learn that holds
for every agent belongs in `AGENTS.md`, not here.

## Skills

Two maintenance workflows are packaged as skills in `.claude/skills/`. Prefer
them over improvising the steps — they encode decisions a plain re-run gets
wrong:

- **`add-project`** — add, list or feature a repo in the generated README
  listing, including handling an "Add a link" issue. Covers making the repo
  discoverable, `ingest → enrich → render`, pinning the category when the
  classifier diverges, and closing the issue.
- **`refresh-metadata`** — the periodic refresh of the listing's stars, forks
  and dormancy signals, with no repo to add. It handles the cache-versus-TTL
  decision (whether to clear `cache_github/` first).

`.agents/skills/` holds harness-neutral copies of both. Edit one and port the
change to the other.

## The default classifier is `claude`

`enrich` shells out to the `claude` CLI unless `--classifier` says otherwise, so
running `mise run enrich` from inside a Claude Code session spawns a **nested,
non-interactive** `claude -p` per repo to classify. That is expected — but it
means the run is billed per repo, and a session-level interrupt does not
propagate to the child. Prefer `--classifier copilot` in CI, which is what
`.github/workflows/refresh-metadata.yml` uses.

The role and output contract for that backend live in
`.claude/agents/repo-classifier.md`. `AGENTS.md` lists the three other places
the same contract is duplicated — change one, change all of them.

## Repository-specific tool notes

- The pinned Python lives in mise's venv at `.venv/`. It has no `pip`; use
  `uv pip install --python .venv/bin/python …` or the mise tasks.
- `python` on `PATH` is not the project interpreter unless mise has activated
  the directory. `.venv/bin/python` always is.
