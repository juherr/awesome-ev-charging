"""Checks on the vendored OSCP 2.0 material under oscp/OSCP-2.0/.

The specification PDF is (c) Open Charge Alliance under CC BY-ND 4.0 (p. 4).
The JSON schemas carry no licence notice, so their licence is not established
and nothing grants a right to modify them: they must stay byte-identical to
the OCA download, defects included. These tests pin the material with
a SHA-256 manifest, then turn the "Known defects" table of
oscp/OSCP-2.0/README.md into checked facts: each defect is shown to break a
message the specification allows, and the local patch the README recommends
is shown to be enough. Patches only ever touch an in-memory deep copy; no
patched schema is written to disk.
"""

import copy
import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft7Validator
from referencing import Registry, Resource
from referencing.exceptions import Unresolvable

OSCP_DIR = Path(__file__).resolve().parent.parent / "oscp" / "OSCP-2.0"
SCHEMA_DIR = OSCP_DIR / "schemas"
ID_PREFIX = "http://www.openchargealliance.org/schemas/oscp/2.0/"

# Every vendored file, relative to OSCP_DIR. README.md is ours, not OCA's.
VENDORED_SHA256 = {
    "OSCP 2.0 Specification.pdf": "7d04d4dd56a1125e0e099019f736a1abbca5b385181f9e9f9d2a476ac5962cc0",
    "schemas/adjust-group-capacity-forecast.json": "71f52d96a1b2e17ddd4df7755d83aff106cbc0a0e90fc29a2a67d3ea563f236d",
    "schemas/asset-category.json": "112baf5165368ee5e20ab17bd120aa4d1dd71bef02b3cf7859fa0a4e1eff2dbc",
    "schemas/asset-measurement.json": "3bcdc9c6dd2f1925d8539fdcb43fc7f4a0731cfeefbf9ed38efbdfacdb919443",
    "schemas/capacity-forecast-type.json": "790beefd2a9ee3e7c4256fade58f6963a617d495ba1769c3f62b185e2713125f",
    "schemas/energy-flow-direction.json": "3cf451adf2c9b66d60f07cf6ea190d1bf62ba318fb40519bb8c1b83e21fdf914",
    "schemas/energy-measurement-unit.json": "c70addd79e011746287ce6b853f3af4eeeb0dd74d274ecba54a3b5f2c138e448",
    "schemas/energy-measurement.json": "29e9ef3008de947bd4da21b8d26fcac2e87aa4ebacb06675f13d67ec89c14385",
    "schemas/energy-type.json": "eb5fc53a027e0e8a90fd50a353f217d9c4a3de6278ca0aa4a0cdffca0282ae7e",
    "schemas/error.json": "ebe5c66b392cb5121385f1393708ece92d4015506221721b1eb8d58967c97c42",
    "schemas/forecasted-block-unit.json": "57c3b602cb6e67ad781bd95cab61d6260bccfabe96c1a10619b7de3698533628",
    "schemas/forecasted-block.json": "1df083a3ecb4ba9e2ccb923ae64946045fe4e4021c62650a08f68a0af613e624",
    "schemas/group-capacity-compliance-error.json": "d7b24fe8d692a7200e1cf189f6cf010d4b81751e4c54af75dbf0d263cb756339",
    "schemas/handshake-acknowledge.json": "e2f266eca2f61595466a18d79f0e92b82f2f4bc1ea8fbf05d84a4a68f71f4b07",
    "schemas/handshake.json": "afde742030e3ca33195c8d1ea9754781a5d2f9e3ae993cb15b1e5487ed3d7cfb",
    "schemas/heartbeat.json": "8875abb86b05484fcb266d96080912b847b66199cca9f04745abb8ad3d668176",
    "schemas/instantaneous-measurement-unit.json": "3b0d32fdb240ca48f79dc18501170c168e2e018dc4b4a9c89e9dde98d97259ba",
    "schemas/instantaneous-measurement.json": "b8a79157cfc2b19c65990c57157759ff4a5b1450676f053d629019af31b6d72a",
    "schemas/measurement-configuration.json": "94c39f0e74fb7dfe33e73de7866fb5a49aba6b3a344b5dd0f5b7ebdc20090816",
    "schemas/paginated-request.json": "bce94692856c8e91349f4d271ec2549202b5c7aae4c86ba5f5c9c5fb020f621a",
    "schemas/phase-indicator.json": "ac95ae157d552f68a3074a4c8a3f397adf7a8d0b68e3cb51655acaf3bfb24fb2",
    "schemas/register.json": "20b29a2fa323c8456be2a89997da6587f81a9b1de85d852100e29e7e4ce29a14",
    "schemas/required-behaviour.json": "ba139444847e1d6606f0009cc48c0c88e18b27e5e94515f06b997969f1250a88",
    "schemas/update-asset-measurements.json": "3308c36afd143d3d5fba81ab8e65931de0ad0f4eef0833043d821579e91e49a1",
    "schemas/update-group-capacity-forecast.json": "c58756ceff768291ae62676176f4a88ce6f6c6dc643c9817d9a3875d9f0794c8",
    "schemas/update-group-measurements.json": "de44a59f367800d17415eef68d107e72714eae81b1fee1e2ec0b629e844612a0",
    "schemas/version-url.json": "6e6214a5a73af196500750b631be1946d93006a6d030407bb70792758774a030",
}

LICENCE_NOTE = (
  "oscp/OSCP-2.0/ is (c) Open Charge Alliance; the schemas' licence is not "
  "established and nothing grants a right to modify them, so they must stay "
  "byte-identical: restore the published files instead of updating this manifest"
)

# The two schemas whose published $id does not match their file name.
ID_DEFECTS = {
  "update-asset-measurements.json": ID_PREFIX + "update-asset-measurement.json",
  "version-url.json": ID_PREFIX + "version_url.json",
}


# --- Helpers ------------------------------------------------------------------

SCHEMA_NAMES = sorted(Path(name).name for name in VENDORED_SHA256
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

def test_vendored_files_are_byte_identical_to_the_oca_download():
  # Dotfiles (a Finder .DS_Store) are local noise git ignores, not vendored files.
  present = {path.relative_to(OSCP_DIR).as_posix()
             for path in OSCP_DIR.rglob("*")
             if path.is_file() and not path.name.startswith(".")} - {"README.md"}
  assert present == set(VENDORED_SHA256), (
    f"{LICENCE_NOTE}. Added: {sorted(present - set(VENDORED_SHA256))}, "
    f"missing: {sorted(set(VENDORED_SHA256) - present)}")
  changed = [name for name, digest in VENDORED_SHA256.items()
             if hashlib.sha256((OSCP_DIR / name).read_bytes()).hexdigest() != digest]
  assert not changed, f"{LICENCE_NOTE}. Changed: {changed}"


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
