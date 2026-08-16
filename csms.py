"""Charging Station Management System (CSMS) product listing.

Two stages, connected by a reviewable CSV:

    fetch   -> csms-certificates.csv  the Open Charge Alliance certificate registry
    render  -> csms.md                one table, merging certificates + curated data

Deliberately a separate script from pipeline.py: that module is GitHub discovery,
this one mirrors a non-GitHub registry. It imports pipeline only to reuse the
HTTP cache, the GitHub helpers and the marker injection.

Run `python csms.py <stage> --help` for stage options.
"""

import argparse
import csv
import hashlib
import json
import os
import re
import time
from collections import defaultdict

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
CSMS_MD_PATH = "csms.md"
# `render` replaces the text between these markers, so the prose around the table
# (intro, methodology, feature legend, caveats) stays hand-authored.
CSMS_MARKER_BEGIN = "<!-- BEGIN GENERATED CSMS -->"
CSMS_MARKER_END = "<!-- END GENERATED CSMS -->"

CERT_FIELDS = [
  "certificate_no", "company", "company_link", "country",
  "product_designation", "certificate_type", "software_version",
  "protocol_version", "date_of_registration", "certificate_url", "product_type",
]

# Every column of csms.csv, in file order, with the scope it carries:
#   IDENTITY — decides which entry the row lands on; `merge` handles each by hand
#   COMPANY  — a fact about the vendor, so one row can set it for all its products
#   PRODUCT  — a fact about this product only
# The overlay lists below are derived from this table, so adding a column here is
# the only edit needed; previously the same schema was restated in three places
# and a name missing from one of them was dropped silently.
IDENTITY, COMPANY, PRODUCT = "identity", "company", "product"

VENDOR_FIELDS = {
  "slug": IDENTITY, "product": IDENTITY, "company": IDENTITY,
  "oca_company": IDENTITY, "oca_product": IDENTITY,
  "open_source": IDENTITY, "repo": IDENTITY,
  "website": COMPANY, "api": COMPANY, "api_docs": COMPANY,
  "pricing": COMPANY, "pricing_url": COMPANY, "changelog": COMPANY,
  "hq_country": IDENTITY, "hq_city": COMPANY, "company_founded": COMPANY,
  "first_release": PRODUCT, "latest_version": PRODUCT,
  "latest_version_date": PRODUCT,
  "ocpp_claimed": IDENTITY, "features_claimed": IDENTITY,
  "ocpi": PRODUCT, "iso15118": PRODUCT, "eichrecht": PRODUCT,
  "license": PRODUCT, "deployment": PRODUCT,
  "status": COMPANY, "notes": COMPANY, "sources": COMPANY,
}

COMPANY_FIELDS = [f for f, scope in VENDOR_FIELDS.items() if scope == COMPANY]
OVERLAY_FIELDS = [f for f, scope in VENDOR_FIELDS.items() if scope != IDENTITY]

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

# Short labels for the Markdown table — the full names blow the column width out.
FEATURE_SHORT = {
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
}

# Stable display order, most-common first, so the column reads consistently.
FEATURE_RANK = {name: i for i, name in enumerate(FEATURE_SHORT)}


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
  """Order a feature set for display, unknown names last (alphabetically)."""
  return sorted(set(features),
                key=lambda f: (FEATURE_RANK.get(f, len(FEATURE_RANK)), f))


def unresolved_tokens(certs):
  """Certificate-type tokens no rule in derive_features recognises."""
  return sorted({t for r in certs
                 for t in derive_features(r["certificate_type"],
                                          r["protocol_version"])[1]})


# --- Product identity ---------------------------------------------------------

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


def canonical_product(company, designation):
  """Return the display name a certificate's product should be grouped under."""
  alias = PRODUCT_ALIASES.get((company or "").strip().lower(), {})
  hit = alias.get((designation or "").strip().lower())
  if hit:
    return hit
  stripped = _TRAILING_VERSION_RE.sub("", (designation or "").strip()).strip(" -–_")
  return stripped or (designation or "").strip()


# --- HTTP with on-disk cache -------------------------------------------------

def post_json_cached(url, payload, ttl=pipeline.CACHE_TTL):
  """POST a JSON body and cache the response on disk, keyed by URL + payload.

  pipeline.github_request_cached is GET-only and picks its cache extension from
  the Accept header, so the OCA endpoint needs its own helper. Shares the same
  cache directory, which is already git-ignored.
  """
  key = hashlib.md5((url + json.dumps(payload, sort_keys=True)).encode()).hexdigest()
  cache_path = os.path.join(pipeline.CACHE_DIR, key + ".json")

  if os.path.exists(cache_path) and (time.time() - os.path.getmtime(cache_path) < ttl):
    with open(cache_path, "r", encoding="utf-8") as f:
      return json.load(f)

  try:
    r = requests.post(url, json=payload, timeout=HTTP_TIMEOUT,
                      headers={"Content-Type": "application/json"})
    r.raise_for_status()
    content = r.text
    with open(cache_path, "w", encoding="utf-8") as f:
      f.write(content)
    return json.loads(content)
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

  with open(args.out, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=CERT_FIELDS)
    writer.writeheader()
    writer.writerows(rows)

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


def _key(company, product):
  """Case-insensitive join key shared by certificates and curated rows."""
  return (clean(company).lower(), clean(product).lower())


def new_entry(product, company, company_link="", country=""):
  """Blank merged-product record — the one place the entry shape is defined.

  `certified` is not stored: a product is certified exactly when it holds a
  certificate, so the list is the single source of truth.
  """
  return {
    "product": clean(product),
    "company": clean(company),
    "company_link": company_link,
    "country": country,
    "versions": set(),
    "features": set(),
    "certificates": [],
  }


def group_certificates(certs):
  """Aggregate certificates into one entry per (company, canonical product)."""
  products = {}
  for row in certs:
    product = canonical_product(row["company"], row["product_designation"])
    key = _key(row["company"], product)
    entry = products.setdefault(
      key, new_entry(product, row["company"], row["company_link"], row["country"]))

    version = row["protocol_version"].replace("OCPP", "").strip()
    entry["versions"].add(version)
    entry["features"].update(
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
  """Fill release metadata for an open-source entry from the GitHub API.

  Curated values always win, so every write here is a setdefault. A failed repo
  lookup aborts: Website, First release and Latest version exist only in this
  response for most open-source rows, and letting a rate-limit render them as
  "—" would publish a transient error as "no source we can cite".
  """
  obj = pipeline.get_repo_data(repo, headers)
  if not obj:
    raise SystemExit(f"GitHub lookup failed for {repo} — aborting rather than "
                     f"rendering its metadata as unknown. Retry, or pass --token.")

  # Deliberately not using obj["homepage"]: projects often point it at a hosted
  # commercial offering (SteVe -> powerfill.io), which would make the row read as
  # if the open-source project and the paid product were the same thing.
  entry["repo_url"] = obj.get("html_url") or f"https://github.com/{repo}"
  entry["open_source"] = True
  entry.setdefault("first_release", (obj.get("created_at") or "")[:10])

  # /releases?per_page=1 rather than /releases/latest: the latter 404s on repos
  # with no release, which is the common case here and only produces noise.
  releases = pipeline.github_request_cached(
    f"{pipeline.BASE_URL}/repos/{repo}/releases?per_page=1", headers=headers)
  release = releases[0] if isinstance(releases, list) and releases else None
  if release:
    # The releases page is the de facto changelog for a GitHub-hosted project.
    entry.setdefault("changelog", f"https://github.com/{repo}/releases")
    if release.get("tag_name"):
      entry.setdefault("latest_version", release["tag_name"])
      entry.setdefault("latest_version_date", (release.get("published_at") or "")[:10])
  # No tagged release: the last push is the closest honest proxy.
  entry.setdefault("latest_version_date", (obj.get("pushed_at") or "")[:10])


def _overlay(entry, row, fields):
  """Copy the non-empty curated values of `fields` onto an entry.

  Curated data completes what the registry gave; an empty cell never blanks a
  value, which is what lets one curated row carry only what it actually knows.
  """
  for field in fields:
    value = clean(row.get(field))
    if value:
      entry[field] = value
  country = clean(row.get("hq_country"))
  if country:
    entry["country"] = country


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
  entry["features"].update(
    f.strip() for f in clean(row.get("features_claimed")).split(",") if f.strip())
  _overlay(entry, row, OVERLAY_FIELDS)

  if clean(row.get("open_source")).lower() in ("y", "yes", "true", "1"):
    entry["open_source"] = True
  repo = clean(row.get("repo"))
  if repo:
    enrich_from_github(entry, repo, headers)


def merge(certs, vendors, headers):
  """Union the OCA registry with the curated CSV into one row per product.

  Product rows run first and company rows second, so a company-level row reaches
  every product regardless of where it sits in the file — with a single pass its
  effect depended on row order, which is invisible in a file people append to.
  """
  products = group_certificates(certs)

  # A curated row naming a company but no product carries company-level facts.
  def is_company_row(row):
    return bool(clean(row.get("oca_company")) and not clean(row.get("oca_product")))

  company_rows = [r for r in vendors if is_company_row(r)]

  for row in vendors:
    if not is_company_row(row) and clean(row.get("product")):
      _apply_product_row(products, row, headers)

  by_company = defaultdict(list)
  for (company, _), entry in products.items():
    by_company[company].append(entry)

  for row in company_rows:
    targets = by_company.get(clean(row.get("oca_company")).lower())
    if not targets:
      print(f"⚠️  {row.get('slug')}: no OCA company matches {row.get('oca_company')!r}")
      continue
    for entry in targets:
      _overlay(entry, row, COMPANY_FIELDS)

  return products


# --- Markdown ----------------------------------------------------------------

TABLE_HEADERS = [
  "Product", "Company", "HQ", "OCA-certified", "Open-source", "OCPP", "Features",
  "OCPI", "API", "Pricing", "Founded", "First release", "Latest version", "Status",
  "Website", "Certificates",
]


def _link(label, url):
  """Render a Markdown link, falling back to the bare label when there's no URL."""
  return f"[{label}]({url})" if url else (label or "")


def _host(url):
  """Shorten a URL to a readable label: the domain, or owner/repo for GitHub."""
  bare = re.sub(r"^https?://(www\.)?", "", url or "").rstrip("/")
  if bare.startswith("github.com/"):
    return "/".join(bare.split("/")[1:3])
  return bare.split("/")[0]


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


def render_row(entry):
  """Build one table row from a merged product entry."""
  site = entry.get("website") or entry.get("repo_url") or ""
  website = _link(_host(site), site)

  # "Y" only means a public API is documented; blank stays "unknown", never "no".
  api = _link(entry.get("api") or ("Y" if entry.get("api_docs") else ""),
              entry.get("api_docs"))
  pricing = _link(entry.get("pricing", ""), entry.get("pricing_url"))

  versions = ", ".join(sorted(entry["versions"], key=_version_key))
  features = " · ".join(FEATURE_SHORT.get(f, f) for f in sort_features(entry["features"]))

  def _cert_label(cert):
    label = f"{cert['version']} {cert['type']}".strip()
    return label + (f" ({cert['software']})" if cert["software"] else "")

  certificates = " · ".join(
    _link(_cert_label(c), c["url"])
    for c in sorted(entry["certificates"],
                    key=lambda c: (_version_key(c["version"]), c["date"], c["type"])))

  # The version doubles as the changelog link — no column of its own needed.
  # With a changelog but no known version, the link still carries the useful bit.
  version_text = " ".join(x for x in (entry.get("latest_version", ""),
                                      entry.get("latest_version_date", "")) if x)
  latest = _link(version_text or ("Changelog" if entry.get("changelog") else ""),
                 entry.get("changelog"))

  return [
    entry["product"] or entry["company"],
    # The registry gives an OCA participant page for most certified vendors; it
    # lists their certificates and postal address, so it earns the company link.
    _link(entry["company"], entry.get("company_link")),
    entry.get("country", ""),
    "Y" if entry["certificates"] else "N",
    "Y" if entry.get("open_source") else "N",
    versions,
    features,
    entry.get("ocpi", ""),
    api,
    pricing,
    entry.get("company_founded", ""),
    entry.get("first_release", ""),
    latest,
    entry.get("status", ""),
    website,
    certificates,
  ]


def cmd_render(args):
  """Merge the certificate mirror with the curated CSV and inject the table."""
  certs = read_csv(args.certs)
  if not certs:
    raise SystemExit(f"{args.certs} is empty or missing — run `python csms.py fetch` first.")

  # Check before any network work: an unknown token means the mapping is stale,
  # and rendering would quietly publish a product with fewer features than it has.
  unresolved = unresolved_tokens(certs)
  if unresolved:
    raise SystemExit(f"Unknown certificate-type tokens {unresolved} — update "
                     f"CERT_LETTERS in csms.py rather than rendering empty features.")

  vendors = read_csv(args.vendors, fields=VENDOR_FIELDS)
  products = merge(certs, vendors, pipeline.auth_headers(args.token))

  entries = sorted(products.values(), key=lambda e: (e["product"] or e["company"]).lower())
  body = "\n".join(md_table(TABLE_HEADERS, [render_row(e) for e in entries]))
  pipeline._inject_between_markers(args.md, body, CSMS_MARKER_BEGIN, CSMS_MARKER_END)

  certified = sum(1 for e in entries if e["certificates"])
  oss = sum(1 for e in entries if e.get("open_source"))
  both = sum(1 for e in entries if e["certificates"] and e.get("open_source"))
  print(f"✅ {len(entries)} products · {certified} OCA-certified · {oss} open-source · "
        f"{both} both -> {args.md}")


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

  p_render = sub.add_parser("render", help="Render the merged CSMS table into csms.md.")
  p_render.add_argument("--certs", default=CERTS_PATH, help="Certificate CSV path.")
  p_render.add_argument("--vendors", default=VENDORS_PATH, help="Curated CSV path.")
  p_render.add_argument("--md", default=CSMS_MD_PATH, help="Markdown file to inject into.")
  p_render.add_argument("--token", help="GitHub personal access token (optional).")
  p_render.set_defaults(func=cmd_render)

  args = parser.parse_args()
  args.func(args)


if __name__ == "__main__":
  main()
