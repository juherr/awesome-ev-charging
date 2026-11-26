"""The site's committed fixture export is a fresh render of its fixture CSV.

`site/fixtures/data/` is what the site's tests and CI build read in place of
`data/` (where `projects.json` is not published yet, issue #98). It must be
the real exporter's output, so a change to the export that the fixture does
not follow fails here rather than in a site build that happens to still pass.
Regenerate it with `mise run site-fixture`.
"""

import hashlib
import json
import pathlib
import types

import pipeline

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXTURE_CSV = "site/fixtures/repos.enriched.csv"
FIXTURE_DATA = ROOT / "site" / "fixtures" / "data"

STALE = "The site fixture drifted from a fresh render: run `mise run site-fixture`."


def _fresh_render(tmp_path, monkeypatch):
  # The manifest records input paths relative to the current directory, and
  # the mise task runs from the repository root.
  monkeypatch.chdir(ROOT)
  out = tmp_path / "data"
  out.mkdir()
  pipeline.render(types.SimpleNamespace(infile=FIXTURE_CSV, readme=None,
                                        out=str(tmp_path / "legacy-projects.md"),
                                        export_dir=str(out)))
  return out


def test_projects_json_matches_a_fresh_render(tmp_path, monkeypatch):
  fresh = _fresh_render(tmp_path, monkeypatch)
  committed = (FIXTURE_DATA / "projects.json").read_bytes()
  assert committed == (fresh / "projects.json").read_bytes(), STALE


def test_manifest_projects_entry_matches_a_fresh_render(tmp_path, monkeypatch):
  fresh = _fresh_render(tmp_path, monkeypatch)
  committed = json.loads((FIXTURE_DATA / "manifest.json").read_text(encoding="utf-8"))
  expected = json.loads((fresh / "manifest.json").read_text(encoding="utf-8"))
  assert committed["payloads"]["projects"] == expected["payloads"]["projects"], STALE


def test_fixture_csms_json_is_the_one_its_manifest_describes():
  """The CSMS payload is copied from `data/`, with its manifest entry."""
  manifest = json.loads((FIXTURE_DATA / "manifest.json").read_text(encoding="utf-8"))
  entry = manifest["payloads"]["csms"]
  payload = (FIXTURE_DATA / entry["file"]).read_bytes()
  assert hashlib.sha256(payload).hexdigest() == entry["sha256"], STALE
  assert len(json.loads(payload)["products"]) == entry["records"], STALE


def test_fixture_covers_the_cases_the_site_renders():
  """A fixture trimmed by accident would leave a page state untested."""
  projects = json.loads((FIXTURE_DATA / "projects.json").read_text(encoding="utf-8"))["projects"]
  assert {p["host"] for p in projects} >= {"github", "codeberg", "other"}
  assert {p["curation"] for p in projects} == {"selection", "dormant", "to_refine"}
  assert any(p["ocpp_versions"] for p in projects)
  assert any(p["ocpi_versions"] for p in projects)
  assert any(p["ocpp_versions"] is None and p["ocpi_versions"] is None for p in projects)
  assert any(p["language"] is None for p in projects)
  assert any(p["dormant"] is None for p in projects)
  assert any(p["deprecated"] for p in projects)
  assert any(not p["categories"] for p in projects)
  subs = {(c["main"], c["sub"]) for p in projects for c in p["categories"]}
  assert any(sub == "Libraries" for _, sub in subs)
  assert any(main == "Other" for main, _ in subs)
  assert any(sub is None for _, sub in subs)
