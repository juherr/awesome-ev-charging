"""Every vendored third-party file stays byte-identical to what was vendored.

The specifications under the seven vendored directories are kept verbatim
(see docs/third-party-assets.md): most carry no licence that allows a
modification, and the CC BY-ND ones forbid one. tests/vendored_assets.sha256
pins each of them; the repository's own files there (FIRST_PARTY) are not
pinned, since we edit them.
"""

import re

import pytest

from vendored_manifest import (
  FIRST_PARTY,
  MANIFEST,
  ROOT,
  VENDORED_DIRS,
  load_manifest,
  sha256_of,
  tracked_files,
  tracked_vendored_files,
)

INVENTORY = ROOT / "docs" / "third-party-assets.md"
REGENERATE = "python tests/vendored_manifest.py --write"


def _in_dir(paths, directory):
  return {path for path in paths if path.startswith(directory + "/")}


@pytest.mark.parametrize("directory", VENDORED_DIRS)
def test_vendored_files_are_pinned(directory):
  pinned = {path: digest for path, digest in load_manifest().items()
            if path.startswith(directory + "/")}
  tracked = _in_dir(tracked_vendored_files(), directory)
  present = {path for path in pinned if (ROOT / path).is_file()}
  added = sorted(tracked - set(pinned))
  missing = sorted(set(pinned) - present)
  modified = sorted(path for path in present
                    if sha256_of(ROOT / path) != pinned[path])
  assert not (added or missing or modified), (
    f"{directory}/ holds third-party files that must stay byte-identical. "
    f"Added: {added}, missing: {missing}, modified: {modified}. Restore the "
    f"published file, or, for a deliberate addition, removal or upgrade, "
    f"record its provenance in the {directory}/ README and its rights in "
    f"docs/third-party-assets.md (counts included), then run `{REGENERATE}` "
    f"to rewrite {MANIFEST.relative_to(ROOT).as_posix()}.")


def test_manifest_pins_only_vendored_directories():
  stray = sorted(path for path in load_manifest()
                 if path in FIRST_PARTY
                 or not path.startswith(tuple(d + "/" for d in VENDORED_DIRS)))
  assert not stray, f"Pinned outside the vendored set: {stray}. Run `{REGENERATE}`."


def test_every_first_party_file_exists_and_is_tracked():
  tracked = tracked_files()
  stale = sorted(path for path in FIRST_PARTY
                 if path not in tracked or not (ROOT / path).is_file())
  assert not stale, (
    f"FIRST_PARTY in tests/vendored_manifest.py names files that are gone: "
    f"{stale}. Update it and the list in docs/third-party-assets.md.")


def test_inventory_counts_match_the_manifest():
  text = INVENTORY.read_text(encoding="utf-8")
  total = re.search(r"add\s+up\s+to\s+(\d+)\s+files", text)
  assert total, "docs/third-party-assets.md lost its 'add up to N files' sentence"
  rows = dict(re.findall(r"^\| (Allowed|Unknown) \| (\d+) \|", text, re.MULTILINE))
  assert set(rows) == {"Allowed", "Unknown"}, (
    f"Summary table rows not found in docs/third-party-assets.md: {rows}")
  pinned = len(load_manifest())
  assert (int(total.group(1)), int(rows["Allowed"]) + int(rows["Unknown"])) \
    == (pinned, pinned), (
      f"docs/third-party-assets.md counts {total.group(1)} files "
      f"(Allowed {rows['Allowed']} + Unknown {rows['Unknown']}), the manifest "
      f"pins {pinned}: update the inventory with the files you added or removed.")
