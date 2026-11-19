"""The public JSON export written by `render --export-dir`, and its manifest.

Every test renders from a fixture enriched CSV written in `tmp_path`: no
network, no LLM, no committed data. The export must be byte-stable for the
same input, consume exactly the rows the Markdown uses, and say `null` for
what the pipeline does not know.
"""

import hashlib
import json
import shutil

import pytest

import pipeline
from export_helpers import render, row


def export(tmp_path, rows):
    """Render `rows` and return the exported records keyed by id."""
    out = render(tmp_path, rows)
    payload = json.loads((out / "data" / "projects.json").read_text(encoding="utf-8"))
    return {record["id"]: record for record in payload["projects"]}


@pytest.fixture(autouse=True)
def isolated(monkeypatch, tmp_path):
    """Run from tmp_path so manifest paths are relative to it, and pin the curation knobs."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(pipeline, "EXCLUDED_REPOS", {"acme/excluded"})


# --- Without the flag nothing changes -------------------------------------------

def test_the_markdown_is_identical_with_and_without_the_export(tmp_path):
    rows = [row("acme/server"), row("acme/old", dormant="true"), row("acme/new", starred_by="")]
    plain = render(tmp_path, rows, export=False, name="plain")
    exported = render(tmp_path, rows, export=True, name="exported")
    for name in ("legacy-projects.md", "README.md"):
        assert (plain / name).read_bytes() == (exported / name).read_bytes()
    assert not (plain / "data").exists()
    assert (exported / "data" / "projects.json").exists()


def test_render_without_an_export_dir_attribute_still_works(tmp_path):
    """Callers that predate the flag pass a namespace without `export_dir`."""
    out = render(tmp_path, [row("acme/server")], export=False)
    assert (out / "legacy-projects.md").exists()


# --- Byte stability ----------------------------------------------------------------

def test_the_same_input_renders_byte_identical_files(tmp_path):
    rows = [row("Zeta/b"), row("acme/a", description="Ünïcode ⚡ tool")]
    names = ("projects.json", "manifest.json")
    first = render(tmp_path, rows)
    before = {name: (first / "data" / name).read_bytes() for name in names}
    shutil.rmtree(first)
    second = render(tmp_path, rows)
    assert {name: (second / "data" / name).read_bytes() for name in names} == before


def test_the_row_order_of_the_input_does_not_change_the_payload(tmp_path):
    rows = [row("Zeta/b"), row("acme/a"), row("acme/c", dormant="true")]
    first = render(tmp_path, rows, name="first")
    second = render(tmp_path, list(reversed(rows)), name="second")
    assert ((first / "data" / "projects.json").read_bytes()
            == (second / "data" / "projects.json").read_bytes())


def test_the_payload_has_a_fixed_shape_and_formatting(tmp_path):
    out = render(tmp_path, [row("Zeta/b"), row("acme/a", description="Ünïcode ⚡ tool")])
    raw = (out / "data" / "projects.json").read_text(encoding="utf-8")
    payload = json.loads(raw)
    assert raw == json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    assert "⚡" in raw  # ensure_ascii=False: UTF-8, not \u escapes
    assert payload["schema_version"] == "1.0"
    assert [p["id"] for p in payload["projects"]] == ["acme/a", "zeta/b"]
    assert payload["projects"][1]["full_name"] == "Zeta/b"


def test_two_rows_with_the_same_id_fail_the_render(tmp_path):
    with pytest.raises(SystemExit) as exc:
        render(tmp_path, [row("Acme/Server"), row("acme/server")])
    assert "Acme/Server" in str(exc.value) and "acme/server" in str(exc.value)
    assert not (tmp_path / "out" / "legacy-projects.md").exists()


# --- Curation tiers --------------------------------------------------------------------

def test_each_tier_is_exported(tmp_path):
    records = export(tmp_path, [
        row("acme/selected"),
        row("acme/stale", dormant="true"),
        row("acme/unlisted", starred_by="", promoted="0"),
        row("acme/retired", description="Deprecated OCPP server, use acme/selected"),
    ])
    assert records["acme/selected"]["curation"] == "selection"
    assert records["acme/stale"]["curation"] == "dormant"
    assert records["acme/stale"]["dormant"] is True
    assert records["acme/unlisted"]["curation"] == "to_refine"
    retired = records["acme/retired"]
    assert (retired["curation"], retired["dormant"], retired["deprecated"]) == ("dormant", False, True)
    assert records["acme/selected"]["deprecated"] is None  # no wording is not "not deprecated"


def test_the_tier_helper_matches_the_markdown_partition(tmp_path):
    out = render(tmp_path, [row("acme/selected"), row("acme/stale", dormant="true"),
                            row("acme/unlisted", starred_by="")])
    readme = (out / "README.md").read_text(encoding="utf-8")
    legacy = (out / "legacy-projects.md").read_text(encoding="utf-8")
    assert "acme/selected" in readme and "acme/selected" not in legacy
    assert "acme/stale" in legacy.split("## To refine")[0]
    assert "acme/unlisted" in legacy.split("## To refine")[1]


def test_an_excluded_repo_is_not_exported(tmp_path):
    records = export(tmp_path, [row("acme/server"), row("Acme/Excluded")])
    assert set(records) == {"acme/server"}


# --- Hosts -----------------------------------------------------------------------------

def test_hosts_are_derived_from_the_effective_url(tmp_path, monkeypatch):
    monkeypatch.setitem(pipeline.REPO_OVERRIDES, "acme/moved",
                        {"html_url": "https://gitlab.com/acme/moved", "dormant": "false"})
    records = export(tmp_path, [
        row("acme/server"),
        row("forge/tariffs", html_url="https://codeberg.org/forge/tariffs", source="codeberg",
            starred_by="", promoted="0", pushed_at="", license="N/A"),
        row("acme/moved", archived="true", dormant="true"),
    ])
    assert records["acme/server"]["host"] == "github"
    codeberg = records["forge/tariffs"]
    assert (codeberg["host"], codeberg["url"]) == ("codeberg", "https://codeberg.org/forge/tariffs")
    assert codeberg["curation"] == "selection"  # CODEBERG_REPOS scores at least 1
    assert codeberg["pushed_at"] is None
    assert codeberg["dormant"] is None  # no last commit read: activity is unknown
    assert codeberg["license"] is None
    assert codeberg["discovered_via"] == ["codeberg"]
    moved = records["acme/moved"]
    assert (moved["host"], moved["url"]) == ("other", "https://gitlab.com/acme/moved")
    assert (moved["dormant"], moved["archived"], moved["curation"]) == (False, True, "selection")


# --- Categories --------------------------------------------------------------------------

def test_categories_are_the_effective_ones_protocol_first(tmp_path, monkeypatch):
    monkeypatch.setitem(pipeline.CATEGORY_OVERRIDES, "acme/pinned", "OCPI > Libraries")
    records = export(tmp_path, [
        row("acme/pinned", categories="Other > Home automation"),
        row("acme/mixed", categories="Other > home assistant|OCPP > Server|OCPP > Server"),
    ])
    assert records["acme/pinned"]["categories"] == [{"main": "OCPI", "sub": "Libraries"}]
    mixed = records["acme/mixed"]
    expected_other = pipeline._row_categories({"full_name": "x", "categories": "Other > home assistant"})
    assert mixed["primary_category"] == {"main": "OCPP", "sub": "Server"}
    assert mixed["categories"] == [{"main": "OCPP", "sub": "Server"},
                                   {"main": "Other", "sub": expected_other[0][1]}]


def test_a_bare_main_has_a_null_sub(tmp_path):
    records = export(tmp_path, [row("acme/bare", categories="OCPP")])
    assert records["acme/bare"]["categories"] == [{"main": "OCPP", "sub": None}]


# --- Unknown is null ----------------------------------------------------------------------

def test_empty_values_are_exported_as_null(tmp_path):
    records = export(tmp_path, [row(
        "acme/blank", description="  ", language="", license="", stars="", forks="",
        archived="", dormant="", pushed_at="", updated_at="", categories="",
        ocpp_versions="", ocpi_versions="", topics="", source="")])
    blank = records["acme/blank"]
    for field in ("description", "language", "license", "stars", "forks", "archived",
                  "dormant", "pushed_at", "updated_at", "primary_category",
                  "ocpp_versions", "ocpi_versions"):
        assert blank[field] is None, field
    assert blank["categories"] == []  # the README's "Uncategorized" bucket is not data
    assert pipeline._row_categories({"full_name": "acme/blank", "categories": ""}) == [
        ("Uncategorized", None)]  # ...which the Markdown still uses
    assert blank["topics"] == [] and blank["discovered_via"] == []


def test_a_full_record_maps_every_field(tmp_path):
    records = export(tmp_path, [row("Acme/Server", topics="zeta|alpha", source="topic+readme",
                                    ocpi_versions="2.2.1", description=" an OCPP tool. ")])
    assert records["acme/server"] == {
        "id": "acme/server",
        "full_name": "Acme/Server",
        "url": "https://github.com/Acme/Server",
        "host": "github",
        "description": "an OCPP tool.",
        "primary_category": {"main": "OCPP", "sub": "Server"},
        "categories": [{"main": "OCPP", "sub": "Server"}],
        "ocpp_versions": ["1.6", "2.0.1"],
        "ocpi_versions": ["2.2.1"],
        "language": "Python",
        "license": "MIT License",
        "stars": 10,
        "forks": 2,
        "archived": False,
        "dormant": False,
        "deprecated": None,
        "curation": "selection",
        "pushed_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-02T00:00:00Z",
        "topics": ["alpha", "zeta"],
        "discovered_via": ["readme", "topic"],
    }


def test_an_unknown_last_commit_exports_an_unknown_dormancy(tmp_path):
    records = export(tmp_path, [
        row("forge/empty", pushed_at="", dormant="false"),
        row("forge/archived", pushed_at="", archived="true", dormant="true"),
    ])
    assert records["forge/empty"]["dormant"] is None
    assert records["forge/archived"]["dormant"] is True  # archived alone makes it dormant


def test_an_unknown_dormancy_leaves_the_markdown_unchanged(tmp_path):
    out = render(tmp_path, [row("forge/empty", pushed_at="", dormant="false")])
    assert "forge/empty" in (out / "README.md").read_text(encoding="utf-8")


# --- The manifest -------------------------------------------------------------------------

def test_render_records_the_projects_payload_in_the_manifest(tmp_path):
    out = render(tmp_path, [row("acme/a"), row("acme/b")])
    data = out / "data"
    manifest_raw = (data / "manifest.json").read_text(encoding="utf-8")
    manifest = json.loads(manifest_raw)
    assert manifest["schema_version"] == "1.0"
    entry = manifest["payloads"]["projects"]
    assert entry["file"] == "projects.json"
    assert entry["records"] == 2
    assert entry["sha256"] == hashlib.sha256((data / "projects.json").read_bytes()).hexdigest()
    infile = out / "repos.enriched.csv"
    assert entry["inputs"] == {"out/repos.enriched.csv": hashlib.sha256(infile.read_bytes()).hexdigest()}
    assert str(tmp_path) not in manifest_raw


def test_a_manifest_entry_survives_an_update_of_another_key(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    (data / "projects.json").write_text('{"projects": []}\n', encoding="utf-8")
    (data / "csms.json").write_text('{"products": [1]}\n', encoding="utf-8")
    (tmp_path / "csms.csv").write_text("slug\nx\n", encoding="utf-8")
    (tmp_path / "repos.enriched.csv").write_text("full_name\n", encoding="utf-8")

    pipeline.write_manifest(str(data), "csms", str(data / "csms.json"), ["csms.csv"], 1)
    pipeline.write_manifest(str(data), "projects", str(data / "projects.json"),
                            ["repos.enriched.csv"], 0)
    first = json.loads((data / "manifest.json").read_text(encoding="utf-8"))
    assert set(first["payloads"]) == {"csms", "projects"}
    assert first["payloads"]["csms"]["records"] == 1

    (data / "csms.json").write_text('{"products": [1, 2]}\n', encoding="utf-8")
    pipeline.write_manifest(str(data), "csms", str(data / "csms.json"), ["csms.csv"], 2)
    second = json.loads((data / "manifest.json").read_text(encoding="utf-8"))
    assert second["payloads"]["projects"] == first["payloads"]["projects"]
    assert second["payloads"]["csms"] == {
        "file": "csms.json",
        "sha256": hashlib.sha256((data / "csms.json").read_bytes()).hexdigest(),
        "records": 2,
        "inputs": {"csms.csv": hashlib.sha256((tmp_path / "csms.csv").read_bytes()).hexdigest()},
    }
    raw = (data / "manifest.json").read_text(encoding="utf-8")
    assert raw == json.dumps(second, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def test_a_bare_relative_path_is_written_in_place_without_a_temp_file(tmp_path):
    """`isolated` chdirs to tmp_path, so the file lands in the working directory."""
    payload = {"schema_version": pipeline.PUBLIC_SCHEMA_VERSION, "b": [1], "a": "é"}
    pipeline.write_public_json("x.json", payload)
    assert (tmp_path / "x.json").read_text(encoding="utf-8") == pipeline.dump_public_json(payload)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["x.json"]
