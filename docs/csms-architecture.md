# csms.py architecture

Design detail of `csms.py`, moved out of `AGENTS.md`, which keeps a summary,
the commands and the rules an agent must know without opening this file. The
reader-level account of the same catalogue is
[csms-methodology.md](csms-methodology.md); the export contract is
[public-data.md](public-data.md).

## Fetch

**Stage 1 — `fetch`.** The OCA certified-products page renders client-side but is backed by a public JSON endpoint: `POST https://openchargealliance.org/wp-json/custom/v1/ajax-loader` with `{id: "299052", paged: N, posts_per_page: 50, post_type: "certificate", filters: [{field: "product-type", value: "Charging Station Management System"}]}`. The endpoint defaults to 6 items per page but honours `posts_per_page`, so asking for 50 turns the sweep into 6 requests instead of 49. `post_json_cached` is the POST counterpart of `github_request_cached` (which is GET-only and picks its cache extension from the `Accept` header), sharing `cache_github/`; its key hashes the payload as well as the URL, since one URL serves every page and filter. Values are whitespace-collapsed and pipe-escaped, dates converted to ISO. Aborts rather than writing a truncated mirror if a page fails.

## Render

**Stage 2 — `render`.** Five files, one rule each, plus `data/csms.json` with `--export-dir data` (see [Public JSON export](pipeline-architecture.md#public-json-export--data)):

- `csms-certificates.csv` — generated, one row per certificate (~293). Never hand-edited.
- `csms.csv` — curated, one row per product (or per company): **the canonical dataset**. **No script ever writes it.** Every curated value needs a URL in its `sources` column. Keyed by a unique `slug`; `product_slugs` fails the render on a missing or duplicate one. It deliberately keeps columns the tables no longer show (HQ, founding year, pricing, licence, ISO 15118, Eichrecht, release history) — the view shrank, the dataset did not.
- `csms-features.csv` — curated, one row per `(slug, feature, source_url, note)`. Normalised rather than a list column, because the sourcing rule applies per feature. `read_features` fails the render on a feature outside `FEATURE_VOCAB`, a slug with no product row, or a missing `source_url`, reporting every problem in one pass.
- `csms.md` — the 9-column directory (`Product | Company | OCPP | OCA certificates | Source available | OCPI | API | Deployment | Status`) injected between `<!-- BEGIN/END GENERATED CSMS -->`; the surrounding prose (intro, four caveats, contributing pointer) is hand-authored. Detailed methodology lives in `docs/csms-methodology.md`, outside the deliverable.
- `csms-features.md` — the feature annex (`Product | Company | Certified (OCA) | Vendor-documented`) between `<!-- BEGIN/END GENERATED CSMS FEATURES -->`.

## Product identity and merge

`canonical_product(company, designation)` decides product identity before grouping: it strips a trailing dotted version (`eBAB Server v1.6` / `v1.6.1` → one product; a dot is required so `MON-CSMS-V10` survives) and applies `PRODUCT_ALIASES`, a hand-maintained table for platforms the registry renamed between certificates (Driivz, NEC, KEPCO KDN, Elvo, I-Charge Solutions). `company_key` does the same job on the vendor side, dropping punctuation and parentheticals so `Shenzhen Infypower Co. Ltd` / `Co., Ltd` and `Instituto Tecnológico de la Energía` with and without `(ITE)` group as one company; legal suffixes are deliberately kept. Together they collapse 11 duplicates. `canonical_product` is applied to curated `oca_product` values too, so a contributor may cite either the raw OCA designation or the merged name. Only merge when the certificates clearly describe one platform — vendors do ship several CSMS, and some registry entries are hardware model numbers misfiled under the CSMS product type.

`merge` unions the three: certificates grouped by `(company, canonical product)` lowercased become certified entries; curated product rows matching via `oca_company`/`oca_product` are overlaid onto them; the rest are appended as non-certified; then curated features attach by `slug` through `merge`'s `by_slug` map, since the entry key is `(company, product)` and a curated row may rename either. The slug is also stored on the entry, as the public `id` of `data/csms.json`, so two curated rows landing on one entry fail the render (`_apply_product_row`) rather than let the second take over the first one's id and features. So **certification and source availability are derived, never typed**, and `csms.csv` only needs rows that add information — not the ~193 certified products. A curated row that collides with a certified key merges into it rather than replacing it. `sort_entries` orders by `(display name, company)` — the company tiebreak is what keeps two homonymous products from reshuffling between renders.

## Features

**Two kinds of feature evidence, never merged.** `entry["features_certified"]` (a set) is what an OCA certificate proves; `entry["features_claimed"]` (name → source URLs) is what the vendor documents. `csms-features.md` renders them in separate columns, and a feature legitimately appears in both — the reverse promotion never happens.

`derive_features` expands the OCA certificate type into the certified set. `CERT_LETTERS` is the verbatim legend from the registry's own `Certificate type` filter (`S` Advanced Security, `L` Local Authorization List Management, `C` Smart Charging, `D` Advanced Device Management, `R` Reservation, `U` Advanced User Interface, `I` ISO 15118 Support). `OCPP16_FULL` — the expansion of `Full` on OCPP 1.6 into the six OCPP 1.6 feature profiles — is **our inference, not an OCA statement**, and `docs/csms-methodology.md` says so. `Subset`/`Family` are scope qualifiers and yield no features. Unknown tokens are collected and make `render` exit non-zero rather than silently emitting an empty cell; the monthly workflow also fails if the mirror drops below 250 rows.

`FEATURE_VOCAB` is the single controlled vocabulary (canonical name → short label, insertion order = display order), shared by both kinds of evidence so they stay comparable; `FEATURE_RANK` derives from it. Curated names outside it fail the render. `vocabulary_gaps()` guards the other direction: `CERT_LETTERS` and `OCPP16_FULL` are edited independently, and a name they emit that the vocabulary lacks would surface as a mid-render `KeyError` instead of an actionable message.

Features are derived at render, never stored — `certificate_type` stays raw in the CSV, so fixing the mapping fixes the whole file.

## Column semantics and scope

Column semantics worth not re-deriving: **`Product`** carries the link to the vendor site (or the repo) — there is no separate `Website` column. **`Source available`** is `Y` or empty, **never `N`**: we check whether a repository exists, not whether one is absent. **`API`** separates two facts — `api` means a reliable source attests an API exists (login-gated documentation included), `api_docs` means that documentation is public, so a documented-but-gated API is an unlinked `Y` and an empty cell is *unverified*. **`OCPI`** is `Y` when the `ocpi` column says so or a curated `OCPI Roaming` feature exists, linked to the feature's source. `pricing`, `changelog`, `latest_version` and the rest stay in the CSV without a column — and are curated only: `enrich_from_github` no longer derives them, since nothing rendered what it produced.

A curated row with `oca_company` set and `oca_product` **empty** carries company-level facts (`COMPANY_FIELDS`: website, founding year, HQ, API, pricing…) and is applied to every entry of that company, certified or not — one row instead of one per listing. `fill_only=True`, so it only fills gaps a product row left empty.

Two traps this design exists to avoid: a commercial product built on an open-source project does not make that project certified (`steve` vs `powerfill` rows), and `enrich_from_github` deliberately ignores the repo's `homepage` field because projects point it at a hosted commercial offering.

Scope for non-certified rows: companies publishing a **named, OCPP-based management platform**. CPO networks, roaming hubs and unnamed vendor portals are out — `docs/csms-methodology.md` states this so the omissions read as a choice.
