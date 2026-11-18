# Public data export

The project listing and the CSMS catalogue are also published as JSON under
`data/`, so a consumer (a static site, a script, a notebook) can reuse them
without parsing the Markdown. This document is the contract for those files.

Building on them needs no network access, no GitHub token and no LLM: every
value is already resolved in the committed files.

## Files

| File | Content | Schema |
| --- | --- | --- |
| `data/projects.json` | The project listing: every repository the pipeline renders, in all three curation blocks | [`projects.schema.json`](../data/schema/projects.schema.json) |
| [`data/csms.json`](../data/csms.json) | The CSMS catalogue: OCA-certified and curated products | [`csms.schema.json`](../data/schema/csms.schema.json) |
| [`data/manifest.json`](../data/manifest.json) | Checksums, record counts and input checksums of the two payloads | — |

`data/projects.json` is **not published yet** (issue #98). It is rendered
from `repos.enriched.csv`, which only `enrich` produces and which is not
committed. The monthly refresh workflow writes it, so the first refresh after
this export landed publishes it. Until then, the projects queries below are
illustrative and were checked against a fixture render.

## How the files are generated

The files are generated and committed. **Never edit them by hand**: change the
canonical inputs and re-render.

```bash
python pipeline.py render --readme README.md --export-dir data   # projects.json
python csms.py render --export-dir data                          # csms.json
```

Each command writes its payload and refreshes its own entry in
`data/manifest.json`, leaving the other entry as it was. The inputs are:

- `projects.json`: `repos.enriched.csv` (the output of `ingest` and `enrich`,
  with `classifications.csv` as the classifier's committed cache), plus the
  overrides in `pipeline.py` (`CATEGORY_OVERRIDES`, `REPO_OVERRIDES`).
- `csms.json`: `csms-certificates.csv` (the OCA registry mirror), `csms.csv`
  and `csms-features.csv` (curated), with the rules in `csms.py`. It reads
  nothing from GitHub, so it can be reproduced offline from those three files.

The monthly refresh (`.github/workflows/refresh-metadata.yml`) runs both
renders and commits `data/` in the same pull request as the Markdown. The test
suite checks the committed `csms.json` and its manifest entry against a fresh
export of the committed CSVs and validates it against its schema. The projects
export is validated on a fixture render; once `data/projects.json` is
committed, the suite also validates it against its schema, checks that its
`projects` manifest entry records its SHA-256 and record count (neither may
exist without the other), and checks that its curation blocks agree with
`README.md` and `legacy-projects.md`.

## Unknown is never "no"

`null`, an empty list, or a missing entry means **unknown**: nobody verified
it. It never means the property is absent. In particular:

- `source_available`, `ocpi`, `iso15118`, `eichrecht` and `api` in
  `csms.json` are `true` or `null`, never `false`.
- A feature missing from `features_certified` or `features_documented` is
  unknown, not unsupported.
- `ocpp_versions` / `ocpi_versions` in `projects.json`, and `ocpp_versions`
  in `csms.json`, are `null` when no version is known, never `[]`: the
  schemas require at least one item.
- `deprecated` in `projects.json` is `true` or `null`, never `false`: a
  description without deprecation wording does not show the project is
  maintained.
- `dormant` in `projects.json` is `null` when no last commit could be read
  (an empty Codeberg repository, a default branch that answered 404) and the
  repository is not archived.

Do not "complete" the data by turning `null` into `false`.

## `projects.json`

```json
{"schema_version": "1.0", "projects": [ … ]}
```

One record per repository, sorted by `id`.

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | string | The lowercased `full_name`. Stable and unique; use it as the key |
| `full_name` | string | `owner/name` as the host spells it |
| `url` | string or null | The canonical URL, after `REPO_OVERRIDES` (a repo that moved off GitHub points at its new host) |
| `host` | `github`, `codeberg`, `other` or null | Derived from `url`. `other` is a host the pipeline cannot read (GitLab, self-hosted), set through an override |
| `description` | string or null | The listing's one-line description (a `REPO_OVERRIDES` text, else the classifier's summary, else the host's own description) |
| `primary_category` | object or null | The first entry of `categories`: the section the Markdown lists the repo under |
| `categories` | array | Every `{main, sub}` facet, in order. Protocol categories come before `Other`, so the first one is the primary. `sub` is `null` for a bare main category. Empty when the repo has none; the README's "Uncategorized" bucket never appears here |
| `ocpp_versions`, `ocpi_versions` | non-empty array or null | Versions detected in the README, in file order. `null` when none was detected |
| `language` | string or null | The host's primary language |
| `license` | string or null | The licence name; `null` when none was detected (Codeberg repos included) |
| `stars`, `forks` | integer or null | Counts at the last refresh |
| `archived` | boolean or null | The host's archived flag |
| `dormant` | boolean or null | Raw activity signal: no push for 365 days, **or** archived. `null` when `pushed_at` is unknown and the repo is not archived |
| `deprecated` | `true` or null | The description flags the project as deprecated or unmaintained. `null` otherwise, never `false` |
| `curation` | `selection`, `dormant` or `to_refine` | The block the project renders in (see below) |
| `pushed_at` | string or null | Last commit, ISO 8601 UTC. Decides `dormant` |
| `updated_at` | string or null | Last known modification, metadata edits included. Not used for dormancy |
| `topics` | array | The host's topics, sorted |
| `discovered_via` | array | How ingest found the repo (`topic`, `manual`, `readme`, `starred-list`, `codeberg`), sorted |

### `curation` versus the raw flags

`curation` is the editorial verdict, and the Markdown is rendered from the same
function, so the two cannot disagree:

- `selection`: curated and active. Listed in `README.md`.
- `dormant`: curated, but `dormant` or `deprecated`. Listed in
  `legacy-projects.md`.
- `to_refine`: not curated (in no maintainer's star list, not contributed to).
  Listed in `legacy-projects.md`, whatever its activity.

So an uncurated dormant repository is `to_refine`, not `dormant`, and a
curated one whose `dormant` is `null` stays in `selection`. Read
`dormant`, `archived` and `deprecated` for the raw signals, and `curation` for
the listing.

## `csms.json`

```json
{"schema_version": "1.0", "products": [ … ]}
```

One record per product, sorted by `id`.

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | string | The curated `slug` from `csms.csv`; otherwise derived from the company and the canonical product name, so a respelt company name (punctuation, a parenthetical) or a version bump keeps it. A real rename changes a derived id; a curated slug survives it |
| `name`, `company` | string / string or null | Display name and vendor |
| `oca_company_url` | string or null | The vendor's page on the OCA registry |
| `website` | string or null | The product's or the vendor's site (a company-level row in `csms.csv` fills it for every product of that company) |
| `repo`, `repo_url` | string or null | The curated GitHub `owner/name` and its URL |
| `source_available` | `true` or null | A public repository was found. `null` is unverified |
| `ocpp_versions` | non-empty array or null | Certified versions plus the versions the vendor claims (`ocpp_claimed`). Not a certification list: read `certificates` for that |
| `certificates` | array | Every OCA certificate: `number`, `ocpp_version`, the raw `type` (e.g. `Core + S + C`), `software_version`, registration `date`, `url` |
| `features_certified` | array | Features an OCA certificate proves, derived from the certificate types |
| `features_documented` | array | Features the vendor documents, each `{feature, source_urls}` |
| `ocpi`, `iso15118`, `eichrecht` | `true` or null | Stated by a source. `ocpi` is also `true` when an `OCPI Roaming` feature is documented |
| `api` | `true` or null | An API exists (documentation possibly login-gated). Also `true` when `api_docs` is set |
| `api_docs` | string or null | URL of public API documentation |
| `pricing`, `pricing_url`, `changelog`, `hq_country`, `hq_city`, `company_founded`, `first_release`, `latest_version`, `latest_version_date`, `license`, `deployment`, `status`, `notes` | string or null | Curated text from `csms.csv`, copied as written |
| `sources` | array | Where the curated values come from, in file order: an `http(s)://` URL, or `contributor:<login>` (see below) |

Most `sources` entries are URLs. The one other form is `contributor:<login>`,
a fact a maintainer (`<login>` is their GitHub login) knows from their own
research but cannot cite publicly; the record's `notes` say so. It is not a
link: render it as text, or as a link to `https://github.com/<login>` if you
want one, never as a URL on its own. Treat any other value without a scheme
the same way.

### Certified versus documented features

The two lists are two kinds of evidence and are never merged. A feature may
appear in both.

- `features_certified` is what an OCA certificate proves. One expansion is
  ours, not OCA's: an OCPP 1.6 `Full` certificate is read as the six OCPP 1.6
  feature profiles. [`csms-methodology.md`](csms-methodology.md) explains it.
- `features_documented` is what the vendor's own documentation states, with a
  source URL for each claim. It is not a certification.

Both use the controlled vocabulary of `FEATURE_VOCAB` in `csms.py`.

## Determinism

The same inputs produce byte-identical files:

- records are sorted by `id`, and every list inside a record has a fixed
  order (sorted, or the input's order where that order means something:
  `categories`, `sources`);
- JSON is written with sorted keys, a two-space indent, UTF-8 without
  escaping, and a trailing newline;
- nothing time-dependent is written: no generation timestamp, no git revision.

A diff of `data/` between two commits therefore shows only real changes.

## `manifest.json`

```json
{
  "schema_version": "1.0",
  "payloads": {
    "csms": {
      "file": "csms.json",
      "sha256": "…",
      "records": 285,
      "inputs": {"csms-certificates.csv": "…", "csms-features.csv": "…", "csms.csv": "…"}
    },
    "projects": {"file": "projects.json", "sha256": "…", "records": "…", "inputs": {"repos.enriched.csv": "…"}}
  }
}
```

The `projects` entry appears once `data/projects.json` is published (#98).

- `file` is relative to `data/`; `sha256` and `records` describe that payload.
- `inputs` maps each input path, relative to the repository root, to its
  SHA-256. The CSMS inputs are committed, so a consumer can check them. The
  projects input, `repos.enriched.csv`, is git-ignored: its checksum is
  provenance only and cannot be verified from the repository.
- There is no timestamp. The commit that changed the file dates it.

## Versioning

`schema_version` follows `MAJOR.MINOR`, and both payloads and the manifest
share it.

- A new optional field is a **minor** bump (`1.1`).
- Removing or renaming a field, changing its type, or changing what a value
  means is a **major** bump (`2.0`).

The schema files live next to the data and change in the same commit. The
schemas are strict (`additionalProperties: false`, `schema_version` pinned to
one value), so validate a payload against the schema from the **same commit**
as the data, not a copy cached earlier. In your own code, ignore fields you do
not know, so a minor bump does not break you.

To pin a version, read the files from a tag or a commit SHA rather than
`main`.

### Id stability

An `id` is not guaranteed for the lifetime of a record, and its changes do not
bump `schema_version`: they change data, not the format.

- `projects.json`: the id is the lowercased `full_name`, so it changes when a
  repository is renamed or transferred.
- `csms.json`: a product with no curated row carries an id derived from its
  company and product name. When a curated row is later added to
  `csms.csv` for that product, its id **switches to the row's `slug`**, and the
  derived id disappears from the file. `python csms.py render --export-dir`
  compares the new file with the one it replaces and prints a warning listing
  every id that disappears, whether the product was renamed, re-slugged or
  removed. If you key URLs or storage on `id`, keep a redirect from the old id
  when it vanishes.

## Sample queries

With [`jq`](https://jqlang.org/), from the repository root:

```bash
# CSMS products with a public repository, and its URL
jq -r '.products[] | select(.source_available == true) | "\(.name)\t\(.repo_url // "")"' data/csms.json

# Products holding at least one OCPP 2.0.1 certificate
jq -r '.products[] | select(any(.certificates[]; .ocpp_version == "2.0.1")) | .name' data/csms.json

# Smart Charging documented by the vendor but not proven by a certificate
jq -r '.products[]
  | select((.features_documented | map(.feature) | index("Smart Charging"))
           and ((.features_certified | index("Smart Charging")) | not))
  | .name' data/csms.json

# Check a payload against the manifest
jq -r '.payloads.csms.sha256' data/manifest.json; shasum -a 256 data/csms.json
```

Illustrative, until `data/projects.json` is published (#98):

```bash
# The README selection, with the OCPP versions of each OCPP project
jq -r '.projects[] | select(.curation == "selection" and .primary_category.main == "OCPP")
  | "\(.full_name)\t\(.ocpp_versions // [] | join(", "))"' data/projects.json

# Every repository hosted on Codeberg
jq -r '.projects[] | select(.host == "codeberg") | .url' data/projects.json

# Any project with a given facet, primary or not
jq -r '.projects[] | select(any(.categories[]; .main == "Other" and .sub == "Home automation"))
  | .full_name' data/projects.json
```
