"""Fixture builders shared by the tests of the public JSON export.

Not a test module and not a conftest: pytest neither collects nor
auto-loads it, so each test file imports what it uses.
"""

import csv
import types

import pipeline

FIELDS = pipeline.CSV_FIELDS + ["categories", "ocpp_versions", "ocpi_versions"]

README = (
  "# List\n\n## Contents\n\n"
  f"{pipeline.README_TOC_BEGIN}\n{pipeline.README_TOC_END}\n\n"
  "## Tools and Resources\n\n"
  f"{pipeline.README_MARKER_BEGIN}\n{pipeline.README_MARKER_END}\n"
)


def row(full_name, **fields):
  """A complete enriched row: an active, starred-by-both GitHub repo."""
  out = {field: "" for field in FIELDS}
  out.update(
    full_name=full_name,
    html_url=f"https://github.com/{full_name}",
    description="An OCPP tool",
    language="Python",
    license="MIT License",
    stars="10",
    forks="2",
    open_issues="1",
    topics="ocpp|ev-charging",
    topic_matches="2",
    pushed_at="2026-01-01T00:00:00Z",
    days_since_push="5",
    dormant="false",
    archived="false",
    created_at="2020-01-01T00:00:00Z",
    updated_at="2026-01-02T00:00:00Z",
    is_fork="false",
    starred_by="juherr|mateogreil",
    promoted="2",
    by_contributor="false",
    source="starred-list+topic",
    categories="OCPP > Server",
    ocpp_versions="1.6,2.0.1",
    ocpi_versions="",
  )
  out.update(fields)
  return out


def write_csv(path, rows):
  with open(path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)
  return path


def render(tmp_path, rows, export=True, readme=True, name="out"):
  """Render `rows`; return the output directory."""
  out = tmp_path / name
  out.mkdir()
  infile = write_csv(out / "repos.enriched.csv", rows)
  args = types.SimpleNamespace(infile=str(infile), out=str(out / "legacy-projects.md"),
                               readme=None)
  if readme:
    (out / "README.md").write_text(README, encoding="utf-8")
    args.readme = str(out / "README.md")
  if export:
    args.export_dir = str(out / "data")
  pipeline.render(args)
  return out
