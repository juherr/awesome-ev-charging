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

👉 <https://github.com/juherr/awesome-ev-charging/issues/new/choose>

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

| Column        | Meaning                                                                   |
| ------------- | ------------------------------------------------------------------------- |
| `full_name`   | `owner/repo`                                                              |
| `pushed_at`   | last push timestamp (cache key — leave it alone)                          |
| `categories`  | one or more `Main > Sub` entries, pipe-separated (e.g. `Other > Battery`) |
| `description` | the factual one-sentence description shown in the list                    |

- Valid **main** categories come from `CATEGORY_TREE` in `pipeline.py`: `OCPP`,
  `OCPI`, `iso15118`, `OICP`, `EMIP`, `OIOI`, `Eichrecht`, `Other`. **Sub**categories
  are free-form.
- A repo can belong to several categories: separate them with `|`, e.g.
  `Other > Open Charge Map SDK|Other > MCP Server`.

**Do not commit** the generated artifacts `repos.csv`, `repos.enriched.csv`,
`cache_github/`, or `list.txt` — they're git-ignored. The files meant to be
committed are `classifications.csv`, `README.md`, `legacy-projects.md`,
`csms.csv` and `csms-certificates.csv` (plus `csms.md`).

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

#### Fix a description

1. Edit the `description` cell for that repo's row in `classifications.csv`.
2. `mise run enrich` — reuses the cache (no LLM call) since `pushed_at` is unchanged.
3. `python pipeline.py render --readme README.md`
4. Commit `classifications.csv` and `README.md`.

#### Change or move a category (section)

- *Option A — edit the data:* change the `categories` cell in
  `classifications.csv`, then `mise run enrich` → `render`.
- *Option B — code override (most robust):* add an entry to `CATEGORY_OVERRIDES`
  in `pipeline.py`, e.g. `"owner/repo": "Other > Battery"`, then just
  `python pipeline.py render --readme README.md`. This is applied at render time,
  needs no `enrich`, and survives `--refresh`.
- To merge near-duplicate subcategory names, add them to `SUBCATEGORY_ALIASES`
  in `pipeline.py` and re-render.

#### Add a project

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

#### Remove a project

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

## Adding or correcting a CSMS entry

[`csms.md`](csms.md) is a separate deliverable with its own script, `csms.py`.
It lists Charging Station Management Systems as products rather than
repositories, with their OCA certification status and certified feature
profiles. Its table also lives between `GENERATED` markers — **never edit it by
hand**.

Two data files feed it:

| File | Nature | Rule |
| --- | --- | --- |
| `csms-certificates.csv` | Generated mirror of the [OCA certified products registry](https://openchargealliance.org/certified-companies/) | Never edit it. Refresh with `python csms.py fetch`; corrections belong upstream with the OCA |
| `csms.csv` | Curated, one row per product | No script ever writes it. This is where you contribute |

To add a product that is **not** OCA-certified (open source or commercial), add
a row to `csms.csv`. To attach facts to an **already certified** product, add a
row and fill `oca_company` / `oca_product` with the exact strings from
`csms-certificates.csv` — the render merges the two. A mismatch prints a
warning rather than failing, since the OCA does rename and withdraw entries.

For facts that belong to the **company** rather than to one product — website,
founding year, HQ — fill `oca_company` and leave `oca_product` empty. The row
then applies to every product that company has certified, so one row covers a
vendor with several listings.

`changelog` holds the product's release-notes URL; the rendered *Latest
version* cell links to it. Open-source entries get their GitHub releases page
automatically, so only fill it for commercial products.

The hand-authored prose in `csms.md` quotes a few figures from the registry
(certificate counts, the share of Korean certificates, how many products are
certified on both OCPP versions). Nothing regenerates those — re-check them
after a `csms.py fetch` that moves the numbers.

Then:

```bash
mise run csms   # fetch + render, or run the two csms.py stages separately
```

Rules specific to this file:

- **Every curated value needs a URL in that row's `sources` column.** If you
  cannot cite it, leave the cell empty — an empty cell reads as *unknown*, and
  that is the honest answer. The one exception is `contributor:<name>`, for a
  fact a maintainer knows from their own research but cannot cite publicly;
  say so in `notes` too, and replace it with a URL when one turns up.
- **Do not record private evaluation data here.** No sales contacts or personal
  email addresses, no prices obtained under a quote or an NDA, no subjective
  verdicts on a vendor's reputation or product quality. This file is a public,
  factual catalogue; keep commercial assessments in your own notes.
- **Never set a certification by hand.** `OCA-certified` is derived from the
  registry. A commercial product built on an open-source project does not make
  that project certified — see the `steve` and `powerfill` rows for the worked
  example.
- **Spotted the same product twice?** The registry certifies a product *and
  software version*, so one platform can appear under several designations.
  A trailing dotted version is stripped automatically; anything else needs an
  entry in `PRODUCT_ALIASES` in `csms.py`. Only merge when the certificates
  clearly describe one platform — a vendor may genuinely ship two CSMS.
- **`api` is `Y` only for documentation reachable without an account.** Put the
  spec URL in `api_docs`. A login-gated developer portal leaves the cell empty.
- **`pricing` uses one of four values**, with the page in `pricing_url`:
  `Price list` (figures published), `On request` (pricing page quotes nothing),
  `Published` (page exists, contents unverified), `Free (self-hosted)`
  (open-source software).

## Golden rules

- ✅ Never edit between the `GENERATED` markers in `README.md` or `csms.md`.
- ✅ Only commit `classifications.csv` and `csms.csv` (plus the generated
  `README.md`, `legacy-projects.md`, `csms-certificates.csv` and `csms.md`).
- ✅ Don't pass `--refresh` if you want to keep manual edits.
- ✅ No source, no value — leave curated CSMS cells empty rather than guessing.

Hand-authored prose sections of the README (intro, `## Specifications`,
`## Contributing`) are the only parts you may edit directly, along with the
prose around the table in `csms.md`.
