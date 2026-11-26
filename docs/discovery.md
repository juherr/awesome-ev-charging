# External-list discovery

`discovery.py` reads other community lists (forks of this list, other awesome
lists), compares every resource they link with the catalogue, and writes a
Markdown review report. `AGENTS.md` keeps the summary and the command; this
page holds the rules.

## What it does and does not do

It does:

- fetch each configured source and extract the GitHub repositories and the
  other http(s) URLs it links;
- resolve each repository through the GitHub API, so a renamed or transferred
  repository is compared under its current name;
- give each candidate one status against the catalogue, and keep which sources
  link it;
- write one report, the same bytes for the same inputs;
- with `--issue-body` and `--workflow-url`, also write the body of the rolling
  issue (see [Workflow and artifact](#workflow-and-artifact)).

It never writes curated data: not `classifications.csv`, `README.md`,
`legacy-projects.md`, the CSMS files nor `data/`. Its only outputs are the
report, the issue body when asked for, and the disposable `cache_github/`.
The weekly workflow opens or edits one issue with that body, and nothing
else: no commit, no pull request, no comment. Nothing it finds reaches the
catalogue without a review, through the usual workflows below.

Like `csms.py`, it is a separate script that imports `pipeline` for the HTTP
cache, the README fetch and the README scan. Do not fold it into
`pipeline.py`.

## Running it

```bash
mise run discover   # writes discovery-report.md (git-ignored)
python discovery.py --sources discovery-sources.toml --report <path> [--token T]
#   [--issue-body <path> --workflow-url <url>]: also write the issue body
```

Run it from the repository root: it reads the catalogue files from the current
directory. Without `--token`, GitHub's unauthenticated rate limit applies, and
every source repository costs two API requests (its README and its lookup) and
every linked repository one (cached for the usual TTL in `cache_github/`).

| Exit code | Meaning |
| --- | --- |
| 0 | Report written, at least one source read |
| 1 | Every source failed; the report is still written and lists the failures |
| 2 | Configuration error: invalid `--sources` file, or a catalogue file missing (not run from the repository root) |

## Sources

`discovery-sources.toml` holds one `[[sources]]` table per list. Adding a
source is an edit of that file, with no code change:

```toml
[[sources]]
name = "andreibesleaga/awesome-ev-charging"   # unique, shown in the report
repo = "andreibesleaga/awesome-ev-charging"   # a GitHub repository: its README

[[sources]]
name = "some-list"
url = "https://example.org/list.md"           # or a raw Markdown file
```

Each table takes a non-empty, unique `name` and exactly one of `repo`
(`owner/name`) or `url` (`http(s)://`); any other key is an error. A `name`
may hold only letters, digits, `_`, `.`, `/`, `-` and spaces, since it is
printed in a table and in code spans of the report. A `repo` source is read
through the GitHub API with the token; a `url` source is fetched without any
authentication header, whatever its host, bypassing the HTTP cache and with a
30-second timeout (`URL_TIMEOUT`).

A source that cannot be read is listed under "Failed sources" and the run goes
on with the others:

- `not found` — the repository or its README is gone, or the URL answers 404
  or 200 with an empty body;
- `fetch failed` — rate limit, server error, timeout or network failure.

A failed source never reads as a list that links nothing.

## Extraction

- **GitHub repositories**: the same rules as the README scan of `ingest`
  (`pipeline.repo_names_from_text`): a `/tree/...` or `/blob/...` link folds
  to its repository, non-repository paths are skipped, `.git` is stripped.
  Images, gists (`gist.github.com`) and uploads (`github.com/user-attachments`)
  are skipped too: they are not repositories.
- **Other URLs**: every http(s) link that is not on GitHub (`github.com`, its
  asset and `githubusercontent.com` hosts), skipping images and badge hosts
  (`BADGE_HOSTS`). A URL is normalized before comparison: scheme and host in
  lower case, fragment dropped, tracking parameters dropped (`utm_*`,
  `fbclid`, `gclid`, `mc_cid`, `mc_eid`, `ref`, `ref_src`), the remaining
  parameters sorted, one trailing `/` and the punctuation Markdown leaves
  after a link (`).,;`) stripped. `www.` is kept.

Candidates are deduplicated across sources, case-insensitively, and each
keeps the sorted list of the sources that link it, plus the source line that
links it (the list's own words about it).

## Statuses

The catalogue is, for repositories: the keys of `classifications.csv`, the
repositories linked in `README.md`, `legacy-projects.md` and `csms.md`,
`ADDITIONAL_REPOS` and `CODEBERG_REPOS`. For other URLs: every URL in those
three Markdown files, plus the Codeberg page of each `CODEBERG_REPOS` entry.

Each linked repository is looked up (`GET /repos/{owner}/{name}`), which
follows renames and transfers. Names that resolve to the same repository merge
into one candidate, keeping all the linked names (aliases) and all the
sources. The first matching rule gives the status:

1. **excluded** — an alias or the current name is in `EXCLUDED_REPOS`
   (reason `EXCLUDED_REPOS`), is a configured source repository under its
   configured or current name (`discovery source`: a list never recommends
   itself; a failed lookup of the source keeps only the configured name), or
   has a deprecated classification (`deprecated`).
2. **unavailable** — the lookup answered 404 (`not found`, or `not found
   (tracked)` when an alias is in the catalogue), or failed otherwise (rate
   limit, server error, network) for a name the catalogue does not hold
   (`lookup failed`).
3. **existing** — the catalogue holds the repository under the same name: the
   current name is tracked and every alias equals it, or the lookup failed
   transiently but an alias is tracked.
4. **changed** — the catalogue holds it under another name. Either the current
   name is tracked and the source links an old name (stale in the `source`),
   or an alias is tracked under a name the repository no longer has (stale in
   the `catalogue`). The catalogue can also be stale when the source links
   only the current name: a repository that would be `new` has its related
   tracked names (same short name, another owner) looked up too, and one that
   resolves to it makes it `changed`, stale in the `catalogue`. This only
   catches a rename or transfer that keeps the short name; a related name
   whose lookup fails leaves the repository `new`, with that name listed as
   related.
5. **new** — anything else.

Other URLs are `existing` when their normalized form is in the catalogue,
`new` otherwise.

## Report

The report has no timestamp and sorts everything (statuses in a fixed order,
then names case-insensitively), so two runs on the same inputs give the same
bytes and a re-run adds nothing to review. Sections:

- **Summary**: counts per status for repositories and other URLs, then per
  source.
- **Failed sources**: name and reason.
- **New**: per repository, its canonical link, sources, description, archived
  flag, last push, licence (SPDX id), related tracked projects (tracked
  repositories with the same name under another owner, a possible duplicate)
  and the line of each source that links it. A value GitHub does not give is
  left blank: blank means unknown, never "no". New other URLs follow, with
  their sources.
- **Changed**: `old -> new`, with the stale side.
- **Unavailable** and **Excluded**: name, reason and sources.
- **Existing**: counts only.

## Workflow and artifact

`.github/workflows/discovery.yml` runs every Monday at 06:00 UTC and on
`workflow_dispatch`. It appends the report to the job summary, uploads it as
the `discovery-report` artifact, and keeps one rolling issue up to date. These
steps also run when every source failed, so the failures can be read while the
job ends red. It opens no pull request.

The rolling issue is the open issue labelled `discovery-report` (the oldest
one if there are several). The workflow creates the label when it is missing,
and the issue when none is open, titled « Discovery report: candidates from
external lists ». Its body, written by `discovery.py --issue-body <path>
--workflow-url <url>`, is a hidden `<!-- discovery-report -->` marker, a link
to the workflow (each run's `discovery-report` artifact holds the full
report), then the report. Nothing in it is specific to a run, so an unchanged
report gives an unchanged body. When the report is longer than GitHub's
65,536 characters, the body keeps the summary and the `New`, `Changed` and
`Unavailable` sections, whole while they fit, cut on a line boundary
otherwise, and ends with a line pointing at the workflow's artifacts for the
full report.

The issue is created once, then its body is edited only when it differs from
the new one; the workflow never comments, closes or reopens it. Closing it is
how a reviewer marks the report as handled: the next run opens a new one.
Mentions and issue references in external metadata (a repository description,
say) are neutralised with a zero-width space: after `@`, `#` and the `GH` of
`GH-1`, and before the number of an issue, pull request or discussion URL. So
the bot pings no one and links no other issue. The job's token holds
`contents: read` and `issues: write`, nothing more.

## Acting on the report

| Status | What to do |
| --- | --- |
| `new` repository | Review it; to list it, follow the `add-project` skill (`.claude/skills/` or `.agents/skills/`) |
| `new` URL | Decide whether it belongs in the hand-authored prose of `README.md`, and add it there by hand |
| `changed`, stale in the `catalogue` | Update the old name where the catalogue holds it (`ADDITIONAL_REPOS`, a README link, ...) and re-run the pipeline |
| `changed`, stale in the `source` | Nothing to do here: the catalogue is current |
| `unavailable`, `not found (tracked)` | Check the catalogue entry: the repository is gone or private; drop or replace it |
| `unavailable`, `not found` or `lookup failed` | Nothing to add; re-run later for `lookup failed` |
| `excluded` | Nothing to do: the earlier decision stands |
| `existing` | Nothing to do |
| Failed source | Check the entry of `discovery-sources.toml`; remove a source that is gone for good |

## Deviations from issue #120

- The rolling issue came later, with #126 (see
  [Workflow and artifact](#workflow-and-artifact)).
- No suggested category for a new candidate: the classifier runs when the
  candidate is added through `add-project`. Tracked in #140.
- No comparison across several lists: the configuration has one source so
  far. Tracked in #139.
