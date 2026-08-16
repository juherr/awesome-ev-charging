"""Tests for the CSMS catalogue.

Nothing here reaches the network: the only outbound call `merge` can make is
`enrich_from_github`, and the one test that exercises it stubs the GitHub layer.
The last section validates the committed dataset, so a bad curated row fails
here as well as at render time.
"""

import csv

import pytest

import csms


# --- Fixtures -----------------------------------------------------------------

def cert(company="Acme Ltd", product="Acme CSMS", type_="Core + S",
         version="OCPP 2.0.1", software="1.0", number="OCA.1", url="https://oca/1.pdf",
         link="https://oca/acme", country="France", date="2024-01-01"):
  """One row shaped like csms-certificates.csv, every column present."""
  row = {field: "" for field in csms.CERT_FIELDS}
  row.update(certificate_no=number, company=company, company_link=link,
             country=country, product_designation=product, certificate_type=type_,
             software_version=software, protocol_version=version,
             date_of_registration=date, certificate_url=url,
             product_type=csms.OCA_PRODUCT_TYPE)
  return row


def vendor(**overrides):
  """One row shaped like csms.csv, every column present and empty by default."""
  row = {field: "" for field in csms.VENDOR_FIELDS}
  row.update(overrides)
  return row


def render(certs=(), vendors=(), claims=None):
  """Merge and render, the way cmd_render does, without touching the filesystem."""
  products = csms.merge(list(certs), list(vendors), {}, claims)
  return csms.sort_entries(products)


def directory_row(entries, index=0):
  """One rendered directory row, keyed by column name."""
  return dict(zip(csms.TABLE_HEADERS, csms.render_row(entries[index])))


def feature_row(entries, index=0):
  """One rendered annex row, keyed by column name."""
  return dict(zip(csms.FEATURE_TABLE_HEADERS, csms.render_feature_row(entries[index])))


def stub_github(monkeypatch, **repo_fields):
  """Answer enrich_from_github's only call without touching the network."""
  monkeypatch.setattr(csms.pipeline, "get_repo_data",
                      lambda repo, headers: {"html_url": f"https://github.com/{repo}",
                                             **repo_fields})


def write_features(tmp_path, rows):
  path = tmp_path / "features.csv"
  with open(path, "w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=csms.FEATURE_FIELDS)
    writer.writeheader()
    writer.writerows(rows)
  return str(path)


# --- Controlled vocabulary ----------------------------------------------------

def test_certificate_rules_only_emit_vocabulary_names():
  """CERT_LETTERS and OCPP16_FULL are edited independently of FEATURE_VOCAB."""
  assert csms.vocabulary_gaps() == []


def test_every_derived_feature_is_renderable():
  """render_feature_row indexes FEATURE_VOCAB directly, so a gap is a KeyError."""
  types = ["Full", "Core", "Security", "Core + S", "S + L + C + D + R + U + I"]
  for certificate_type in types:
    for protocol in ("OCPP 1.6", "OCPP 2.0.1"):
      features, _ = csms.derive_features(certificate_type, protocol)
      assert all(f in csms.FEATURE_VOCAB for f in features), (certificate_type, protocol)


# --- derive_features ----------------------------------------------------------

def test_letters_expand_through_the_oca_legend():
  features, unresolved = csms.derive_features("Core + S + C", "OCPP 2.0.1")
  assert unresolved == []
  assert set(features) == {"Core", "Advanced Security", "Smart Charging"}


def test_full_on_ocpp_16_expands_to_the_six_feature_profiles():
  features, unresolved = csms.derive_features("Full", "OCPP 1.6")
  assert unresolved == []
  assert features == csms.OCPP16_FULL


def test_full_on_ocpp_201_stays_unresolved():
  """Deliberate: guessing an expansion would publish it as if it were derived."""
  features, unresolved = csms.derive_features("Full", "OCPP 2.0.1")
  assert features == []
  assert unresolved == ["Full"]


def test_scope_qualifiers_contribute_no_features():
  assert csms.derive_features("Subset + Family", "OCPP 1.6") == ([], [])


def test_unknown_token_is_reported_rather_than_ignored():
  _, unresolved = csms.derive_features("Core + Z", "OCPP 2.0.1")
  assert unresolved == ["Z"]


def test_unresolved_tokens_scans_every_certificate():
  assert csms.unresolved_tokens([cert(type_="Core"), cert(type_="Q")]) == ["Q"]


# --- Product and company identity ---------------------------------------------

def test_trailing_dotted_version_is_stripped():
  assert csms.canonical_product("X", "eBAB Server v1.6") == "eBAB Server"
  assert csms.canonical_product("X", "eBAB Server v1.6.1") == "eBAB Server"


def test_model_number_without_a_dot_survives():
  assert csms.canonical_product("X", "MON-CSMS-V10") == "MON-CSMS-V10"


def test_alias_table_merges_a_renamed_platform():
  assert csms.canonical_product("NEC Corporation", "N-CSMS16") == "N-CSMS"
  assert csms.canonical_product("NEC Corporation", "N-CSMS20") == "N-CSMS"


def test_company_spelling_variants_group_as_one_vendor():
  assert csms.company_key("Shenzhen Infypower Co. Ltd") == \
         csms.company_key("Shenzhen Infypower Co., Ltd")
  assert csms.company_key("Instituto Tecnológico de la Energía (ITE)") == \
         csms.company_key("Instituto Tecnológico de la Energía")


def test_legal_suffixes_still_distinguish_companies():
  assert csms.company_key("Everon") != csms.company_key("Everon Co Ltd")


# --- merge --------------------------------------------------------------------

def test_certificates_group_into_one_entry_per_product():
  entries = render(certs=[cert(number="A", type_="Core"),
                          cert(number="B", type_="Core + S", version="OCPP 1.6")])
  assert len(entries) == 1
  assert len(entries[0]["certificates"]) == 2
  assert entries[0]["versions"] == {"1.6", "2.0.1"}


def test_curated_row_completes_a_certified_product_without_replacing_it():
  entries = render(
    certs=[cert()],
    vendors=[vendor(slug="acme", product="Acme CSMS", company="Acme Ltd",
                    oca_company="Acme Ltd", oca_product="Acme CSMS",
                    website="https://acme.example", deployment="saas")])
  assert len(entries) == 1
  assert entries[0]["certificates"], "the certificate must survive the overlay"
  assert entries[0]["website"] == "https://acme.example"


def test_empty_curated_cell_never_blanks_a_registry_value():
  entries = render(certs=[cert(link="https://oca/acme")],
                   vendors=[vendor(slug="acme", product="Acme CSMS",
                                   company="Acme Ltd", oca_company="Acme Ltd",
                                   oca_product="Acme CSMS")])
  assert entries[0]["company_link"] == "https://oca/acme"


def test_company_row_fills_gaps_but_never_overrides_a_product_row():
  entries = render(
    certs=[cert(product="One", number="1"), cert(product="Two", number="2")],
    vendors=[
      vendor(slug="one", product="One", company="Acme Ltd", oca_company="Acme Ltd",
             oca_product="One", website="https://one.example"),
      vendor(slug="acme-co", oca_company="Acme Ltd", website="https://acme.example",
             company_founded="2011"),
    ])
  by_product = {e["product"]: e for e in entries}
  assert by_product["One"]["website"] == "https://one.example"   # product wins
  assert by_product["Two"]["website"] == "https://acme.example"  # company fills
  assert by_product["One"]["company_founded"] == "2011"          # gap filled


def test_curated_row_reaches_the_entry_through_the_merged_product_name():
  """A contributor may cite the raw OCA designation or the merged display name."""
  entries = render(certs=[cert(product="Acme CSMS v2.1")],
                   vendors=[vendor(slug="acme", product="Acme", company="Acme Ltd",
                                   oca_company="Acme Ltd",
                                   oca_product="Acme CSMS v2.1", status="active")])
  assert len(entries) == 1
  assert entries[0]["status"] == "active"


def test_a_curated_repo_makes_the_product_source_available(monkeypatch):
  stub_github(monkeypatch)
  entries = render(vendors=[vendor(slug="steve", product="SteVe", company="Community",
                                   repo="steve-community/steve",
                                   first_release="2013-01-01")])
  assert entries[0]["source_available"] is True
  assert entries[0]["repo_url"] == "https://github.com/steve-community/steve"
  # Curated values are never overwritten by the lookup.
  assert entries[0]["first_release"] == "2013-01-01"


def test_an_unreachable_repo_aborts_rather_than_reading_as_no_source(monkeypatch):
  monkeypatch.setattr(csms.pipeline, "get_repo_data", lambda repo, headers: None)
  with pytest.raises(SystemExit, match="GitHub lookup failed"):
    render(vendors=[vendor(slug="steve", product="SteVe", company="Community",
                           repo="steve-community/steve")])


# --- Curated features: reading and validation ---------------------------------

def test_features_are_read_into_slug_feature_sources(tmp_path):
  """Sources are sorted here, once — _sourced links the label to the first one."""
  path = write_features(tmp_path, [
    {"slug": "acme", "feature": "Tariffs", "source_url": "https://b", "note": ""},
    {"slug": "acme", "feature": "Tariffs", "source_url": "https://a", "note": ""},
  ])
  assert csms.read_features(path, {"acme"}) == {"acme": {"Tariffs": ["https://a", "https://b"]}}


def test_source_order_survives_the_merge(tmp_path):
  """merge must not re-order what read_features already decided."""
  claims = {"acme": {"Tariffs": ["https://a", "https://b"]}}
  entries = render(vendors=[vendor(slug="acme", product="Acme", company="Acme Ltd")],
                   claims=claims)
  assert entries[0]["features_claimed"]["Tariffs"] == ["https://a", "https://b"]


def test_duplicate_source_for_one_feature_is_collapsed(tmp_path):
  path = write_features(tmp_path, [
    {"slug": "acme", "feature": "Tariffs", "source_url": "https://a", "note": "x"},
    {"slug": "acme", "feature": "Tariffs", "source_url": "https://a", "note": "y"},
  ])
  assert csms.read_features(path, {"acme"}) == {"acme": {"Tariffs": ["https://a"]}}


def test_feature_outside_the_vocabulary_fails_the_render(tmp_path):
  path = write_features(tmp_path, [
    {"slug": "acme", "feature": "Blazing Fast Charging", "source_url": "https://a",
     "note": ""}])
  with pytest.raises(SystemExit, match="controlled vocabulary"):
    csms.read_features(path, {"acme"})


def test_feature_without_a_source_fails_the_render(tmp_path):
  path = write_features(tmp_path, [
    {"slug": "acme", "feature": "Tariffs", "source_url": "", "note": "trust me"}])
  with pytest.raises(SystemExit, match="source_url"):
    csms.read_features(path, {"acme"})


def test_feature_for_an_unknown_product_fails_the_render(tmp_path):
  path = write_features(tmp_path, [
    {"slug": "ghost", "feature": "Tariffs", "source_url": "https://a", "note": ""}])
  with pytest.raises(SystemExit, match="no product row"):
    csms.read_features(path, {"acme"})


def test_every_problem_is_reported_in_one_pass(tmp_path):
  path = write_features(tmp_path, [
    {"slug": "acme", "feature": "Nope", "source_url": "https://a", "note": ""},
    {"slug": "ghost", "feature": "Tariffs", "source_url": "", "note": ""}])
  with pytest.raises(SystemExit) as raised:
    csms.read_features(path, {"acme"})
  message = str(raised.value)
  assert "controlled vocabulary" in message
  assert "no product row" in message
  assert "source_url" in message


def test_duplicate_product_slug_fails_before_any_feature_is_attached():
  rows = [vendor(slug="acme", product="One"), vendor(slug="acme", product="Two")]
  with pytest.raises(SystemExit, match="duplicate slug"):
    csms.product_slugs(rows)


def test_row_without_a_slug_fails():
  with pytest.raises(SystemExit, match="without a slug"):
    csms.product_slugs([vendor(product="One")])


def test_company_rows_are_not_feature_targets():
  """Features describe a product, so a company-level slug must not accept one."""
  rows = [vendor(slug="acme", product="One", company="Acme Ltd"),
          vendor(slug="acme-co", oca_company="Acme Ltd")]
  assert csms.product_slugs(rows) == {"acme"}


# --- Curated features: provenance ---------------------------------------------

def test_certified_and_vendor_documented_features_stay_separate():
  entries = render(
    certs=[cert(type_="Core + S")],
    vendors=[vendor(slug="acme", product="Acme CSMS", company="Acme Ltd",
                    oca_company="Acme Ltd", oca_product="Acme CSMS")],
    claims={"acme": {"Tariffs": ["https://acme.example/tariffs"]}})
  entry = entries[0]
  assert entry["features_certified"] == {"Core", "Advanced Security"}
  assert entry["features_claimed"] == {"Tariffs": ["https://acme.example/tariffs"]}


def test_a_feature_can_be_both_certified_and_documented():
  entries = render(
    certs=[cert(type_="Core")],
    vendors=[vendor(slug="acme", product="Acme CSMS", company="Acme Ltd",
                    oca_company="Acme Ltd", oca_product="Acme CSMS")],
    claims={"acme": {"Core": ["https://acme.example/docs"]}})
  row = feature_row(entries)
  assert row["Certified (OCA)"] == "Core"
  assert row["Vendor-documented"] == "[Core](https://acme.example/docs)"


def test_vendor_documented_feature_carries_its_source_link():
  entries = render(vendors=[vendor(slug="acme", product="Acme", company="Acme Ltd")],
                   claims={"acme": {"Smart Charging": ["https://acme.example/sc"]}})
  assert feature_row(entries)["Vendor-documented"] == \
         "[Smart Charging](https://acme.example/sc)"


def test_further_sources_stay_reachable():
  entries = render(vendors=[vendor(slug="acme", product="Acme", company="Acme Ltd")],
                   claims={"acme": {"Tariffs": ["https://one", "https://two"]}})
  assert feature_row(entries)["Vendor-documented"] == \
         "[Tariffs](https://one) [2](https://two)"


def test_no_evidence_renders_as_an_empty_cell_on_both_sides():
  entries = render(vendors=[vendor(slug="acme", product="Acme", company="Acme Ltd")])
  row = feature_row(entries)
  assert (row["Certified (OCA)"], row["Vendor-documented"]) == ("", "")


# --- The directory table ------------------------------------------------------

def test_table_shape_matches_the_header():
  entries = render(certs=[cert()])
  assert len(csms.render_row(entries[0])) == len(csms.TABLE_HEADERS)
  assert len(csms.render_feature_row(entries[0])) == len(csms.FEATURE_TABLE_HEADERS)


def test_the_oca_certified_boolean_is_gone():
  assert "OCA-certified" not in csms.TABLE_HEADERS
  assert "OCA certificates" in csms.TABLE_HEADERS


def test_source_available_is_never_rendered_as_no():
  """Empty means "we found no repository", not "the source is closed"."""
  entries = render(certs=[cert()])
  row = directory_row(entries)
  assert row["Source available"] == ""


def test_source_available_links_to_the_repository(monkeypatch):
  stub_github(monkeypatch)
  entries = render(vendors=[vendor(slug="steve", product="SteVe", company="Community",
                                   repo="steve-community/steve")])
  row = directory_row(entries)
  assert row["Source available"] == "[Y](https://github.com/steve-community/steve)"


def test_product_name_carries_the_website_link():
  entries = render(vendors=[vendor(slug="acme", product="Acme", company="Acme Ltd",
                                   website="https://acme.example")])
  row = directory_row(entries)
  assert row["Product"] == "[Acme](https://acme.example)"


@pytest.mark.parametrize("api,api_docs,expected", [
  ("Y", "https://acme.example/api", "[Y](https://acme.example/api)"),
  # An API attested by a source but documented behind a login is still a Y.
  ("Y", "", "Y"),
  # Empty means unverified, never "no API".
  ("", "", ""),
], ids=["public docs", "login-gated", "unverified"])
def test_the_api_cell_separates_existence_from_public_documentation(api, api_docs,
                                                                    expected):
  entries = render(vendors=[vendor(slug="acme", product="Acme", company="Acme Ltd",
                                   api=api, api_docs=api_docs)])
  assert directory_row(entries)["API"] == expected


def test_ocpi_is_derived_from_a_curated_feature():
  entries = render(vendors=[vendor(slug="acme", product="Acme", company="Acme Ltd")],
                   claims={"acme": {csms.OCPI_FEATURE: ["https://acme.example/ocpi"]}})
  row = directory_row(entries)
  assert row["OCPI"] == "[Y](https://acme.example/ocpi)"


def test_ocpi_column_alone_still_renders():
  entries = render(vendors=[vendor(slug="acme", product="Acme", company="Acme Ltd",
                                   ocpi="Y")])
  row = directory_row(entries)
  assert row["OCPI"] == "Y"


def test_certificate_cell_exposes_version_type_software_and_link():
  entries = render(certs=[cert(type_="Core + S", version="OCPP 2.0.1",
                               software="1.5.1", url="https://oca/x.pdf")])
  row = directory_row(entries)
  assert row["OCA certificates"] == "[2.0.1 Core + S (1.5.1)](https://oca/x.pdf)"


def test_every_certificate_of_a_merged_product_is_listed():
  entries = render(certs=[cert(product="Acme v1.6", number="1", version="OCPP 1.6",
                               type_="Full", url="https://oca/1.pdf"),
                          cert(product="Acme v2.0", number="2", version="OCPP 2.0.1",
                               type_="Core", url="https://oca/2.pdf")])
  row = directory_row(entries)
  assert "https://oca/1.pdf" in row["OCA certificates"]
  assert "https://oca/2.pdf" in row["OCA certificates"]


def test_missing_certificate_renders_as_a_dash_not_as_a_failure():
  entries = render(vendors=[vendor(slug="acme", product="Acme", company="Acme Ltd")])
  lines = csms.md_table(csms.TABLE_HEADERS, [csms.render_row(entries[0])])
  assert "| — |" in lines[-1]


# --- Determinism --------------------------------------------------------------

def test_rendering_twice_gives_the_same_bytes():
  certs = [cert(product="B", number="1"), cert(product="A", number="2")]
  vendors = [vendor(slug="c", product="C", company="Acme Ltd")]
  first = csms.md_table(csms.TABLE_HEADERS,
                        [csms.render_row(e) for e in render(certs, vendors)])
  second = csms.md_table(csms.TABLE_HEADERS,
                         [csms.render_row(e) for e in render(certs, vendors)])
  assert first == second


def test_ordering_does_not_depend_on_input_order():
  certs = [cert(product="B", number="1"), cert(product="A", number="2"),
           cert(product="C", number="3")]
  forward = [e["product"] for e in render(certs)]
  backward = [e["product"] for e in render(list(reversed(certs)))]
  assert forward == backward == ["A", "B", "C"]


def test_same_product_name_from_two_vendors_has_a_stable_order():
  entries = render(certs=[cert(company="Zeta Ltd", product="CSMS", number="1",
                               link="https://oca/z"),
                          cert(company="Alpha Ltd", product="CSMS", number="2",
                               link="https://oca/a")])
  assert [e["company"] for e in entries] == ["Alpha Ltd", "Zeta Ltd"]


def test_pipes_in_a_value_cannot_break_the_table():
  assert csms.clean("a | b") == r"a \| b"


# --- The committed dataset ----------------------------------------------------

def test_committed_dataset_validates():
  """The same checks `render` runs, so a bad curated row fails in CI too."""
  vendors = csms.read_csv(csms.VENDORS_PATH, fields=csms.VENDOR_FIELDS)
  assert vendors, "csms.csv should not be empty"
  slugs = csms.product_slugs(vendors)
  claims = csms.read_features(csms.FEATURES_PATH, slugs)
  assert claims, "csms-features.csv should carry at least one curated feature"


def test_committed_certificate_mirror_has_no_unknown_tokens():
  certs = csms.read_csv(csms.CERTS_PATH, fields=csms.CERT_FIELDS)
  assert certs, "csms-certificates.csv should not be empty"
  assert csms.unresolved_tokens(certs) == []


def committed_body(path, begin_marker, end_marker):
  """The generated block of a deliverable, exactly as `cmd_render` writes it."""
  with open(path, "r", encoding="utf-8") as f:
    content = f.read()
  begin = content.index(begin_marker) + len(begin_marker)
  return content[begin:content.index(end_marker)].strip("\n")


def test_committed_markdown_matches_a_fresh_render(monkeypatch):
  """The CSVs are canonical and the Markdown is only a view of them.

  Without this, a PR editing a curated row but forgetting to re-render merges
  green and the published tables disagree with their own source until the
  monthly refresh job notices. The GitHub stub answers for every curated repo,
  so the test asserts the render is reproducible — not that the repos still
  exist, which is the refresh job's business and needs the network.
  """
  stub_github(monkeypatch)
  certs = csms.read_csv(csms.CERTS_PATH, fields=csms.CERT_FIELDS)
  vendors = csms.read_csv(csms.VENDORS_PATH, fields=csms.VENDOR_FIELDS)
  claims = csms.read_features(csms.FEATURES_PATH, csms.product_slugs(vendors))
  entries = csms.sort_entries(csms.merge(certs, vendors, {}, claims))
  directory, annex = csms.render_bodies(entries)

  assert directory == committed_body(csms.CSMS_MD_PATH, csms.CSMS_MARKER_BEGIN,
                                     csms.CSMS_MARKER_END), \
    "csms.md is stale — re-run `python csms.py render`"
  assert annex == committed_body(csms.FEATURES_MD_PATH, csms.FEATURES_MARKER_BEGIN,
                                 csms.FEATURES_MARKER_END), \
    "csms-features.md is stale — re-run `python csms.py render`"
