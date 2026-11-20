# csms.py architecture

Design detail of `csms.py`, moved out of `AGENTS.md`, which keeps a summary,
the commands and the rules an agent must know without opening this file. The
reader-level account of the same catalogue is
[csms-methodology.md](csms-methodology.md); the export contract is
[public-data.md](public-data.md). This file keeps the implementation facts and
links there for what each file, column and feature means.

## Fetch

**Stage 1 — `fetch`.** The OCA certified-products page renders client-side but is backed by a public JSON endpoint: `POST https://openchargealliance.org/wp-json/custom/v1/ajax-loader` with `{id: "299052", paged: N, posts_per_page: 50, post_type: "certificate", filters: [{field: "product-type", value: "Charging Station Management System"}]}`. The endpoint defaults to 6 items per page but honours `posts_per_page`, so asking for 50 turns the sweep into 6 requests instead of 49. `post_json_cached` is the POST counterpart of `github_request_cached` (which is GET-only and picks its cache extension from the `Accept` header), sharing `cache_github/`; its key hashes the payload as well as the URL, since one URL serves every page and filter. Values are whitespace-collapsed and pipe-escaped, dates converted to ISO. Aborts rather than writing a truncated mirror if a page fails.

`cmd_fetch` also refuses, before writing, a mirror under `--min-rows` (default 250) or smaller than the committed one (unless `--allow-shrink`). In `refresh-metadata.yml` that failure is non-blocking: the CSMS steps are dropped and the committed catalogue is restored, while the rest of the monthly refresh goes on.

## Render

**Stage 2 — `render`.** The role and editing rule of each file are in [Dataset architecture](csms-methodology.md#dataset-architecture); `data/csms.json` is written with `--export-dir data` (see [Public JSON export](pipeline-architecture.md#public-json-export--data)). What the code enforces on top:

- `csms-certificates.csv` — one row per certificate, written only by `fetch`.
- `csms.csv` — keyed by a unique `slug`; `product_slugs` fails the render on a missing or duplicate one.
- `csms-features.csv` — one row per `(slug, feature, source_url, note)`, normalised rather than a list column because the sourcing rule applies per feature. `read_features` fails the render on a feature outside `FEATURE_VOCAB`, a slug with no product row, or a missing `source_url`, reporting every problem in one pass.
- `csms.md` — the 9-column directory (`Product | Company | OCPP | OCA certificates | Source available | OCPI | API | Deployment | Status`) injected between `<!-- BEGIN/END GENERATED CSMS -->`; the surrounding prose (intro, four caveats, contributing pointer) is hand-authored.
- `csms-features.md` — the feature annex (`Product | Company | Certified (OCA) | Vendor-documented`) between `<!-- BEGIN/END GENERATED CSMS FEATURES -->`.

## Product identity and merge

Why certificates are grouped per product, and which cases are merged, is in [One row per product, not per certificate](csms-methodology.md#one-row-per-product-not-per-certificate). In the code, `canonical_product(company, designation)` strips the trailing dotted version and applies `PRODUCT_ALIASES`, the hand-maintained rename table; `company_key` does the same job on the vendor side, dropping punctuation and parentheticals while deliberately keeping legal suffixes. `canonical_product` is applied to curated `oca_product` values too, so a contributor may cite either the raw OCA designation or the merged name.

`merge` unions the three: certificates grouped by `(company, canonical product)` lowercased become certified entries; curated product rows matching via `oca_company`/`oca_product` are overlaid onto them; the rest are appended as non-certified; then curated features attach by `slug` through `merge`'s `by_slug` map, since the entry key is `(company, product)` and a curated row may rename either. The slug is also stored on the entry, as the public `id` of `data/csms.json`, so two curated rows landing on one entry fail the render (`_apply_product_row`) rather than let the second take over the first one's id and features. So **certification and source availability are derived, never typed**, and `csms.csv` only needs rows that add information — not the ~200 certified products. A curated row that collides with a certified key merges into it rather than replacing it. `sort_entries` orders by `(display name, company)` — the company tiebreak is what keeps two homonymous products from reshuffling between renders.

## Features

The two kinds of evidence, the certificate legend and the OCPP 1.6 `Full` inference are in [Features: two kinds of evidence](csms-methodology.md#features-two-kinds-of-evidence). In the code, `entry["features_certified"]` (a set) holds what an OCA certificate proves and `entry["features_claimed"]` (name → source URLs) what the vendor documents; nothing ever copies one into the other.

`derive_features` expands the OCA certificate type into the certified set: `CERT_LETTERS` is the registry's legend verbatim, `OCPP16_FULL` our expansion of `Full` on OCPP 1.6. Unknown tokens are collected and make `render` exit non-zero rather than silently emitting an empty cell.

`FEATURE_VOCAB` is the single controlled vocabulary (canonical name → short label, insertion order = display order), shared by both kinds of evidence; `FEATURE_RANK` derives from it. `vocabulary_gaps()` guards the other direction: `CERT_LETTERS` and `OCPP16_FULL` are edited independently, and a name they emit that the vocabulary lacks would surface as a mid-render `KeyError` instead of an actionable message.

Features are derived at render, never stored — `certificate_type` stays raw in the CSV, so fixing the mapping fixes the whole file.

## Column semantics and scope

What each column means is in [Column semantics](csms-methodology.md#column-semantics), and which products get a row in [What gets a row](csms-methodology.md#what-gets-a-row). The implementation behind them: `Product` carries the link to the vendor site or the repo, so there is no `Website` column; the `API` cell reads two `csms.csv` columns, `api` (an API is attested) and `api_docs` (its public documentation URL). `pricing`, `changelog`, `latest_version` and the rest stay in the CSV without a column — and are curated only: `enrich_from_github` no longer derives them, since nothing rendered what it produced.

Company-level rows ([Source precedence](csms-methodology.md#source-precedence)) overlay `COMPANY_FIELDS`, the columns `VENDOR_FIELDS` scopes to the company, onto every entry of that company, certified or not, with `fill_only=True`.

Two traps this design exists to avoid: a commercial product built on an open-source project does not make that project certified (`steve` vs `powerfill` rows), and `enrich_from_github` deliberately ignores the repo's `homepage` field because projects point it at a hosted commercial offering.
