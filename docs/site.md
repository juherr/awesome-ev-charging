# The static site

`site/` holds a fully static [Astro](https://astro.build/) site published at
<https://juherr.github.io/awesome-ev-charging/>. It is an additional
**reading view** over data this repository already publishes: `README.md` and
the canonical CSVs stay authoritative, and the site never adds a fact they do
not hold. No server, no database, no network access and no GitHub API call at
build time.

Pages:

| Path | Source |
| --- | --- |
| `/` | counts derived from the export |
| `/projects/` | `projects.json`, filtered and sorted in the browser |
| `/projects/<owner>/<name>/` | one page per project, `id` lowercased |
| `/csms/` | `csms.json` |
| `/specifications/` | `README.md` section `## Specifications` |
| `/regulations/` | `README.md` section `## Regulation & Standards Bodies` |

The projects directory renders the whole list server-side and works without
JavaScript; a small script filters, sorts and keeps the URL query parameters
(`q`, `protocol`, `category`, `version`, `language`, `host`, `state`, `sort`)
in sync. That logic lives in the pure module `site/src/lib/filter.ts`.

## Data flow

```text
classifications.csv, csms*.csv          canonical, curated
        │  pipeline.py render / csms.py render  --export-dir data
        ▼
data/projects.json, data/csms.json, data/manifest.json
        │  astro build (validated against data/schema/)
        ▼
site/dist/                              static HTML, deployed to Pages
```

The build reads the export from a data directory, `AEC_DATA_DIR`, by default
`../data` relative to `site/`. At build start it validates every file against
`data/schema/*.schema.json` and requires `schema_version` major 1; a missing
or invalid file stops the build with the loader's message. A missing
`projects.json` fails with a pointer to issue
[#98](https://github.com/juherr/awesome-ev-charging/issues/98).

The editorial pages render `README.md` at build time. Its relative links to
vendored files (`ocpp/…`, `img/…`, `csms.md`, …) are rewritten to the file on
GitHub, so the PDFs and schemas are never copied into `dist/`.

The build therefore reads `../README.md` and `../data/schema/`: run it from
`site/` with the whole repository checked out.

## Local commands

The mise tasks in the root `mise.toml` wrap everything. Node is pinned there
(exact 22.x LTS), and `site/` is a separate npm package with its own
`package-lock.json`.

```bash
mise run site-install   # npm ci in site/
mise run site-dev       # dev server; set AEC_DATA_DIR to pick the data
mise run site-build     # static build into site/dist/ from AEC_DATA_DIR
mise run site-check     # astro check + vitest + fixture build + link check
mise run site-fixture   # regenerate site/fixtures/data/ (from the repo root)
```

Until `data/projects.json` is published, build against the fixture:

```bash
AEC_DATA_DIR=fixtures/data mise run site-dev
AEC_DATA_DIR=fixtures/data mise run site-build
```

The path is relative to `site/`, where both tasks run.

## Base path and internal links

The site is a GitHub Pages project site, so `site/astro.config.mjs` sets
`site: 'https://juherr.github.io'`, `base: '/awesome-ev-charging'` and
`trailingSlash: 'always'`.

**Every internal link goes through `url()`** (`site/src/lib/url.ts`), which
prefixes `import.meta.env.BASE_URL`; `projectPath(id)` builds a project page
link. A hard-coded `/projects/` would work in `astro dev` and break once
deployed under the base path.

`site/scripts/check-links.mjs` enforces it after the build. It reads every
`href` and `src` in `dist/` and fails on a document-relative link, a link
outside the base path, or a link to a file the build did not produce (a page
link without its trailing slash included). `site-check` runs it.
It also fails on an absolute URL whose scheme is not `http:`, `https:` or
`mailto:`, and on a path that leaves the base path or `dist/` once its `..`
segments (encoded ones included) are resolved.

## The fixture and its drift test

CI cannot build against `data/` while `projects.json` is missing, and should
not depend on the live export anyway. `site/fixtures/` holds a small committed
`repos.enriched.csv` and the `data/` directory that the **real exporter**
renders from it (`pipeline.py render --export-dir`), with `csms.json` and its
manifest entry copied from `data/`.

`tests/test_site_fixture.py` (run by `mise run test`) re-renders the fixture
and fails when the committed copy differs. After a change to the exporter,
run `mise run site-fixture` and commit the result.

## CI and deployment

- `.github/workflows/site.yml` runs `mise run site-install` and
  `mise run site-check` on pull requests and pushes to `main` that touch
  `site/`, `data/`, `README.md`, `pipeline.py`, `mise.toml` or the workflow.
  Once `data/projects.json` exists, it also runs `mise run site-check-data`:
  a build from `data/` and the link check on that build.
- `.github/workflows/pages.yml` builds from `data/` and deploys on pushes to
  `main` that touch `site/`, `data/`, `README.md`, `mise.toml` or the
  workflow, and on demand (`workflow_dispatch`).

**Deploy gate.** The first job of `pages.yml` checks that
`data/projects.json` exists. While it does not, it emits a notice naming
issue #98 and skips the build and the deploy, so the run is green. The first
real deploy follows the merge of the refresh PR opened by the scheduled run of
2026-12-01, which publishes the file.

**Enabling Pages** (once, by a repository admin): Settings → Pages → Build
and deployment → Source: **GitHub Actions**. The `github-pages` environment
is created on the first deploy.

## Custom domain

Moving to a custom domain changes the URL scheme, not the code:

- `site` in `astro.config.mjs` becomes the domain, and `base` becomes `/`
  (or is removed). `url()` follows `BASE_URL`, so no link changes; the link
  checker takes the base as its second argument and must follow it.
- Canonical links, the sitemap and Open Graph URLs derive from `site`, so
  they move with it.
- Set the domain in Settings → Pages. With a GitHub Actions deploy, "no
  `CNAME` file is created, and any existing `CNAME` file is ignored and is not
  required"
  ([Managing a custom domain](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)),
  so the artifact needs none. Configure the DNS records, then enable "Enforce
  HTTPS".
