# How the CSMS catalogue is built

Reference document for [`csms.md`](../csms.md) — what the data is, where it comes
from, and what each value is allowed to mean. Read this before drawing a
conclusion from the directory.

## Dataset architecture

The Markdown is a view. Everything it shows is reconstructed on every render from
three files:

```text
OCA registry ──► csms-certificates.csv ─┐
                                        ├─► csms.py render ─► csms.md
csms.csv          (curated products) ───┤                  └─► csms-features.md
csms-features.csv (curated features) ───┘
```

| File | Nature | Rule |
| --- | --- | --- |
| `csms-certificates.csv` | Generated mirror of the [OCA certified products registry](https://openchargealliance.org/certified-companies/), one row per certificate | Never edited by hand. `python csms.py fetch` refreshes it; corrections belong upstream with the Open Charge Alliance |
| `csms.csv` | Curated, one row per product (or per company) | **The canonical curated dataset.** No script ever writes it |
| `csms-features.csv` | Curated, one row per (product, feature, source) | No script ever writes it |
| `csms.md`, `csms-features.md` | Generated tables inside `GENERATED` markers, hand-authored prose around them | Never edit between the markers |

`csms.csv` carries more than the directory shows — HQ country and city, founding
year, first release, latest version, pricing, ISO 15118, Eichrecht, licence,
deployment model, notes and sources. Those columns were dropped from the table
because a sixteen-column Markdown table is unreadable, **not** because the data
stopped mattering. They stay in the dataset for anyone consuming the CSV.

## Source precedence

1. **The OCA registry** wins for what it covers: company name, country,
   participant page, product designation, OCPP version, certificate type,
   certified software version and the certificate PDF.
2. **Curated product rows** (`csms.csv`) complete it and are the only source for
   non-certified products. An empty curated cell never blanks a registry value —
   which is what lets a row carry only the facts it actually knows.
3. **Company-level rows** — `oca_company` filled, `oca_product` empty — carry
   facts about the vendor (website, founding year, HQ, API, pricing, status) and
   apply to every product listed under that company, certified or not — they
   are facts about the vendor, not about a certificate. They only fill gaps; a
   product row always wins over its company row.
4. **Curated feature rows** (`csms-features.csv`) attach vendor-documented
   capabilities by `slug`.

Every curated value needs a URL in that row's `sources` column, and every curated
feature needs one in its own `source_url`. A value you cannot cite belongs in no
cell. The single exception is `contributor:<name>`, for a fact a maintainer knows
from their own research but cannot cite publicly; the row's `notes` says so, and
such a value is a candidate for upgrading, not a verified fact.

## What gets a row

Every OCA-certified CSMS, plus any company publishing a **named, OCPP-based
charging-station management platform** — software-only or sold alongside its own
hardware.

Deliberately excluded: charge point operators that merely run a network without
selling the platform (Pod Point, ChargeZone, Statiq, Izivia, Freshmile…), roaming
hubs (Hubject, Gireve), and hardware vendors whose portal has no distinct product
name. These omissions are a scope choice, not an oversight.

### CSMS versus the layers next to it

The line that catches most candidates out is the one between a CSMS and the
products that sit beside it. A platform that optimises energy, shaves peaks,
schedules sessions or resells a driver app on top of *someone else's* CSMS is not
one.

FLEXECHARGE draws that line itself: "HARMON-E is not a CPMS replacement. It works
alongside CPMS platforms" — its gateway is "a standard OCPP proxy, which relays
incoming messages from connected charging stations to any freely selectable
Charge Point Management System". Peak Energy is just as blunt: "Peak Energy is
not another CPMS or energy platform. It is a specialized DSO pricing and capacity
insights service that sits alongside your existing systems." Scopt Powerconnect
(a smart-charging overlay working "with any CPMS"), Perific (home energy metering
that reports *into* Monta and AMPECO), Vourity (unattended-payment terminals) and
Fell Tech (home automation treating a charger as one schedulable load) are out on
the same test, despite appearing on charger vendors' integration-partner pages
next to real CSMS.

The test cuts both ways. Invisia markets itself as building energy management,
but its service list includes hardware-less OCPP station management, RFID card
issuance, tariffs and roaming — so it is in. What a vendor calls itself matters
less than whether it terminates OCPP and manages the stations.

Beware name collisions when checking a vendor against the registry: the
OCA-certified `ELOCITYTECH INC` (Canada, "HIEV CSMS") is unrelated to the Polish
`elo.city`, and the certified `Everon CO., Ltd.` (Republic of Korea) is unrelated
to the Dutch Everon platform.

## Features: two kinds of evidence

[`csms-features.md`](../csms-features.md) keeps them in separate columns, and the
data model never merges them.

### Certified — derived from the OCA certificate type

The OCA publishes a certificate *type* rather than a feature list. The
single-letter codes are expanded using the legend from the registry's own
`Certificate type` filter:

| Code | Feature |
| --- | --- |
| `S` | Advanced Security |
| `L` | Local Authorization List Management |
| `C` | Smart Charging |
| `D` | Advanced Device Management |
| `R` | Reservation |
| `U` | Advanced User Interface |
| `I` | ISO 15118 Support |

`Core` maps to itself and `Security` to Advanced Security — the same feature the
`S` letter yields. `Subset` and `Family` are scope qualifiers, not feature sets,
and contribute nothing. A product holding several
certificates gets the union of their features.

An unknown token fails the render rather than producing an empty cell, so a new
OCA code forces a deliberate decision instead of silently shrinking a product's
feature list.

### The OCPP 1.6 `Full` inference

`Full` is the one expansion the OCA legend does not spell out. On OCPP 1.6 we
read it as the six feature profiles the OCPP 1.6 specification defines (section
3, "Feature Profiles") — Core, Firmware Management, Local Authorization List
Management, Reservation, Smart Charging and Remote Trigger. **This expansion is
our inference, not an OCA statement.** The raw certificate type stays in the
`OCA certificates` column so the derivation can be checked against the PDF.

On OCPP 2.0.1, `Full` is deliberately **not** expanded. No CSMS certificate uses
it today, and guessing "Core plus every block" would publish an inference that
reads exactly like a derived feature. It is treated as an unknown token instead,
which fails the render — so the first such certificate forces a decision rather
than a guess.

### Vendor-documented — curated in `csms-features.csv`

A certificate is expensive and opt-in, so it under-reports what products do.
`csms-features.csv` records capabilities the vendor documents publicly, one row
per `(slug, feature, source_url)`. Acceptable sources, in order of preference:

1. official API or technical documentation;
2. official product documentation and feature matrices;
3. official product pages;
4. repositories the vendor maintains.

Third-party marketing directories are a last resort and, in practice, a reason to
leave the cell empty instead. Marketing adjectives are not features: the source
has to describe the capability, and the row's `note` quotes or paraphrases the
sentence it came from.

Feature names come from a **controlled vocabulary** (`FEATURE_VOCAB` in
`csms.py`), shared with the certificate derivation so the two kinds of evidence
stay comparable. A name outside it fails the render. Adding a capability is a
deliberate edit to that table, not a free-text cell — otherwise the dataset
accumulates twelve spellings of "load balancing".

A feature can legitimately appear on both sides: an OCA certificate proves it and
the vendor also documents it. Both are shown. What never happens is the reverse
promotion — vendor documentation does not turn into certification.

## One row per product, not per certificate

The registry issues a certificate per product *and software version*, and vendors
often bake that version into the product name — `eBAB Server v1.6` and
`eBAB Server v1.6.1` are one product, certified twice. A trailing dotted version
is therefore stripped before grouping; a dot is required, so model numbers like
`MON-CSMS-V10` survive.

A few vendors go further and rename the platform between certificates; those are
merged through a small hand-maintained alias table in `csms.py` (Driivz, NEC,
KEPCO KDN, Elvo, I-Charge Solutions). The registry also spells the same company
several ways — `Shenzhen Infypower Co. Ltd` and `Co., Ltd`,
`Instituto Tecnológico de la Energía` with and without `(ITE)` — which would
split one product in two, so punctuation and parentheticals are ignored when
matching a vendor. Eleven such duplicates are collapsed today.

Merging never hides evidence: the **OCA certificates** column lists *every*
certificate the product holds, each with its OCPP version, certificate type, the
certified software version in parentheses, and a link to the PDF.
`csms-certificates.csv` remains the unmerged, one-row-per-certificate record,
including registration dates.

Two products from one vendor are only merged when the certificates clearly
describe the same platform. Vendors legitimately ship several CSMS products, and
the registry also contains a few entries that look like hardware model numbers
filed under the CSMS product type — those are left alone.

## Column semantics

**Product** links to the vendor's own site, or to the repository for a
source-available project. **Company** links to the vendor's **OCA participant
page** where the registry provides one (158 of the 293 certificates); that page
lists the vendor's certificates and postal address.

**OCA certificates** lists the certificates found in the mirrored registry. An
empty cell means *no certificate was found there* — not that a product was
assessed and failed. Certification is voluntary and paid for.

**Source available** is `Y`, linked to the repository, when the source code is
publicly accessible. It is **not** a licence statement: source-available is not
the same as open source under an OSI-approved licence. The `license` column of
`csms.csv` tracks that separately, and you should read the licence before
assuming any right to reuse, modify or redistribute. There is no `N`: we check
whether a repository exists, not whether one is absent.

**API** is `Y` when a reliable source documents that the product exposes an API.
When the documentation is public, that `Y` links straight to it. Several
platforms document their API behind a customer login — those show an unlinked
`Y`, because the API is attested even though you cannot read the reference
without an account. An empty cell means *unverified*, never *no API*.

**OCPI** is `Y` when the product row states it or a curated feature row documents
`OCPI Roaming`, in which case the cell links to that source.

**Deployment** is `saas`, `self-hosted` or `both`. **Status** is `active`,
`acquired` or `discontinued`.

## Interpreting an empty cell

**An empty cell means *not known from a source we can cite*.** It never means
*no*. This is the single most important thing to know about the dataset, and it
follows directly from the sourcing rule: a contributor who cannot cite a fact
leaves the cell empty rather than guessing, so absence is a statement about our
research, not about the product.

Three consequences worth keeping in mind:

**A missing feature is not an absent feature.** Certification is opt-in and costs
money, and vendor documentation is incomplete by nature. A vendor certified for
`Core` alone may well support Smart Charging without having certified it.

**Certification applies to a product and a software version, not to a brand.**
Each certificate PDF names the exact software version tested. A vendor being in
this list says nothing about the version you are about to deploy.

**The certified set is geographically skewed.** 194 of the 293 CSMS certificates
are held by South Korean companies, because certification is effectively required
there. The OCA registry is an exhaustive list of *certified* CSMS, not a
representative sample of the market — several major platforms are absent simply
because they never applied.

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md#adding-or-correcting-a-csms-entry) for
how to add or correct an entry.
