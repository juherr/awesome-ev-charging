"""The public JSON contract: schemas, the committed manifest, and agreement
with the Markdown views.

`data/projects.json` needs `repos.enriched.csv`, which only `enrich` produces,
so it is not committed yet (issue #98). Its schema is checked on a fixture
render instead, and its README consistency check skips until it lands.
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
], ids=["unknown-curation", "unknown-host", "extra-field", "extra-root-field",
        "other-version", "missing-field"])
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
], ids=["source-available-false", "ocpi-false", "extra-field", "extra-root-field",
        "unsourced-feature", "missing-field"])
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
