"""The public JSON contract: schemas, the committed manifest, and agreement
with the Markdown views.

`data/projects.json` needs `repos.enriched.csv`, which only `enrich` produces,
so it is not committed yet (issue #98). Its schema and manifest checks run on
a fixture render instead, and the checks on the committed file skip until it
lands.
"""

import copy
import hashlib
import json
import os
import re

import pytest
from jsonschema import Draft202012Validator

import csms
import pipeline
from test_public_export import render, row

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def load(*parts):
  with open(os.path.join(*parts), "r", encoding="utf-8") as f:
    return json.load(f)


def validator(name):
  schema = load(DATA, "schema", name)
  Draft202012Validator.check_schema(schema)
  return Draft202012Validator(schema)


def errors(name, payload):
  return [e.message for e in validator(name).iter_errors(payload)]


def fixture_projects(tmp_path):
  out = render(tmp_path, [
    row("acme/selected"),
    row("acme/stale", dormant="true", ocpp_versions="", categories=""),
    row("acme/unlisted", starred_by="", promoted="0", stars="", archived=""),
    row("acme/moved", html_url="https://codeberg.org/acme/moved", source="codeberg"),
  ])
  return load(str(out / "data" / "projects.json")), out


# --- Schemas ---------------------------------------------------------------------

def test_a_fixture_projects_export_validates(tmp_path):
  payload, _ = fixture_projects(tmp_path)
  assert {p["curation"] for p in payload["projects"]} == {"selection", "dormant", "to_refine"}
  assert errors("projects.schema.json", payload) == []


@pytest.mark.parametrize("mutate", [
  lambda p: p["projects"][0].update(curation="featured"),
  lambda p: p["projects"][0].update(host="gitlab"),
  lambda p: p["projects"][0].update(extra=True),
  lambda p: p.update(extra=True),
  lambda p: p.update(schema_version="2.0"),
  lambda p: p["projects"][0].pop("curation"),
  lambda p: p["projects"][0].update(deprecated=False),
  lambda p: p["projects"][0].update(ocpp_versions=[]),
  lambda p: p["projects"][0].update(ocpi_versions=[]),
], ids=["unknown-curation", "unknown-host", "extra-field", "extra-root-field",
        "other-version", "missing-field", "deprecated-false", "empty-ocpp-versions",
        "empty-ocpi-versions"])
def test_the_projects_schema_rejects(tmp_path, mutate):
  payload, _ = fixture_projects(tmp_path)
  mutate(payload)
  assert errors("projects.schema.json", payload)


def test_the_committed_csms_export_validates():
  payload = load(DATA, csms.CSMS_EXPORT)
  assert payload["products"]
  assert errors("csms.schema.json", payload) == []


@pytest.mark.parametrize("mutate", [
  lambda p: p["products"][0].update(source_available=False),
  lambda p: p["products"][0].update(ocpi=False),
  lambda p: p["products"][0].update(extra=True),
  lambda p: p.update(extra=True),
  lambda p: p["products"][0]["features_documented"].append({"feature": "Core"}),
  lambda p: p["products"][0].pop("certificates"),
  lambda p: p["products"][0].update(ocpp_versions=[]),
], ids=["source-available-false", "ocpi-false", "extra-field", "extra-root-field",
        "unsourced-feature", "missing-field", "empty-ocpp-versions"])
def test_the_csms_schema_rejects(mutate):
  payload = copy.deepcopy(load(DATA, csms.CSMS_EXPORT))
  mutate(payload)
  assert errors("csms.schema.json", payload)


def test_the_manifest_checksum_matches_the_committed_payload():
  entry = load(DATA, pipeline.MANIFEST_EXPORT)["payloads"]["csms"]
  with open(os.path.join(DATA, entry["file"]), "rb") as f:
    payload = f.read()
  assert entry["sha256"] == hashlib.sha256(payload).hexdigest()
  assert entry["records"] == len(json.loads(payload)["products"])


def projects_export_problems(data_dir):
  """What is wrong with the projects payload in `data_dir`, or None when absent.

  The payload and its `projects` manifest entry come together or not at all;
  when both are there, the payload must validate and the entry must record its
  file name, SHA-256 and record count.
  """
  path = os.path.join(data_dir, pipeline.PROJECTS_EXPORT)
  manifest_path = os.path.join(data_dir, pipeline.MANIFEST_EXPORT)
  entry = None
  if os.path.exists(manifest_path):
    entry = load(manifest_path)["payloads"].get("projects")
  if not os.path.exists(path):
    return None if entry is None else ["manifest entry without payload"]
  if entry is None:
    return ["payload without manifest entry"]
  with open(path, "rb") as f:
    raw = f.read()
  payload = json.loads(raw)
  problems = errors("projects.schema.json", payload)
  if entry["file"] != pipeline.PROJECTS_EXPORT:
    problems.append("manifest file name")
  if entry["sha256"] != hashlib.sha256(raw).hexdigest():
    problems.append("manifest sha256")
  if entry["records"] != len(payload["projects"]):
    problems.append("manifest record count")
  return problems


def test_a_fixture_projects_export_matches_its_manifest(tmp_path):
  _, out = fixture_projects(tmp_path)
  assert projects_export_problems(str(out / "data")) == []


def _set_entry(data_dir, **fields):
  manifest = load(data_dir, pipeline.MANIFEST_EXPORT)
  manifest["payloads"]["projects"].update(fields)
  pipeline.write_public_json(os.path.join(data_dir, pipeline.MANIFEST_EXPORT), manifest)


def _drop_entry(data_dir):
  manifest = load(data_dir, pipeline.MANIFEST_EXPORT)
  del manifest["payloads"]["projects"]
  pipeline.write_public_json(os.path.join(data_dir, pipeline.MANIFEST_EXPORT), manifest)


def _break_payload(data_dir):
  path = os.path.join(data_dir, pipeline.PROJECTS_EXPORT)
  payload = load(path)
  payload["projects"][0]["curation"] = "featured"
  pipeline.write_public_json(path, payload)


@pytest.mark.parametrize("mutate,problem", [
  (lambda d: _set_entry(d, sha256="0" * 64), "manifest sha256"),
  (lambda d: _set_entry(d, records=1), "manifest record count"),
  (lambda d: _set_entry(d, file="other.json"), "manifest file name"),
  (_drop_entry, "payload without manifest entry"),
  (lambda d: os.remove(os.path.join(d, pipeline.PROJECTS_EXPORT)),
   "manifest entry without payload"),
], ids=["wrong-sha256", "wrong-records", "wrong-file", "no-entry", "no-payload"])
def test_the_projects_export_check_catches(tmp_path, mutate, problem):
  _, out = fixture_projects(tmp_path)
  mutate(str(out / "data"))
  assert problem in projects_export_problems(str(out / "data"))


def test_the_projects_export_check_runs_the_schema(tmp_path):
  _, out = fixture_projects(tmp_path)
  _break_payload(str(out / "data"))
  problems = projects_export_problems(str(out / "data"))
  assert any("featured" in p for p in problems)
  assert "manifest sha256" in problems


def test_the_committed_projects_export_matches_its_manifest():
  problems = projects_export_problems(DATA)
  if problems is None:
    pytest.skip("data/projects.json is not committed yet (issue #98)")
  assert problems == []


# --- JSON <-> Markdown --------------------------------------------------------------

LINK = re.compile(r"^\s*- \[([^\]]+)\]\(", re.M)


def linked(text):
  return set(LINK.findall(text))


def readme_selection(readme):
  begin = readme.index(pipeline.README_MARKER_BEGIN)
  return linked(readme[begin:readme.index(pipeline.README_MARKER_END)])


def tiers(projects):
  by_tier = {"selection": set(), "dormant": set(), "to_refine": set()}
  for project in projects["projects"]:
    by_tier[project["curation"]].add(project["full_name"])
  return by_tier


def consistency_problems(projects, readme, legacy):
  """Where the export and the two Markdown views disagree on the tiers."""
  by_tier = tiers(projects)
  problems = []
  if by_tier["selection"] != readme_selection(readme):
    problems.append(("README.md", by_tier["selection"] ^ readme_selection(readme)))
  rest = by_tier["dormant"] | by_tier["to_refine"]
  if rest != linked(legacy):
    problems.append(("legacy-projects.md", rest ^ linked(legacy)))
  return problems


def test_the_consistency_check_passes_on_a_fresh_render(tmp_path):
  projects, out = fixture_projects(tmp_path)
  assert consistency_problems(projects, (out / "README.md").read_text(encoding="utf-8"),
                              (out / "legacy-projects.md").read_text(encoding="utf-8")) == []


def test_the_consistency_check_catches_a_moved_repo(tmp_path):
  projects, out = fixture_projects(tmp_path)
  projects["projects"][0]["curation"] = "to_refine"
  moved = projects["projects"][0]["full_name"]
  problems = consistency_problems(
    projects, (out / "README.md").read_text(encoding="utf-8"),
    (out / "legacy-projects.md").read_text(encoding="utf-8"))
  assert problems == [("README.md", {moved}), ("legacy-projects.md", {moved})]


def test_committed_projects_json_agrees_with_the_markdown():
  path = os.path.join(DATA, pipeline.PROJECTS_EXPORT)
  if not os.path.exists(path):
    pytest.skip("data/projects.json is not committed yet (issue #98)")
  with open(os.path.join(ROOT, "README.md"), "r", encoding="utf-8") as f:
    readme = f.read()
  with open(os.path.join(ROOT, "legacy-projects.md"), "r", encoding="utf-8") as f:
    legacy = f.read()
  assert consistency_problems(load(path), readme, legacy) == []
