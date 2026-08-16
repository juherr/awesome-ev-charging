"""Charging Station Management System (CSMS) product listing.

Two stages, connected by reviewable CSVs:

    fetch   -> csms-certificates.csv  the Open Charge Alliance certificate registry
    render  -> csms.md                the compact directory
            -> csms-features.md       the feature annex

The curated CSVs are the canonical dataset; the Markdown files are only a view:

    OCA registry ──► csms-certificates.csv ─┐
                                            ├─► render ─► csms.md
    csms.csv          (curated products) ───┤          └─► csms-features.md
    csms-features.csv (curated features) ───┘

Nothing may reach the Markdown that cannot be reconstructed from those three
files plus the rules in this module.

Deliberately a separate script from pipeline.py: that module is GitHub discovery,
this one mirrors a non-GitHub registry. It imports pipeline only to reuse the
HTTP cache, the GitHub helpers and the marker injection.

Run `python csms.py <stage> --help` for stage options.
"""

import argparse
import csv
import hashlib
import io
import json
import os
import re
import tempfile
import time
import unicodedata
from collections import Counter, defaultdict

import requests

import pipeline

# --- Open Charge Alliance registry -------------------------------------------

# The certified-products page renders client-side, but its filter UI is backed by
# a public JSON endpoint. `id` is the WordPress page id of /certified-companies/.
OCA_AJAX_URL = "https://openchargealliance.org/wp-json/custom/v1/ajax-loader"
OCA_PAGE_ID = "299052"
OCA_PRODUCT_TYPE = "Charging Station Management System"
# The endpoint defaults to 6 items per page but honours posts_per_page, which
# turns the CSMS sweep from 49 requests into 6 against someone else's registry.
OCA_PAGE_SIZE = 50
HTTP_TIMEOUT = 30  # seconds; without it a stalled connection hangs the CI job

CERTS_PATH = "csms-certificates.csv"
VENDORS_PATH = "csms.csv"
FEATURES_PATH = "csms-features.csv"
CSMS_MD_PATH = "csms.md"
FEATURES_MD_PATH = "csms-features.md"
# `render` replaces the text between these markers, so the prose around each table
# (intro, caveats, legend) stays hand-authored.
CSMS_MARKER_BEGIN = "<!-- BEGIN GENERATED CSMS -->"
CSMS_MARKER_END = "<!-- END GENERATED CSMS -->"
FEATURES_MARKER_BEGIN = "<!-- BEGIN GENERATED CSMS FEATURES -->"
FEATURES_MARKER_END = "<!-- END GENERATED CSMS FEATURES -->"

CERT_FIELDS = [
  "certificate_no", "company", "company_link", "country",
  "product_designation", "certificate_type", "software_version",
  "protocol_version", "date_of_registration", "certificate_url", "product_type",
]

# Every column of csms.csv, in file order, with the scope it carries:
#   IDENTITY — never overlaid: `merge` reads each one by hand, either to place the
#              row on an entry or because the value needs coercing (a set, a flag)
#   COMPANY  — a fact about the vendor, so one row can set it for all its products
#   PRODUCT  — a fact about this product only
# The overlay lists below are derived from this table, so adding a column here is
# the only edit needed; previously the same schema was restated in three places
# and a name missing from one of them was dropped silently.
IDENTITY, COMPANY, PRODUCT = "identity", "company", "product"

VENDOR_FIELDS = {
  "slug": IDENTITY, "product": IDENTITY, "company": IDENTITY,
  "oca_company": IDENTITY, "oca_product": IDENTITY,
  "source_available": IDENTITY, "repo": IDENTITY,
  "website": COMPANY, "api": COMPANY, "api_docs": COMPANY,
  "pricing": COMPANY, "pricing_url": COMPANY, "changelog": COMPANY,
  "hq_country": IDENTITY, "hq_city": COMPANY, "company_founded": COMPANY,
  "first_release": PRODUCT, "latest_version": PRODUCT,
  "latest_version_date": PRODUCT,
  "ocpp_claimed": IDENTITY,
  "ocpi": PRODUCT, "iso15118": PRODUCT, "eichrecht": PRODUCT,
  "license": PRODUCT, "deployment": PRODUCT,
  "status": COMPANY, "notes": COMPANY, "sources": COMPANY,
}

COMPANY_FIELDS = [f for f, scope in VENDOR_FIELDS.items() if scope == COMPANY]
OVERLAY_FIELDS = [f for f, scope in VENDOR_FIELDS.items() if scope != IDENTITY]

# csms-features.csv — one row per (product, feature, source). Normalised rather
# than a list column in csms.csv, because the sourcing rule applies per feature:
# a claim without a URL is not a claim, and a row per fact keeps the diff
# reviewable when a vendor's documentation changes.
FEATURE_FIELDS = ["slug", "feature", "source_url", "note"]

# --- Certificate type -> supported features ----------------------------------

# Verbatim legend from the `Certificate type` filter on the OCA certified
# products page (https://openchargealliance.org/certified-companies/). These are
# the OCPP 2.0.1 functional blocks; OCA also applies the letters to OCPP 1.6.
CERT_LETTERS = {
  "S": "Advanced Security",
  "L": "Local Authorization List Management",
  "C": "Smart Charging",
  "D": "Advanced Device Management",
  "R": "Reservation",
  "U": "Advanced User Interface",
  "I": "ISO 15118 Support",
}

# The OCA legend spells out the letters but not `Full`. On OCPP 1.6 a full
# certificate covers the six feature profiles defined by the OCPP 1.6 spec
# (section 3, "Feature Profiles") — this expansion is our inference, and
# csms.md documents it as such.
OCPP16_FULL = [
  "Core",
  "Firmware Management",
  "Local Authorization List Management",
  "Reservation",
  "Smart Charging",
  "Remote Trigger",
]

# `Full` on OCPP 2.0.1 has no published expansion and no CSMS certificate uses it
# today. Guessing "Core plus every block" would publish an inference that looks
# identical to a derived feature, so it is left unresolved instead: the first such
# certificate fails the render and forces a deliberate, documented decision.

# The controlled vocabulary: canonical name -> short label for the table, where
# the full names blow the column width out. Insertion order is the display order.
#
# One vocabulary for both kinds of evidence. A curated feature naming something
# the OCA also certifies must use the OCA's own name, so "certified" and
# "vendor-documented" stay comparable instead of drifting into two dialects; a
# name outside this table fails the render rather than accumulating marketing
# labels. Adding a capability is a deliberate edit here, not a free-text cell.
FEATURE_VOCAB = {
  # Derivable from an OCA certificate type (see CERT_LETTERS / OCPP16_FULL).
  "Core": "Core",
  "Advanced Security": "Security",
  "Smart Charging": "Smart Charging",
  "Local Authorization List Management": "Local Auth",
  "Reservation": "Reservation",
  "Firmware Management": "Firmware",
  "Remote Trigger": "Remote Trigger",
  "Advanced Device Management": "Device Mgmt",
  "Advanced User Interface": "User Interface",
  "ISO 15118 Support": "ISO 15118",
  # Vendor-documented only: no OCA certificate expands into these, so they can
  # reach an entry only through csms-features.csv, with a source.
  "Plug & Charge": "Plug & Charge",
  "OCPI Roaming": "OCPI Roaming",
  "Tariffs": "Tariffs",
  "Payments": "Payments",
  "Token Management": "Token Mgmt",
  "Load Management": "Load Mgmt",
  "Reporting": "Reporting",
  "Multi-tenancy": "Multi-tenancy",
  "White-label": "White-label",
  "Remote Commands": "Remote Commands",
}

# Stable display order, most-common first, so the column reads consistently.
FEATURE_RANK = {name: i for i, name in enumerate(FEATURE_VOCAB)}

# The OCPI column is a shorthand for one vocabulary entry, so a curated feature
# row and the product-level `ocpi` cell cannot disagree about the same fact.
OCPI_FEATURE = "OCPI Roaming"


def derive_features(certificate_type, protocol_version):
  """Expand an OCA certificate type into (feature list, unresolved tokens).

  `certificate_type` is a `+`-joined mix of base types (Full, Core, Security,
  Subset, Family) and single-letter functional blocks. Unresolved tokens are
  returned rather than ignored so a new OCA code fails loudly instead of
  silently rendering an empty cell.
  """
  features, unresolved = [], []
  is_16 = (protocol_version or "").strip().startswith("OCPP 1.6")

  for token in [t.strip() for t in (certificate_type or "").split("+") if t.strip()]:
    if token == "Full" and is_16:
      features += OCPP16_FULL
    elif token == "Core":
      features.append("Core")
    elif token == "Security":
      features.append("Advanced Security")
    elif token in CERT_LETTERS:
      features.append(CERT_LETTERS[token])
    elif token in ("Subset", "Family"):
      # Scope qualifiers, not feature sets: `Subset` means "an unpublished
      # subset", `Family` that the certificate covers a product family.
      continue
    else:
      unresolved.append(token)

  return features, unresolved


def sort_features(features):
  """Order a feature set for display.

  Indexing FEATURE_RANK rather than tolerating a miss: both ways into a feature
  name are closed (vocabulary_gaps guards the derived ones, read_features the
  curated ones), so an unknown name is a broken invariant, not a value to sort
  last — and render_feature_row would raise on it a line later regardless.
  """
  return sorted(set(features), key=FEATURE_RANK.__getitem__)


def unresolved_tokens(certs):
  """Certificate-type tokens no rule in derive_features recognises."""
  return sorted({t for r in certs
                 for t in derive_features(r["certificate_type"],
                                          r["protocol_version"])[1]})


def vocabulary_gaps():
  """Feature names the certificate rules emit but the vocabulary does not define.

  The two tables are edited independently — a letter added to CERT_LETTERS is a
  natural place to forget FEATURE_VOCAB — and a gap would surface as a KeyError
  in the middle of rendering rather than as something a contributor can act on.
  """
  emitted = set(CERT_LETTERS.values()) | set(OCPP16_FULL) | {"Core"}
  return sorted(emitted - set(FEATURE_VOCAB))


# --- Product identity ---------------------------------------------------------

def company_key(company):
  """Normalise a company name so its spelling variants group as one vendor.

  The registry spells the same company several ways across certificates —
  "Shenzhen Infypower Co. Ltd" / "Co., Ltd", "Instituto Tecnológico de la
  Energía" with and without "(ITE)" — which would otherwise split one product
  into two rows. Every Unicode punctuation mark is dropped, not just the period
  and comma seen so far, so a hyphen, apostrophe or middle dot cannot introduce
  the same split again. Legal suffixes are deliberately kept: "Co Ltd" still
  distinguishes companies that differ only by that.
  """
  bare = re.sub(r"\([^)]*\)", " ", str(company or ""))
  bare = "".join(" " if unicodedata.category(c).startswith("P") else c for c in bare)
  return re.sub(r"\s+", " ", bare).strip().lower()

# Vendors often bake a version into the product designation, so the same product
# appears once per certificate ("eBAB Server v1.6" / "eBAB Server v1.6.1"). Strip
# a trailing dotted version so those collapse into one row. Conservative on
# purpose: a dot is required, so model numbers like "MON-CSMS-V10" survive.
_TRAILING_VERSION_RE = re.compile(
  r"[\s\-–_]*(?:ver\.?|version|v)?\s*\d+(?:\.\d+)+\s*$", re.I)

# Judgment calls the regex cannot make: the same platform registered under
# genuinely different names. Keyed by lowercased company -> {lowercased
# designation: canonical name}. Only add an entry when the certificates clearly
# describe one product; distinct products from one vendor must stay distinct.
PRODUCT_ALIASES = {
  "driivz ltd": {
    # One platform, renamed between the 2019 (1.6) and 2023 (2.0.1) certificates.
    "driivz charging network management system": "Driivz",
    "driivz csms operator portal": "Driivz",
  },
  "nec corporation": {
    # N-CSMS16 / N-CSMS20 differ only by the OCPP generation they were tested on.
    "n-csms16": "N-CSMS",
    "n-csms20": "N-CSMS",
  },
  "kepco kdn": {
    "kdn-csms": "KEPCO KDN CSMS",
    "kepco kdn csms": "KEPCO KDN CSMS",
  },
  "elvo technology": {
    "elvo": "Elvo Platform – CSMS",
    "elvo platform – csms": "Elvo Platform – CSMS",
  },
  "i-charge solutions international co. ltd.": {
    "i-charge solutions charging stations management system": "I-Charge Solutions CSMS",
    "ics csms20": "I-Charge Solutions CSMS",
  },
}


# Re-keyed with company_key so an alias survives the registry respelling the
# company. Keyed on the raw name, "Driivz Ltd." would silently stop matching
# "Driivz Ltd" and the merge it encodes would come undone without a warning.
ALIASES_BY_COMPANY = {company_key(c): a for c, a in PRODUCT_ALIASES.items()}


def canonical_product(company, designation):
  """Return the display name a certificate's product should be grouped under."""
  alias = ALIASES_BY_COMPANY.get(company_key(company), {})
  hit = alias.get((designation or "").strip().lower())
  if hit:
    return hit
  stripped = _TRAILING_VERSION_RE.sub("", (designation or "").strip()).strip(" -–_")
  return stripped or (designation or "").strip()


# --- HTTP with on-disk cache -------------------------------------------------

def write_atomic(path, text):
  """Write a file via a temporary sibling, so readers never see it half-written.

  Both the cache and the committed mirror are read back by later runs; a process
  killed mid-write would otherwise leave a truncated file behind. The temporary
  file is unique per call — a fixed name would let two writers aimed at the same
  path corrupt each other's — and lives in the destination directory so the
  replace stays on one filesystem, which is what makes it atomic.
  """
  directory = os.path.dirname(path) or "."
  fd, tmp = tempfile.mkstemp(dir=directory, prefix=os.path.basename(path) + ".",
                             suffix=".tmp")
  try:
    with os.fdopen(fd, "w", newline="", encoding="utf-8") as f:
      f.write(text)
    os.replace(tmp, path)
  except BaseException:
    if os.path.exists(tmp):
      os.unlink(tmp)
    raise


def post_json_cached(url, payload, ttl=pipeline.CACHE_TTL):
  """POST a JSON body and cache the response on disk, keyed by URL + payload.

  pipeline.github_request_cached is GET-only and picks its cache extension from
  the Accept header, so the OCA endpoint needs its own helper. Shares the same
  cache directory, which is already git-ignored.
  """
  # The payload is part of the key: one URL serves every page and filter. The
  # digest only derives a filename — nothing here is a security boundary — but
  # SHA-256 keeps the file clear of the scanners that flag MD5 on sight.
  key = hashlib.sha256((url + json.dumps(payload, sort_keys=True)).encode()).hexdigest()
  cache_path = os.path.join(pipeline.CACHE_DIR, key + ".json")

  if os.path.exists(cache_path) and (time.time() - os.path.getmtime(cache_path) < ttl):
    try:
      with open(cache_path, "r", encoding="utf-8") as f:
        return json.load(f)
    except (OSError, ValueError):
      # A half-written cache file must read as a miss, not poison every run.
      pass

  try:
    r = requests.post(url, json=payload, timeout=HTTP_TIMEOUT,
                      headers={"Content-Type": "application/json"})
    r.raise_for_status()
    content = r.text
    parsed = json.loads(content)
    write_atomic(cache_path, content)
    return parsed
  except Exception as e:
    print(f"⚠️  OCA request failed: {e}")
    return None


# --- Normalisation -----------------------------------------------------------

_ORDINAL_DATE_RE = re.compile(r"^([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)\s+(\d{4})$")
_MONTHS = {m: i for i, m in enumerate(
  ["january", "february", "march", "april", "may", "june",
   "july", "august", "september", "october", "november", "december"], start=1)}


def parse_oca_date(text):
  """Convert an OCA date ("July 18th 2023") to ISO, or return it unchanged."""
  m = _ORDINAL_DATE_RE.match((text or "").strip())
  if not m:
    return (text or "").strip()
  month = _MONTHS.get(m.group(1).lower())
  if not month:
    return text.strip()
  return f"{m.group(3)}-{month:02d}-{int(m.group(2)):02d}"


def clean(text):
  """Collapse whitespace and escape pipes so a value is safe in a table cell."""
  return re.sub(r"\s+", " ", str(text or "")).strip().replace("|", r"\|")


# --- Stage 1: fetch ----------------------------------------------------------

def fetch_certificates(product_type):
  """Return every OCA certificate of a product type, normalised and deduplicated."""
  rows, seen, page, pages = [], set(), 1, 1

  while page <= pages:
    payload = {
      "id": OCA_PAGE_ID,
      "lang": "en",
      "paged": page,
      "posts_per_page": OCA_PAGE_SIZE,
      "group": "main",
      "status": "active",
      "post_type": "certificate",
      "filters": [{"field": "product-type", "value": product_type}],
    }
    body = post_json_cached(OCA_AJAX_URL, payload)
    if not body:
      raise SystemExit(f"OCA registry unreachable at page {page} — aborting rather "
                       f"than writing a truncated {CERTS_PATH}.")

    pages = body.get("pages") or 1
    for item in body.get("items") or []:
      certificate = item.get("certificate") or {}
      number = clean(certificate.get("text"))
      if not number or number in seen:
        continue
      seen.add(number)
      rows.append({
        "certificate_no": number,
        "company": clean((item.get("company") or {}).get("text")),
        "company_link": clean(item.get("company_link")),
        "country": clean(item.get("country")),
        "product_designation": clean(item.get("product_designation")),
        "certificate_type": clean(item.get("certificate_type")),
        "software_version": clean(item.get("version")),
        "protocol_version": clean(item.get("protocol_version")),
        "date_of_registration": parse_oca_date(item.get("date_of_registration")),
        "certificate_url": clean((certificate.get("file") or {}).get("url")),
        "product_type": clean(item.get("product_type")),
      })

    print(f"📥 OCA page {page}/{pages} ({len(rows)} certificates)")
    page += 1

  return rows


def cmd_fetch(args):
  """Mirror the OCA certificate registry into a CSV."""
  rows = fetch_certificates(args.product_type)
  rows.sort(key=lambda r: (r["company"].lower(), r["product_designation"].lower(),
                           r["certificate_no"]))

  # Guard before writing, not after: a scrape of an undocumented endpoint that
  # comes back short must not reach the file, let alone the render that follows.
  previous = len(read_csv(args.out, quiet=True))
  if len(rows) < args.min_rows:
    raise SystemExit(f"Only {len(rows)} certificates fetched (expected at least "
                     f"{args.min_rows}) — refusing to overwrite {args.out}.")
  if len(rows) < previous and not args.allow_shrink:
    raise SystemExit(f"{args.out} would shrink from {previous} to {len(rows)} rows "
                     f"— refusing. Pass --allow-shrink if the registry really did.")

  buffer = io.StringIO()
  writer = csv.DictWriter(buffer, fieldnames=CERT_FIELDS)
  writer.writeheader()
  writer.writerows(rows)
  write_atomic(args.out, buffer.getvalue())

  unresolved = unresolved_tokens(rows)
  if unresolved:
    print(f"⚠️  Unknown certificate-type tokens (update CERT_LETTERS): {unresolved}")

  companies = {r["company"] for r in rows}
  products = {(r["company"], r["product_designation"]) for r in rows}
  print(f"✅ {len(rows)} certificates · {len(companies)} companies · "
        f"{len(products)} products -> {args.out}")


# --- Stage 2: render ---------------------------------------------------------

def read_csv(path, fields=None, quiet=False):
  """Read a CSV into a list of dicts, tolerating a missing file.

  With `fields`, unknown column names are reported: csms.csv is hand-edited, and
  a misspelt header would otherwise be read into nothing and vanish in silence.
  """
  if not os.path.exists(path):
    if not quiet:
      print(f"⚠️  {path} not found — continuing without it.")
    return []
  with open(path, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    unknown = sorted(set(reader.fieldnames or []) - set(fields or []))
    if fields and unknown:
      print(f"⚠️  {path}: unknown column(s) {unknown} — ignored.")
  return rows


def is_company_row(row):
  """A curated row naming a company but no product carries company-level facts."""
  return bool(clean(row.get("oca_company")) and not clean(row.get("oca_product")))


def is_product_row(row):
  """A curated row that becomes an entry of its own, and so can own features.

  The same predicate decides which slugs `product_slugs` accepts and which rows
  `merge` turns into entries. Stated twice, the looser one would validate a slug
  the merge then has nowhere to attach, and its features would vanish behind a
  warning.
  """
  return bool(not is_company_row(row) and clean(row.get("product")))


def product_slugs(vendors, path=VENDORS_PATH):
  """Every product-row slug in csms.csv, rejecting missing or duplicate ones.

  The slug is what csms-features.csv joins on, so it has to be present and
  unique before any feature can be attached. A duplicate would silently give one
  product another's features, which is exactly the failure the sourcing
  discipline exists to prevent.
  """
  counts = Counter(clean(row.get("slug")) for row in vendors)
  missing = counts.pop("", 0)
  duplicates = sorted(slug for slug, n in counts.items() if n > 1)

  problems = []
  if missing:
    problems.append(f"{missing} row(s) without a slug")
  if duplicates:
    problems.append(f"duplicate slug(s) {duplicates}")
  if problems:
    raise SystemExit(f"{path}: " + "; ".join(problems) + " — every row needs one "
                     f"unique slug, it is the key {FEATURES_PATH} joins on.")

  return {clean(r.get("slug")) for r in vendors if is_product_row(r)}


def read_features(path, slugs):
  """Read the curated feature file into {slug: {feature: [source URLs]}}.

  Everything is validated up front and reported at once: a contributor fixing
  one typo per run would give up long before the file rendered.
  """
  claims = defaultdict(lambda: defaultdict(set))
  unknown_features, unknown_slugs, unsourced = set(), set(), set()

  for row in read_csv(path, fields=FEATURE_FIELDS):
    slug, feature = clean(row.get("slug")), clean(row.get("feature"))
    source = clean(row.get("source_url"))
    if feature not in FEATURE_VOCAB:
      unknown_features.add(feature or "(empty)")
    if slug not in slugs:
      unknown_slugs.add(slug or "(empty)")
    if not source:
      unsourced.add(f"{slug or '(empty)'} / {feature or '(empty)'}")
    else:
      # Anything collected below is discarded by the raise, so the accumulation
      # needs no guard of its own — one condition per rule, stated once.
      claims[slug][feature].add(source)

  problems = []
  if unknown_features:
    problems.append(f"feature(s) outside the controlled vocabulary: "
                    f"{sorted(unknown_features)} — add them to FEATURE_VOCAB in "
                    f"csms.py, or use the existing name")
  if unknown_slugs:
    problems.append(f"slug(s) with no product row in {VENDORS_PATH}: "
                    f"{sorted(unknown_slugs)}")
  if unsourced:
    problems.append(f"row(s) without a source_url: {sorted(unsourced)} — an "
                    f"unsourced feature is not a feature")
  if problems:
    raise SystemExit(f"{path}: " + "; ".join(problems) + ".")

  # Sorted here and nowhere else: this is the one owner of source order, and
  # _sourced links the label to the first URL, so the order is visible output.
  return {slug: {feature: sorted(urls) for feature, urls in features.items()}
          for slug, features in claims.items()}


def _key(company, product):
  """Join key shared by certificates and curated rows."""
  return (company_key(company), clean(product).lower())


def new_entry(product, company, company_link=""):
  """Blank merged-product record — the one place the entry shape is defined.

  `certified` is not stored: a product is certified exactly when it holds a
  certificate, so the list is the single source of truth. Neither is the country:
  it lives in the two CSVs, and no table renders it.

  The two feature sets are never merged. `features_certified` is what an OCA
  certificate proves; `features_claimed` (name -> source URLs) is what the vendor
  documents. Collapsing them would make a marketing page read like a certificate.
  """
  return {
    "product": clean(product),
    "company": clean(company),
    "company_link": company_link,
    "versions": set(),
    "features_certified": set(),
    "features_claimed": {},
    "certificates": [],
  }


def group_certificates(certs):
  """Aggregate certificates into one entry per (company, canonical product)."""
  products = {}
  for row in certs:
    product = canonical_product(row["company"], row["product_designation"])
    key = _key(row["company"], product)
    entry = products.setdefault(
      key, new_entry(product, row["company"], row["company_link"]))

    # Spelling variants merged: keep the fullest name, and any participant link
    # whichever certificate happens to carry it. Length alone would leave two
    # equally long spellings decided by mirror row order, which `fetch`
    # regenerates — so the name breaks ties on itself and stays stable.
    if (len(row["company"]), row["company"]) > (len(entry["company"]), entry["company"]):
      entry["company"] = row["company"]
    entry["company_link"] = entry["company_link"] or row["company_link"]

    version = row["protocol_version"].replace("OCPP", "").strip()
    entry["versions"].add(version)
    entry["features_certified"].update(
      derive_features(row["certificate_type"], row["protocol_version"])[0])
    # Keep every certificate: merging designations must not hide one.
    entry["certificates"].append({
      "version": version,
      "type": row["certificate_type"],
      "software": row["software_version"],
      "date": row["date_of_registration"],
      "url": row["certificate_url"],
    })

  return products


def enrich_from_github(entry, repo, headers):
  """Confirm a curated repository exists, and take its canonical URL.

  The repository is the evidence behind `Source available`, and it is what that
  cell links to. A failed lookup aborts rather than rendering the row as if no
  source had been found: that would publish a rate-limit as a fact.

  This used to also read the release list for First release / Latest version.
  Those columns are gone; the release call is not made any more, and the CSV
  columns that held them (`first_release`, `latest_version`, `changelog`) are
  curated like every other value — never derived here.
  """
  obj = pipeline.get_repo_data(repo, headers)
  if not obj:
    raise SystemExit(f"GitHub lookup failed for {repo} — aborting rather than "
                     f"rendering its metadata as unknown. Retry, or pass --token.")

  # Deliberately not using obj["homepage"]: projects often point it at a hosted
  # commercial offering (SteVe -> powerfill.io), which would make the row read as
  # if the open-source project and the paid product were the same thing.
  entry["repo_url"] = obj.get("html_url") or f"https://github.com/{repo}"
  entry["source_available"] = True


def _overlay(entry, row, fields, fill_only=False):
  """Copy the non-empty curated values of `fields` onto an entry.

  Curated data completes what the registry gave; an empty cell never blanks a
  value, which is what lets one curated row carry only what it actually knows.

  `fill_only` is for company-level rows: a fact stated for the whole vendor is a
  default, so it must not overwrite what a product row said about one product.
  """
  for field in fields:
    if fill_only and clean(entry.get(field)):
      continue
    value = clean(row.get(field))
    if value:
      entry[field] = value


def _apply_product_row(products, row, headers):
  """Overlay a curated row describing one product, creating it if it is new."""
  # Canonicalise here too, so a curated row may cite either the raw OCA
  # designation or the merged display name and still land on the same entry.
  oca_key = _key(row.get("oca_company"),
                 canonical_product(row.get("oca_company"), row.get("oca_product")))
  if clean(row.get("oca_company")) and oca_key not in products:
    print(f"⚠️  {row.get('slug') or row.get('product')}: no OCA certificate matches "
          f"{row.get('oca_company')!r} / {row.get('oca_product')!r}")

  own_key = _key(row.get("company"), row.get("product"))
  # Never replace an entry a curated row happens to collide with — that would
  # silently drop a certified product.
  entry = products.get(oca_key) or products.get(own_key)
  if entry is None:
    entry = products.setdefault(own_key, new_entry(row.get("product"), row.get("company")))
  else:
    entry["product"] = clean(row.get("product"))
    if clean(row.get("company")):
      entry["company"] = clean(row.get("company"))

  entry["versions"].update(
    v.strip() for v in clean(row.get("ocpp_claimed")).split(",") if v.strip())
  _overlay(entry, row, OVERLAY_FIELDS)

  if clean(row.get("source_available")).lower() in ("y", "yes", "true", "1"):
    entry["source_available"] = True
  repo = clean(row.get("repo"))
  if repo:
    enrich_from_github(entry, repo, headers)

  return entry


def merge(certs, vendors, headers, claims=None):
  """Union the OCA registry with the curated CSVs into one row per product.

  Product rows run first and company rows second, so a company-level row reaches
  every product regardless of where it sits in the file — with a single pass its
  effect depended on row order, which is invisible in a file people append to.
  Curated features come last: they attach by slug, which only exists once the
  product rows have been applied.
  """
  products = group_certificates(certs)
  company_rows = [r for r in vendors if is_company_row(r)]

  # The entry key is (company, product), either of which a curated row may
  # rename, so the slug is carried here rather than stored on the entry.
  by_slug = {clean(row.get("slug")): _apply_product_row(products, row, headers)
             for row in vendors if is_product_row(row)}

  # read_features validated every slug against the same is_product_row
  # predicate, so each one has an entry waiting for it.
  for slug, features in (claims or {}).items():
    by_slug[slug]["features_claimed"] = features

  # Every entry of the vendor, not just its certified ones: COMPANY_FIELDS are
  # facts about the company (website, founding year, HQ…), so withholding them
  # from a product that happens to hold no certificate would render "unknown"
  # for something the dataset knows. `fill_only` keeps it to filling gaps.
  by_company = defaultdict(list)
  for (company, _), entry in products.items():
    by_company[company].append(entry)

  for row in company_rows:
    targets = by_company.get(company_key(row.get("oca_company")))
    if not targets:
      print(f"⚠️  {row.get('slug')}: no OCA company matches {row.get('oca_company')!r}")
      continue
    for entry in targets:
      _overlay(entry, row, COMPANY_FIELDS, fill_only=True)

  return products


# --- Markdown ----------------------------------------------------------------

# The directory answers "which of these could I run, and does it speak what I
# need?". Everything else a reader might want — HQ, founding year, pricing,
# licence, release history, ISO 15118, Eichrecht — stays in csms.csv, which is
# the dataset; a sixteen-column table was unreadable and still incomplete.
TABLE_HEADERS = [
  "Product", "Company", "OCPP", "OCA certificates", "Source available",
  "OCPI", "API", "Deployment", "Status",
]

# The feature annex, generated into its own file: 240 products times two
# evidence classes does not belong in a column of the directory.
FEATURE_TABLE_HEADERS = ["Product", "Company", "Certified (OCA)", "Vendor-documented"]


def _link(label, url):
  """Render a Markdown link, falling back to the bare label when there's no URL."""
  return f"[{label}]({url})" if url else (label or "")


def _display_name(entry):
  """What the product is called in both tables, falling back to the vendor.

  A handful of registry entries carry a company but no usable designation.
  """
  return entry["product"] or entry["company"]


def md_table(headers, rows):
  """Render a Markdown table with leading/trailing pipes (MD055/MD056)."""
  lines = ["| " + " | ".join(headers) + " |",
           "| " + " | ".join(["---"] * len(headers)) + " |"]
  for row in rows:
    lines.append("| " + " | ".join(str(c).strip() or "—" for c in row) + " |")
  return lines


def _version_key(version):
  """Sort OCPP version labels numerically (1.6 before 2.0.1)."""
  return tuple(int(p) if p.isdigit() else 0 for p in version.split("."))


def _sourced(label, sources):
  """Link a label to its first source, keeping any further ones reachable."""
  return " ".join([_link(label, sources[0])]
                  + [f"[{i}]({url})" for i, url in enumerate(sources[1:], start=2)])


def _cert_label(cert):
  """`1.6 Full (v2.3)` — OCPP version, certificate type, certified software."""
  label = f"{cert['version']} {cert['type']}".strip()
  return label + (f" ({cert['software']})" if cert["software"] else "")


def render_row(entry):
  """Build one directory row from a merged product entry."""
  site = entry.get("website") or entry.get("repo_url") or ""

  # `api` records that an API exists; `api_docs` that its documentation is
  # public. Documented-but-login-gated is therefore an unlinked "Y", and an
  # empty cell stays "not verified", never "no API".
  api = _link(entry.get("api") or ("Y" if entry.get("api_docs") else ""),
              entry.get("api_docs"))

  versions = ", ".join(sorted(entry["versions"], key=_version_key))

  # Never "N": we check whether a repository exists, not whether one is absent.
  source_available = _link("Y", entry.get("repo_url")) if entry.get("source_available") else ""

  # OCPI is either stated on the product row or documented as a feature; the
  # feature carries a URL, so prefer it as the link target.
  ocpi_sources = entry["features_claimed"].get(OCPI_FEATURE)
  ocpi = _sourced(entry.get("ocpi") or "Y", ocpi_sources) if ocpi_sources \
      else entry.get("ocpi", "")

  certificates = " · ".join(
    _link(_cert_label(c), c["url"])
    for c in sorted(entry["certificates"],
                    key=lambda c: (_version_key(c["version"]), c["date"], c["type"])))

  return [
    # The product name carries the link to the vendor's own site, or to the
    # repository for a source-available project — one column, not two.
    _link(_display_name(entry), site),
    # The registry gives an OCA participant page for most certified vendors; it
    # lists their certificates and postal address, so it earns the company link.
    _link(entry["company"], entry.get("company_link")),
    versions,
    certificates,
    source_available,
    ocpi,
    api,
    entry.get("deployment", ""),
    entry.get("status", ""),
  ]


def render_feature_row(entry):
  """Build one annex row, keeping the two kinds of evidence in their own column."""
  certified = " · ".join(FEATURE_VOCAB[f] for f in sort_features(entry["features_certified"]))
  claimed = " · ".join(
    _sourced(FEATURE_VOCAB[f], entry["features_claimed"][f])
    for f in sort_features(entry["features_claimed"]))

  return [
    _display_name(entry),
    entry["company"],
    certified,
    claimed,
  ]


def sort_entries(products):
  """Order products for display, deterministically.

  Two vendors ship a product under the same name, so the display name alone is
  not a total order — without the company tiebreak their order would follow dict
  insertion, and a re-render could reshuffle rows nothing had changed.
  """
  return sorted(products.values(),
                key=lambda e: (_display_name(e).lower(), e["company"].lower()))


def cmd_render(args):
  """Merge the mirror with the curated CSVs and inject both generated tables."""
  certs = read_csv(args.certs)
  if not certs:
    raise SystemExit(f"{args.certs} is empty or missing — run `python csms.py fetch` first.")

  gaps = vocabulary_gaps()
  if gaps:
    raise SystemExit(f"Certificate rules emit {gaps}, which FEATURE_VOCAB does not "
                     f"define — add them to the vocabulary in csms.py.")

  # Check before any network work: an unknown token means the mapping is stale,
  # and rendering would quietly publish a product with fewer features than it has.
  unresolved = unresolved_tokens(certs)
  if unresolved:
    raise SystemExit(f"Unknown certificate-type tokens {unresolved} — update "
                     f"CERT_LETTERS in csms.py rather than rendering empty features.")

  vendors = read_csv(args.vendors, fields=VENDOR_FIELDS)
  claims = read_features(args.features, product_slugs(vendors, args.vendors))
  products = merge(certs, vendors, pipeline.auth_headers(args.token), claims)

  entries = sort_entries(products)

  # Both files are one view of one dataset, so the render is all-or-nothing:
  # every body is built and every injection validated in memory before the
  # first byte is written. A missing annex, or one whose markers were edited
  # away, must not leave a fresh directory next to a stale annex.
  directory = "\n".join(md_table(TABLE_HEADERS, [render_row(e) for e in entries]))
  annex = "\n".join(
    md_table(FEATURE_TABLE_HEADERS, [render_feature_row(e) for e in entries]))
  rendered = []
  for path, body, begin, end in (
      (args.md, directory, CSMS_MARKER_BEGIN, CSMS_MARKER_END),
      (args.features_md, annex, FEATURES_MARKER_BEGIN, FEATURES_MARKER_END)):
    try:
      with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    except OSError as e:
      raise SystemExit(f"Cannot read {path}: {e}")
    rendered.append(
      (path, pipeline._replace_between_markers(content, body, begin, end, path)))
  for path, content in rendered:
    write_atomic(path, content)

  certified = sum(1 for e in entries if e["certificates"])
  source = sum(1 for e in entries if e.get("source_available"))
  documented = sum(1 for e in entries if e["features_claimed"])
  print(f"✅ {len(entries)} products · {certified} OCA-certified · {source} source-available "
        f"-> {args.md}")
  print(f"✅ {documented} products with vendor-documented features -> {args.features_md}")


# --- CLI ---------------------------------------------------------------------

def main():
  parser = argparse.ArgumentParser(description="CSMS product listing.")
  sub = parser.add_subparsers(dest="stage", required=True)

  p_fetch = sub.add_parser("fetch", help="Mirror the OCA certificate registry into a CSV.")
  p_fetch.add_argument("--out", default=CERTS_PATH, help="Output CSV path.")
  p_fetch.add_argument("--product-type", default=OCA_PRODUCT_TYPE,
                       help="OCA product type to mirror.")
  p_fetch.add_argument("--min-rows", type=int, default=250,
                       help="Refuse to write fewer rows than this (default: 250).")
  p_fetch.add_argument("--allow-shrink", action="store_true",
                       help="Allow the mirror to contain fewer rows than before.")
  p_fetch.set_defaults(func=cmd_fetch)

  p_render = sub.add_parser("render", help="Render the CSMS directory and feature annex.")
  p_render.add_argument("--certs", default=CERTS_PATH, help="Certificate CSV path.")
  p_render.add_argument("--vendors", default=VENDORS_PATH, help="Curated product CSV path.")
  p_render.add_argument("--features", default=FEATURES_PATH, help="Curated feature CSV path.")
  p_render.add_argument("--md", default=CSMS_MD_PATH, help="Directory Markdown file.")
  p_render.add_argument("--features-md", default=FEATURES_MD_PATH,
                        help="Feature annex Markdown file.")
  p_render.add_argument("--token", help="GitHub personal access token (optional).")
  p_render.set_defaults(func=cmd_render)

  args = parser.parse_args()
  args.func(args)


if __name__ == "__main__":
  main()
