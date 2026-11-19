"""Checks on the vendored OSCP 2.0 material under oscp/OSCP-2.0/.

The specification PDF is (c) Open Charge Alliance under CC BY-ND 4.0 (p. 4).
The JSON schemas carry no licence notice, so their licence is not established
and nothing grants a right to modify them: they must stay byte-identical to
the OCA download, defects included. tests/test_vendored_assets.py pins
their bytes with the shared SHA-256 manifest, from which this module takes the
schema set. These tests turn the "Known defects" table of
oscp/OSCP-2.0/README.md into checked facts: each defect is shown to break a
message the specification allows, and the local patch the README recommends
is shown to be enough. Patches only ever touch an in-memory deep copy; no
patched schema is written to disk.
"""

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft7Validator
from referencing import Registry, Resource
from referencing.exceptions import Unresolvable

from vendored_manifest import load_manifest

OSCP_DIR = Path(__file__).resolve().parent.parent / "oscp" / "OSCP-2.0"
SCHEMA_DIR = OSCP_DIR / "schemas"
ID_PREFIX = "http://www.openchargealliance.org/schemas/oscp/2.0/"

# Every pinned OCA file, relative to OSCP_DIR. README.md is ours, not OCA's.
OSCP_PREFIX = "oscp/OSCP-2.0/"
OSCP_FILES = {path[len(OSCP_PREFIX):] for path in load_manifest()
              if path.startswith(OSCP_PREFIX)}

# The two schemas whose published $id does not match their file name.
ID_DEFECTS = {
  "update-asset-measurements.json": ID_PREFIX + "update-asset-measurement.json",
  "version-url.json": ID_PREFIX + "version_url.json",
}


# --- Helpers ------------------------------------------------------------------

SCHEMA_NAMES = sorted(Path(name).name for name in OSCP_FILES
                      if name.startswith("schemas/"))


def load_schemas():
  """File name -> parsed schema, exactly as published.

  Reads the manifest's list rather than globbing, so a stray file fails the
  integrity test instead of breaking collection.
  """
  return {name: json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))
          for name in SCHEMA_NAMES}


def patch_ids(schemas):
  """Copy with every $id set to the URI its file name implies."""
  patched = copy.deepcopy(schemas)
  for name, schema in patched.items():
    schema["$id"] = ID_PREFIX + name
  return patched


def patch_measurements_items(schemas):
  """Copy with UpdateAssetMeasurements.measurements as an array of AssetMeasurement."""
  patched = copy.deepcopy(schemas)
  patched["update-asset-measurements.json"]["properties"]["measurements"] = {
    "type": "array", "items": {"$ref": "asset-measurement.json"}, "minItems": 1,
  }
  return patched


def patch_compliance_error_min_items(schemas):
  """Copy with GroupCapacityComplianceError.forecasted_blocks allowed empty."""
  patched = copy.deepcopy(schemas)
  del patched["group-capacity-compliance-error.json"]["properties"]["forecasted_blocks"]["minItems"]
  return patched


def registry_for(schemas):
  """Registry resolving each schema by its own $id, as published or patched."""
  return Registry().with_resources(
    (schema["$id"], Resource.from_contents(schema)) for schema in schemas.values())


def validator(schemas, name):
  return Draft7Validator(schemas[name], registry=registry_for(schemas))


def refs_in(node):
  """Every $ref value anywhere in a schema."""
  if isinstance(node, dict):
    for key, value in node.items():
      if key == "$ref":
        yield value
      else:
        yield from refs_in(value)
  elif isinstance(node, list):
    for item in node:
      yield from refs_in(item)


ASSET_MEASUREMENT = {
  "asset_id": "evse-1",
  "asset_category": "CHARGING",
  "energy_measurement": {
    "value": 12.5, "phase": "ALL", "unit": "KWH", "direction": "NET",
    "measure_time": "2026-11-15T10:00:00Z",
  },
}


# --- Integrity ----------------------------------------------------------------

def test_the_manifest_pins_the_specification_and_the_26_schemas():
  # The bytes are checked by tests/test_vendored_assets.py. This guards the
  # schema set every test below iterates: an empty or partial filter would
  # let them pass on nothing.
  assert OSCP_FILES - {f"schemas/{name}" for name in SCHEMA_NAMES} \
    == {"OSCP 2.0 Specification.pdf"}
  assert len(SCHEMA_NAMES) == 26


# --- Schema set ---------------------------------------------------------------

@pytest.mark.parametrize("name", SCHEMA_NAMES)
def test_every_schema_is_a_valid_draft_07_schema(name):
  Draft7Validator.check_schema(load_schemas()[name])


def test_only_the_two_documented_schemas_have_an_id_that_is_not_their_file_name():
  mismatched = {name: schema["$id"] for name, schema in load_schemas().items()
                if schema["$id"] != ID_PREFIX + name}
  assert mismatched == ID_DEFECTS


def test_every_ref_resolves_once_the_two_ids_are_patched():
  schemas = patch_ids(load_schemas())
  registry = registry_for(schemas)
  for schema in schemas.values():
    resolver = registry.resolver(base_uri=schema["$id"])
    for ref in refs_in(schema):
      resolver.lookup(ref)  # raises Unresolvable on a dangling $ref


# --- Defects ------------------------------------------------------------------

def test_update_asset_measurements_ref_beside_type_rejects_a_valid_message():
  # §4.5.2: measurements is AssetMeasurement, cardinality 1..*.
  message = {"group_id": "group-1",
             "measurements": [ASSET_MEASUREMENT,
                              {"asset_id": "pv-1", "asset_category": "GENERATION"}]}
  published = load_schemas()
  errors = list(validator(published, "update-asset-measurements.json").iter_errors(message))
  # Draft-07 ignores the keywords beside $ref, so the whole array is checked
  # as one AssetMeasurement object.
  assert [(e.validator, e.validator_value) for e in errors] == [("type", "object")]
  patched = patch_measurements_items(published)
  validator(patched, "update-asset-measurements.json").validate(message)


def test_update_asset_measurements_patch_still_validates_each_measurement():
  message = {"group_id": "group-1", "measurements": [{"asset_id": "evse-1"}]}
  patched = patch_measurements_items(load_schemas())
  assert not validator(patched, "update-asset-measurements.json").is_valid(message)


def test_group_capacity_compliance_error_min_items_rejects_zero_forecasted_blocks():
  # §4.4.3: forecasted_blocks is ForecastedBlock, cardinality 0..*.
  message = {"message": "cannot comply", "forecasted_blocks": []}
  published = load_schemas()
  errors = list(validator(published, "group-capacity-compliance-error.json").iter_errors(message))
  assert [e.validator for e in errors] == ["minItems"]
  patched = patch_compliance_error_min_items(published)
  validator(patched, "group-capacity-compliance-error.json").validate(message)


def test_version_url_id_leaves_the_register_ref_unresolvable():
  message = {"token": "secret",
             "version_url": [{"version": "2.0", "base_url": "https://cp.example/oscp"}]}
  published = load_schemas()
  with pytest.raises(Unresolvable, match="version-url.json"):
    validator(published, "register.json").validate(message)
  patched = patch_ids(published)
  validator(patched, "register.json").validate(message)
