"""The SHA-256 manifest of every vendored third-party file.

Not a test module and not a conftest: pytest neither collects nor
auto-loads it, so each test file imports what it uses.

tests/vendored_assets.sha256 is in `shasum -a 256` format, so it also checks
from the repository root with `shasum -a 256 -c tests/vendored_assets.sha256`.
Regenerate it after a deliberate addition, removal or upgrade with
`python tests/vendored_manifest.py --write`.
"""

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "tests" / "vendored_assets.sha256"

VENDORED_DIRS = ("eichrecht", "emi3", "nemo", "ocpi", "ocpp", "oicp", "oscp")

# The repository's own files under the vendored directories, listed in
# docs/third-party-assets.md ("How to read the verdicts"): we edit them, so
# they are not pinned.
FIRST_PARTY = frozenset({
  "emi3/README.md",
  "nemo/README.md",
  "ocpp/OCPP-1.2/README.md",
  "ocpp/OCPP-1.5/README.md",
  "ocpp/OCPP-1.6-configuration-keys.md",
  "ocpp/OCPP-1.6/schemas/README.md",
  "ocpp/OCPP-2.0.1/OCPP-2.0.1_part3_JSON_schemas/README.md",
  "ocpp/OCPP-2.1/OCPP-2.1_part3_JSON_schemas/README.md",
  "ocpp/Whitepapers/OCPP-1.6-security-whitepaper-edition-4/schema/README.md",
  "oscp/OSCP-2.0/README.md",
})


def tracked_files(*pathspecs):
  """Repo-relative paths git tracks, NUL-separated so spaces survive."""
  out = subprocess.run(["git", "ls-files", "-z", "--", *pathspecs], cwd=ROOT,
                       check=True, capture_output=True).stdout
  return {path for path in out.decode("utf-8").split("\0") if path}


def tracked_vendored_files():
  return tracked_files(*VENDORED_DIRS) - FIRST_PARTY


def sha256_of(path):
  return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_manifest():
  """Repo-relative path -> SHA-256 hex digest."""
  manifest = {}
  for line in MANIFEST.read_text(encoding="utf-8").splitlines():
    digest, path = line.split("  ", 1)
    manifest[path] = digest
  return manifest


def write_manifest():
  paths = sorted(tracked_vendored_files())
  MANIFEST.write_text("".join(f"{sha256_of(ROOT / p)}  {p}\n" for p in paths),
                      encoding="utf-8", newline="\n")
  return len(paths)


if __name__ == "__main__":
  if sys.argv[1:] != ["--write"]:
    sys.exit(f"usage: python {Path(__file__).relative_to(ROOT)} --write")
  print(f"{MANIFEST.relative_to(ROOT)}: {write_manifest()} files")
