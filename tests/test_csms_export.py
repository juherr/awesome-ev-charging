"""The public `csms.json` written by `csms.py render --export-dir`.

The fixture tests build entries in memory, like tests/test_csms.py, and stub
the one GitHub call `merge` can make. The last section checks the committed
`data/csms.json` and its manifest entry against a fresh export of the
committed CSVs, so a curated edit merged without a re-render fails here.
"""

import csv
import json
import os
import subprocess
import sys
import types

import pytest

import csms
import pipeline
from test_csms import cert, stub_github, vendor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSMS_JSON = os.path.join("data", csms.CSMS_EXPORT)
MANIFEST_JSON = os.path.join("data", pipeline.MANIFEST_EXPORT)


def export(certs=(), vendors=(), claims=None):
  """The payload `cmd_render` would write, built without touching the filesystem."""
  return csms.csms_payload(csms.merge(list(certs), list(vendors), {}, claims))


def records(certs=(), vendors=(), claims=None):
  return {p["id"]: p for p in export(certs, vendors, claims)["products"]}


def only(certs=(), vendors=(), claims=None):
  (record,) = export(certs, vendors, claims)["products"]
  return record


# --- The record ---------------------------------------------------------------

EXPORTED_FIELDS = {
  "id", "name", "company", "oca_company_url", "website", "repo", "repo_url",
  "source_available", "ocpp_versions", "certificates", "features_certified",
  "features_documented", "ocpi", "iso15118", "eichrecht", "api", "api_docs",
  "pricing", "pricing_url", "changelog", "hq_country", "hq_city",
  "company_founded", "first_release", "latest_version", "latest_version_date",
  "license", "deployment", "status", "notes", "sources",
}


def test_the_payload_has_a_schema_version_and_a_fixed_field_set():
  payload = export([cert()])
  assert set(payload) == {"schema_version", "products"}
  assert payload["schema_version"] == pipeline.PUBLIC_SCHEMA_VERSION
  assert set(payload["products"][0]) == EXPORTED_FIELDS


def test_an_unknown_value_is_null_never_false_or_empty():
  record = only([cert(link="")])
  for field in EXPORTED_FIELDS - {"id", "name", "company", "certificates",
                                  "features_certified", "features_documented",
                                  "sources", "ocpp_versions"}:
    assert record[field] is None, field
  assert record["sources"] == []
  assert record["features_documented"] == []


def test_a_curated_product_keeps_its_slug_as_id():
  record = only(vendors=[vendor(slug="my-csms", product="My CSMS", company="Me")])
  assert record["id"] == "my-csms"
  assert record["name"] == "My CSMS"
  assert record["company"] == "Me"


def test_a_certified_only_product_gets_a_derived_stable_id():
  record = only([cert(company="Acme Co., Ltd.", product="Acme CSMS v1.2")])
  assert record["id"] == "acme-co-ltd-acme-csms"
  # The same product spelt the other way by the registry keeps the same id.
  assert only([cert(company="Acme Co Ltd", product="Acme CSMS v1.3")])["id"] == record["id"]


def test_a_derived_id_folds_accents_but_keeps_other_scripts():
  assert only([cert(company="Instituto Tecnológico", product="Sistema")])["id"] \
    == "instituto-tecnologico-sistema"
  assert only([cert(company="充电公司", product="平台")])["id"] == "充电公司-平台"


def test_a_certified_product_with_a_curated_row_takes_the_slug():
  record = only([cert()], [vendor(slug="acme", product="Acme CSMS", company="Acme Ltd",
                                  oca_company="Acme Ltd", oca_product="Acme CSMS")])
  assert record["id"] == "acme"


def test_a_derived_id_colliding_with_a_curated_slug_fails():
  with pytest.raises(SystemExit, match="acme-ltd-acme-csms") as error:
    export([cert()], [vendor(slug="acme-ltd-acme-csms", product="Other", company="Else")])
  assert "rename the curated slug" in str(error.value)


def test_two_colliding_derived_ids_ask_for_a_slug_or_an_alias():
  # `Acme_CSMS` and `Acme-CSMS` are two merge keys but fold to one derived id.
  with pytest.raises(SystemExit, match="acme-ltd-acme-csms") as error:
    export([cert(product="Acme_CSMS", number="OCA.1"),
            cert(product="Acme-CSMS", number="OCA.2")])
  message = str(error.value)
  assert "rename the curated slug" not in message
  assert "slug" in message and "PRODUCT_ALIASES" in message


def test_two_curated_rows_landing_on_one_entry_fail():
  rows = [vendor(slug=slug, product="Acme CSMS", company="Acme Ltd",
                 oca_company="Acme Ltd", oca_product="Acme CSMS")
          for slug in ("first", "second")]
  with pytest.raises(SystemExit, match="first.*second|second.*first"):
    csms.merge([cert()], rows, {})


def test_products_are_sorted_by_id():
  ids = [p["id"] for p in export(vendors=[
    vendor(slug=s, product=s.upper(), company="C") for s in ("b", "c", "a")])["products"]]
  assert ids == ["a", "b", "c"]


# --- Fields from the committed CSVs only ----------------------------------------

def test_the_repo_url_is_built_from_the_curated_repo_not_githubs_answer(monkeypatch):
  stub_github(monkeypatch, html_url="https://github.com/Renamed/elsewhere")
  record = only(vendors=[vendor(slug="steve", product="SteVe", company="community",
                                repo="steve-community/steve")])
  assert record["repo"] == "steve-community/steve"
  assert record["repo_url"] == "https://github.com/steve-community/steve"
  assert record["source_available"] is True


def test_source_available_is_true_or_null():
  products = records(vendors=[
    vendor(slug="open", product="Open", company="C", source_available="Y"),
    vendor(slug="closed", product="Closed", company="C")])
  assert products["open"]["source_available"] is True
  assert products["closed"]["source_available"] is None


def test_y_columns_become_true_or_null():
  products = records(vendors=[
    vendor(slug="yes", product="Yes", company="C", api="Y", ocpi="Y", iso15118="Y",
           eichrecht="Y"),
    vendor(slug="unknown", product="Unknown", company="C")])
  for field in ("api", "ocpi", "iso15118", "eichrecht"):
    assert products["yes"][field] is True, field
    assert products["unknown"][field] is None, field


def test_an_unexpected_value_in_a_y_column_fails_rather_than_guessing():
  with pytest.raises(SystemExit, match="iso15118"):
    export(vendors=[vendor(slug="x", product="X", company="C", iso15118="N")])


def test_api_and_ocpi_follow_the_directory_columns():
  """A public API doc or a documented OCPI feature is what makes those cells `Y`."""
  record = only(vendors=[vendor(slug="x", product="X", company="C",
                                api_docs="https://docs.example/api")],
                claims={"x": {csms.OCPI_FEATURE: ["https://example/ocpi"]}})
  assert record["api"] is True
  assert record["api_docs"] == "https://docs.example/api"
  assert record["ocpi"] is True


def test_free_text_columns_are_copied():
  record = only(vendors=[vendor(
    slug="x", product="X", company="C", website="https://x.example", pricing="On request",
    pricing_url="https://x.example/pricing", changelog="https://x.example/changes",
    hq_country="France", hq_city="Paris", company_founded="2019", first_release="2020",
    latest_version="3.1", latest_version_date="2026-01-01", license="BUSL-1.1",
    deployment="saas", status="active", notes="A note.")])
  assert record == record | {
    "website": "https://x.example", "pricing": "On request",
    "pricing_url": "https://x.example/pricing", "changelog": "https://x.example/changes",
    "hq_country": "France", "hq_city": "Paris", "company_founded": "2019",
    "first_release": "2020", "latest_version": "3.1", "latest_version_date": "2026-01-01",
    "license": "BUSL-1.1", "deployment": "saas", "status": "active", "notes": "A note."}


def test_the_markdown_pipe_escape_does_not_reach_the_json():
  record = only(vendors=[vendor(slug="x", product="X", company="C", notes="a | b")])
  assert record["notes"] == "a | b"


def test_sources_are_split_in_file_order():
  record = only(vendors=[vendor(slug="x", product="X", company="C",
                                sources="https://b.example  https://a.example")])
  assert record["sources"] == ["https://b.example", "https://a.example"]


def test_a_company_row_fills_its_products():
  record = only([cert()], [vendor(slug="acme-co", oca_company="Acme Ltd",
                                  hq_country="France", sources="https://acme.example")])
  assert record["hq_country"] == "France"
  assert record["sources"] == ["https://acme.example"]


# --- Certificates, versions and the two kinds of evidence -------------------------

def test_versions_are_sorted_numerically_and_include_claimed_ones():
  record = only([cert(version="OCPP 2.0.1"), cert(version="OCPP 1.6", number="OCA.2")],
                [vendor(slug="acme", product="Acme CSMS", company="Acme Ltd",
                        oca_company="Acme Ltd", oca_product="Acme CSMS",
                        ocpp_claimed="2.1, 1.10, 1.5")])
  assert record["ocpp_versions"] == ["1.5", "1.6", "1.10", "2.0.1", "2.1"]


def test_certificates_are_exported_in_a_deterministic_order():
  certs = [cert(version="OCPP 2.0.1", number="OCA.3", date="2024-01-01", software=""),
           cert(version="OCPP 1.6", number="OCA.2", date="2025-01-01", type_="Full"),
           cert(version="OCPP 1.6", number="OCA.1", date="2023-01-01", type_="Core")]
  first = only(certs)["certificates"]
  assert [c["number"] for c in first] == ["OCA.1", "OCA.2", "OCA.3"]
  assert first[0] == {"number": "OCA.1", "ocpp_version": "1.6", "type": "Core",
                      "software_version": "1.0", "date": "2023-01-01",
                      "url": "https://oca/1.pdf"}
  assert first[2]["software_version"] is None
  assert only(list(reversed(certs)))["certificates"] == first


def test_certified_and_documented_features_stay_apart():
  record = only([cert(type_="Core + S + C")],
                [vendor(slug="acme", product="Acme CSMS", company="Acme Ltd",
                        oca_company="Acme Ltd", oca_product="Acme CSMS")],
                claims={"acme": {"Reservation": ["https://b", "https://a"],
                                 "Advanced Security": ["https://s"]}})
  assert record["features_certified"] == csms.sort_features(
    ["Core", "Advanced Security", "Smart Charging"])
  assert record["features_documented"] == [
    {"feature": f, "source_urls": urls}
    for f, urls in (("Advanced Security", ["https://s"]),
                    ("Reservation", ["https://a", "https://b"]))]


# --- The CLI flag ------------------------------------------------------------------

def _write_csv(path, fields, rows):
  with open(path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)


def render_files(tmp_path, export_dir=None, vendor_rows=()):
  """Run cmd_render on fixture files in `tmp_path`, returning the args."""
  _write_csv(tmp_path / "certs.csv", csms.CERT_FIELDS, [cert()])
  _write_csv(tmp_path / "vendors.csv", csms.VENDOR_FIELDS, vendor_rows)
  features = tmp_path / "features.csv"
  features.write_text(",".join(csms.FEATURE_FIELDS) + "\n", encoding="utf-8")
  for name, begin, end in (("csms.md", csms.CSMS_MARKER_BEGIN, csms.CSMS_MARKER_END),
                           ("features.md", csms.FEATURES_MARKER_BEGIN,
                            csms.FEATURES_MARKER_END)):
    (tmp_path / name).write_text(f"# T\n\n{begin}\n{end}\n", encoding="utf-8")
  args = types.SimpleNamespace(certs="certs.csv", vendors="vendors.csv",
                               features="features.csv", md="csms.md",
                               features_md="features.md", token=None,
                               export_dir=export_dir)
  csms.cmd_render(args)
  return args


def test_render_without_the_flag_writes_no_json(tmp_path, monkeypatch):
  monkeypatch.chdir(tmp_path)
  render_files(tmp_path)
  assert not (tmp_path / "data").exists()
  assert sorted(p.name for p in tmp_path.iterdir()) == [
    "certs.csv", "csms.md", "features.csv", "features.md", "vendors.csv"]


def warnings_in(capsys):
  return [line for line in capsys.readouterr().out.splitlines() if "⚠️" in line]


def test_render_warns_when_a_curated_slug_makes_a_published_id_disappear(
    tmp_path, monkeypatch, capsys):
  monkeypatch.chdir(tmp_path)
  render_files(tmp_path, "data")
  assert warnings_in(capsys) == []
  render_files(tmp_path, "data", vendor_rows=[vendor(
    slug="acme", product="Acme CSMS", company="Acme Ltd", oca_company="Acme Ltd",
    oca_product="Acme CSMS")])
  warnings = warnings_in(capsys)
  assert len(warnings) == 1
  assert "acme-ltd-acme-csms" in warnings[0] and "'acme'" not in warnings[0]


def test_disappeared_ids_are_sorted_and_new_ids_are_not_reported(tmp_path):
  previous = tmp_path / "csms.json"
  previous.write_text(json.dumps({"products": [{"id": "b"}, {"id": "kept"}, {"id": "a"}]}),
                      encoding="utf-8")
  payload = {"products": [{"id": "kept"}, {"id": "new"}]}
  assert csms.disappeared_ids(str(previous), payload) == ["a", "b"]


def test_render_without_a_previous_export_warns_nothing(tmp_path, monkeypatch, capsys):
  monkeypatch.chdir(tmp_path)
  render_files(tmp_path, "data")
  assert warnings_in(capsys) == []
  (tmp_path / "data" / "csms.json").write_text("{not json", encoding="utf-8")
  render_files(tmp_path, "data")
  assert warnings_in(capsys) == []


def test_the_markdown_is_identical_with_and_without_the_flag(tmp_path, monkeypatch):
  for name, export_dir in (("plain", None), ("export", "data")):
    (tmp_path / name).mkdir()
    monkeypatch.chdir(tmp_path / name)
    render_files(tmp_path / name, export_dir)
  for md in ("csms.md", "features.md"):
    assert (tmp_path / "plain" / md).read_bytes() == (tmp_path / "export" / md).read_bytes()


def test_render_with_the_flag_writes_the_payload_and_its_manifest_entry(tmp_path, monkeypatch):
  monkeypatch.chdir(tmp_path)
  (tmp_path / "data").mkdir()
  (tmp_path / "data" / "manifest.json").write_text(pipeline.dump_public_json(
    {"schema_version": "1.0", "payloads": {"projects": {"kept": True}}}), encoding="utf-8")
  render_files(tmp_path, "data")

  payload = (tmp_path / "data" / "csms.json").read_text(encoding="utf-8")
  assert payload == pipeline.dump_public_json(json.loads(payload))
  manifest = json.loads((tmp_path / "data" / "manifest.json").read_text(encoding="utf-8"))
  assert manifest["payloads"]["projects"] == {"kept": True}
  entry = manifest["payloads"]["csms"]
  assert entry["file"] == "csms.json"
  assert entry["records"] == 1
  assert entry["sha256"] == pipeline._sha256(str(tmp_path / "data" / "csms.json"))
  assert sorted(entry["inputs"]) == ["certs.csv", "features.csv", "vendors.csv"]


# --- The committed export ------------------------------------------------------------

def fresh_committed_payload(monkeypatch):
  """Export the committed CSVs the way `csms.py render` does, with GitHub stubbed."""
  stub_github(monkeypatch)
  certs = csms.read_csv(csms.CERTS_PATH, fields=csms.CERT_FIELDS)
  vendors = csms.read_csv(csms.VENDORS_PATH, fields=csms.VENDOR_FIELDS)
  claims = csms.read_features(csms.FEATURES_PATH, csms.product_slugs(vendors))
  return csms.csms_payload(csms.merge(certs, vendors, {}, claims))


def test_committed_csms_json_matches_a_fresh_export(monkeypatch):
  """The CSVs are canonical; data/csms.json is a view of them, like csms.md."""
  fresh = pipeline.dump_public_json(fresh_committed_payload(monkeypatch))
  with open(CSMS_JSON, "r", encoding="utf-8", newline="") as f:
    committed = f.read()
  assert committed == fresh, \
    "data/csms.json is stale — re-run `python csms.py render --export-dir data`"


def test_re_rendering_the_committed_data_reports_no_disappeared_id(monkeypatch):
  assert csms.disappeared_ids(CSMS_JSON, fresh_committed_payload(monkeypatch)) == []


def test_committed_manifest_entry_matches_a_fresh_export(monkeypatch):
  payload = fresh_committed_payload(monkeypatch)
  expected = {
    "file": csms.CSMS_EXPORT,
    "sha256": __import__("hashlib").sha256(
      pipeline.dump_public_json(payload).encode("utf-8")).hexdigest(),
    "records": len(payload["products"]),
    "inputs": {path: pipeline._sha256(path)
               for path in (csms.CERTS_PATH, csms.VENDORS_PATH, csms.FEATURES_PATH)},
  }
  with open(MANIFEST_JSON, "r", encoding="utf-8") as f:
    manifest = json.load(f)
  assert manifest["schema_version"] == pipeline.PUBLIC_SCHEMA_VERSION
  assert manifest["payloads"]["csms"] == expected, \
    "data/manifest.json is stale — re-run `python csms.py render --export-dir data`"


EXPORT_SCRIPT = """
import sys
import csms, pipeline
csms.pipeline.get_repo_data = lambda repo, headers: {"html_url": "https://github.com/" + repo}
certs = csms.read_csv(csms.CERTS_PATH, fields=csms.CERT_FIELDS)
vendors = csms.read_csv(csms.VENDORS_PATH, fields=csms.VENDOR_FIELDS, quiet=True)
claims = csms.read_features(csms.FEATURES_PATH, csms.product_slugs(vendors))
sys.stdout.write(pipeline.dump_public_json(
  csms.csms_payload(csms.merge(certs, vendors, {}, claims))))
"""


def test_the_export_does_not_depend_on_the_hash_seed():
  """Versions and features are sets: every sort must have a total key."""
  outputs = []
  for seed in ("1", "2"):
    done = subprocess.run([sys.executable, "-c", EXPORT_SCRIPT], cwd=ROOT,
                          capture_output=True, text=True, check=True,
                          env={**os.environ, "PYTHONHASHSEED": seed})
    outputs.append(done.stdout.split("{", 1)[1])
  assert outputs[0] == outputs[1]
