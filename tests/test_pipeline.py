"""Tests for the discovery pipeline's classification layer.

Nothing here reaches the network or spawns a classifier CLI: `enrich` runs
against a stubbed backend and a stubbed README fetch, and the backends
themselves are exercised through a stubbed `subprocess.run`.
"""

import csv
import pathlib
import re
import types
from datetime import datetime, timedelta, timezone

import pytest

import pipeline

# The autouse `no_network` fixture stubs this; its own tests need the real one.
real_fetch_readme_content = pipeline.fetch_readme_content


# --- Fixtures -----------------------------------------------------------------

def repo(full_name="acme/charger", **overrides):
    row = {field: "" for field in pipeline.CSV_FIELDS}
    row.update(full_name=full_name, pushed_at="2026-01-01T00:00:00Z")
    row.update(overrides)
    return row


def cached(full_name, categories, pushed_at="2026-01-01T00:00:00Z", description="",
           signals=""):
    return {"full_name": full_name, "pushed_at": pushed_at, "categories": categories,
            "description": description, "signals": signals}


def run_enrich(tmp_path, rows, classify, cache=(), expect_exit=False, **overrides):
    """Run `enrich` with a stubbed backend; return (enriched rows, written cache).

    `expect_exit` asserts the run bailed out. What it wrote is still read back:
    the CSV and the cache are flushed as each row is finalized, so a run that
    stops at the end has already published everything it decided.
    """
    infile = tmp_path / "repos.csv"
    with open(infile, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=pipeline.CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    cache_path = tmp_path / "classifications.csv"
    pipeline.save_classifications(cache_path, {r["full_name"]: r for r in cache})

    args = types.SimpleNamespace(
        infile=str(infile), out=str(tmp_path / "repos.enriched.csv"),
        cache=str(cache_path), token=None, limit=None, classifier="stub",
        skip_forks=False, skip_dormant=False, refresh=False,
        restamp=False, reask_category=None,
    )
    args.__dict__.update(overrides)

    pipeline.CLASSIFIERS["stub"] = classify
    try:
        if expect_exit:
            with pytest.raises(SystemExit):
                pipeline.enrich(args)
        else:
            pipeline.enrich(args)
    finally:
        del pipeline.CLASSIFIERS["stub"]

    with open(args.out, "r", encoding="utf-8", newline="") as f:
        enriched = list(csv.DictReader(f))
    return enriched, pipeline.load_classifications(cache_path)


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    monkeypatch.setattr(pipeline, "fetch_readme_content", lambda *a, **k: "")
    monkeypatch.setattr(pipeline, "auth_headers", lambda token: {})


# --- The CI guard: which empty categories are regressions ----------------------

def test_a_repo_that_lost_its_category_is_a_regression():
    before = {"acme/charger": cached("acme/charger", "OCPP > Server")}
    after = {"acme/charger": cached("acme/charger", "")}
    lost, arrived_empty = pipeline.classification_regressions(before, after)
    assert lost == ["acme/charger"]
    assert arrived_empty == []


def test_a_newly_discovered_repo_without_a_category_is_not_a_regression():
    """The failure that blocked the monthly refresh: new README-less repos.

    They never had a category to lose — an empty one records missing evidence,
    not a classification that regressed.
    """
    after = {"acme/newcomer": cached("acme/newcomer", "")}
    lost, arrived_empty = pipeline.classification_regressions({}, after)
    assert lost == []
    assert arrived_empty == ["acme/newcomer"]


def test_a_repo_that_was_already_empty_stays_silent():
    before = {"acme/charger": cached("acme/charger", "")}
    after = {"acme/charger": cached("acme/charger", "")}
    assert pipeline.classification_regressions(before, after) == ([], [])


def test_every_problem_is_reported_in_one_pass():
    before = {"b/lost": cached("b/lost", "OCPP > Server"),
              "a/lost": cached("a/lost", "OCPI > Libraries"),
              "c/kept": cached("c/kept", "OCPP > Misc")}
    after = {"b/lost": cached("b/lost", ""), "a/lost": cached("a/lost", ""),
             "c/kept": cached("c/kept", "OCPP > Misc"),
             "d/new": cached("d/new", ""), "e/new": cached("e/new", "")}
    lost, arrived_empty = pipeline.classification_regressions(before, after)
    assert lost == ["a/lost", "b/lost"]
    assert arrived_empty == ["d/new", "e/new"]


def test_a_repo_dropped_from_the_run_is_not_a_regression():
    before = {"acme/gone": cached("acme/gone", "OCPP > Server")}
    assert pipeline.classification_regressions(before, {}) == ([], [])


# --- The CI guard: a main category without a subcategory ----------------------

def test_a_repo_that_fell_back_to_a_bare_main_is_reported():
    """The #57 drift: a re-run turned classified repos into a bare `Other`."""
    cache = {"acme/cdk": cached("acme/cdk", "Other"),
             "acme/app": cached("acme/app", "OCPP > Misc|Other")}
    assert pipeline.bare_main_categories(cache) == ["acme/app", "acme/cdk"]


def test_a_bare_main_is_reported_whatever_the_history():
    """The contract forbids a bare main outright, so a newcomer filed directly
    under `Other` and a repo that was already bare break it just the same."""
    cache = {"acme/new": cached("acme/new", "Other"),
             "acme/old": cached("acme/old", "OCPP")}
    assert pipeline.bare_main_categories(cache) == ["acme/new", "acme/old"]


def test_classified_and_empty_repos_are_not_bare():
    """An empty category is `classification_regressions`' business."""
    cache = {"acme/sim": cached("acme/sim", "OCPP > Simulator|Other > Security"),
             "acme/none": cached("acme/none", "")}
    assert pipeline.bare_main_categories(cache) == []


def test_the_guard_warns_on_a_bare_main_without_failing(tmp_path, capsys):
    base = tmp_path / "base.csv"
    cache = tmp_path / "classifications.csv"
    pipeline.save_classifications(base, {})
    pipeline.save_classifications(cache, {"acme/new": cached("acme/new", "Other")})
    pipeline.check_classifications(types.SimpleNamespace(base=str(base), cache=str(cache)))
    out = capsys.readouterr().out
    assert "::warning::acme/new has a main category without a subcategory" in out
    assert "::error::" not in out


# --- The CI guard: a repo that lost a protocol category ------------------------

@pytest.fixture
def curation(monkeypatch):
    """Empty CATEGORY_OVERRIDES / ACCEPTED_PROTOCOL_LOSSES, filled per test.

    The guard tests never depend on the real curated entries.
    """
    overrides, accepted = {}, {}
    monkeypatch.setattr(pipeline, "CATEGORY_OVERRIDES", overrides)
    monkeypatch.setattr(pipeline, "ACCEPTED_PROTOCOL_LOSSES", accepted)
    return types.SimpleNamespace(overrides=overrides, accepted=accepted)


def losses(diff, status=None):
    """(full_name, protocol[, reason]) of the diff's protocol losses."""
    return [(r["full_name"], loss["protocol"]) + ((loss["reason"],) if loss["reason"] else ())
            for r in diff["repos"] for loss in r["protocol_losses"]
            if status is None or loss["status"] == status]


def entry(diff, full_name):
    return next(r for r in diff["repos"] if r["full_name"] == full_name)


def run_guard(tmp_path, before, after):
    base = tmp_path / "base.csv"
    cache = tmp_path / "classifications.csv"
    pipeline.save_classifications(base, {r["full_name"]: r for r in before})
    pipeline.save_classifications(cache, {r["full_name"]: r for r in after})
    pipeline.check_classifications(types.SimpleNamespace(base=str(base), cache=str(cache)))


def test_a_repo_that_lost_a_protocol_category_is_an_unexplained_loss(curation):
    """The #61 drift: a firmware that implements OCPP came back as `Other` only."""
    before = {"acme/fw": cached("acme/fw", "OCPP > Libraries"),
              "acme/meter": cached("acme/meter", "Eichrecht > Misc|Other > Battery")}
    after = {"acme/fw": cached("acme/fw", "Other > EVSE firmware"),
             "acme/meter": cached("acme/meter", "Other > Developer tools & libraries")}
    diff = pipeline.classification_diff(before, after)
    assert losses(diff) == losses(diff, "unexplained") == [("acme/fw", "OCPP"),
                                                           ("acme/meter", "Eichrecht")]
    fw = entry(diff, "acme/fw")
    assert fw["raw_before"] == "OCPP > Libraries"
    assert fw["raw_after"] == "Other > EVSE firmware"
    assert fw["removed"] == ["OCPP > Libraries"]
    assert fw["added"] == ["Other > EVSE firmware"]


def test_a_changed_protocol_subcategory_or_a_lost_other_is_not_a_protocol_loss(curation):
    before = {"acme/sim": cached("acme/sim", "OCPP > Server|Other > Home automation")}
    after = {"acme/sim": cached("acme/sim", "OCPP > Simulator")}
    diff = pipeline.classification_diff(before, after)
    assert losses(diff) == []
    sim = entry(diff, "acme/sim")
    assert sim["removed"] == ["OCPP > Server", "Other > Home automation"]
    assert sim["added"] == ["OCPP > Simulator"]


def test_an_emptied_or_new_repo_is_not_a_protocol_loss(curation):
    """An emptied category is the lost-category check's business, and a
    newcomer had nothing to lose: neither is a change to report here."""
    before = {"acme/lost": cached("acme/lost", "OCPP > Server")}
    after = {"acme/lost": cached("acme/lost", ""), "acme/new": cached("acme/new", "Other > Security")}
    diff = pipeline.classification_diff(before, after)
    assert losses(diff) == []
    assert [r["full_name"] for r in diff["repos"]] == ["acme/lost"]


def test_an_override_masks_a_raw_protocol_loss(curation):
    """A reviewed CATEGORY_OVERRIDES fix keeps the protocol on the page."""
    curation.overrides["acme/fw"] = "OCPP > Libraries|Other > EVSE firmware"
    before = {"acme/fw": cached("acme/fw", "OCPP > Libraries")}
    after = {"acme/fw": cached("acme/fw", "Other > EVSE firmware")}
    diff = pipeline.classification_diff(before, after)
    assert losses(diff) == losses(diff, "masked") == [("acme/fw", "OCPP")]
    fw = entry(diff, "acme/fw")
    assert fw["added"] == fw["removed"] == []
    assert fw["primary_changed"] is False
    assert fw["raw_after"] == "Other > EVSE firmware"


def test_alias_folding_adds_and_removes_nothing(curation):
    """`Charging station map` and `route planner` fold onto one label."""
    before = {"acme/map": cached("acme/map", "OCPI > Libraries|Other > Charging station map")}
    after = {"acme/map": cached("acme/map", "OCPI > Libraries|Other > route planner")}
    diff = pipeline.classification_diff(before, after)
    # Listed for its raw difference, with nothing moved on the page.
    amap = entry(diff, "acme/map")
    assert amap["added"] == amap["removed"] == []
    assert amap["before"] == amap["after"] == ["OCPI > Libraries", "Other > Maps & route planning"]
    assert amap["primary_changed"] is False
    assert losses(diff) == []


def test_a_primary_category_change_is_detected(curation):
    before = {"acme/sim": cached("acme/sim", "OCPP > Server|OCPI > Libraries")}
    after = {"acme/sim": cached("acme/sim", "OCPI > Libraries|OCPP > Server")}
    sim = entry(pipeline.classification_diff(before, after), "acme/sim")
    assert sim["primary_before"] == "OCPP > Server"
    assert sim["primary_after"] == "OCPI > Libraries"
    assert sim["primary_changed"] is True
    assert sim["added"] == sim["removed"] == []


def test_a_protocol_first_reorder_is_not_a_primary_change(curation):
    """The render sorts protocols ahead of `Other`, so the classifier's order
    between the two moves nothing on the page."""
    before = {"acme/ha": cached("acme/ha", "OCPP > Server|Other > Home automation")}
    after = {"acme/ha": cached("acme/ha", "Other > Home automation|OCPP > Server")}
    diff = pipeline.classification_diff(before, after)
    assert all(not r["primary_changed"] and not r["added"] and not r["removed"]
               for r in diff["repos"])


def test_an_accepted_loss_is_reported_with_its_reason(curation):
    curation.accepted["acme/client"] = {"OCPP": "A vendor API client, not OCPP."}
    before = {"acme/client": cached("acme/client", "OCPP > Libraries")}
    after = {"acme/client": cached("acme/client", "Other > Developer tools & libraries")}
    diff = pipeline.classification_diff(before, after)
    assert losses(diff) == losses(diff, "accepted") == [
        ("acme/client", "OCPP", "A vendor API client, not OCPP.")]
    assert diff["stale_exceptions"] == []


def test_an_accepted_loss_excuses_only_the_named_protocol(curation):
    curation.accepted["acme/client"] = {"OCPP": "A vendor API client, not OCPP."}
    before = {"acme/client": cached("acme/client", "OCPP > Libraries|OCPI > Libraries")}
    after = {"acme/client": cached("acme/client", "Other > Developer tools & libraries")}
    diff = pipeline.classification_diff(before, after)
    assert losses(diff, "accepted") == [("acme/client", "OCPP", "A vendor API client, not OCPP.")]
    assert losses(diff, "unexplained") == [("acme/client", "OCPI")]


def test_an_exception_is_stale_only_when_the_repo_or_the_loss_is_gone(curation):
    """Next month the base no longer has the protocol either: an unchanged repo
    still needs its exception, so it is not reported as stale."""
    curation.accepted.update({
        "acme/kept": {"OCPP": "Reviewed."},
        "acme/back": {"OCPP": "Reviewed."},
        "acme/gone": {"OCPI": "Reviewed."},
    })
    before = {"acme/kept": cached("acme/kept", "Other > Security"),
              "acme/back": cached("acme/back", "Other > Security")}
    after = {"acme/kept": cached("acme/kept", "Other > Security"),
             "acme/back": cached("acme/back", "OCPP > Server|Other > Security")}
    diff = pipeline.classification_diff(before, after)
    assert diff["stale_exceptions"] == [("acme/back", "OCPP"), ("acme/gone", "OCPI")]


def test_a_case_only_rename_is_the_same_repo(curation):
    before = {"EcoG-io/pyslac": cached("EcoG-io/pyslac", "iso15118 > SLAC")}
    after = {"ecog-io/pyslac": cached("ecog-io/pyslac", "")}
    assert pipeline.classification_regressions(before, after) == (["ecog-io/pyslac"], [])
    after = {"ecog-io/pyslac": cached("ecog-io/pyslac", "Other > Security")}
    diff = pipeline.classification_diff(before, after)
    assert losses(diff, "unexplained") == [("ecog-io/pyslac", "iso15118")]


def test_a_case_only_rename_is_neither_a_regression_nor_a_newcomer(tmp_path, capsys, curation):
    run_guard(tmp_path, [cached("EcoG-io/pyslac", "iso15118 > SLAC")],
              [cached("ecog-io/pyslac", "iso15118 > SLAC")])
    out = capsys.readouterr().out
    assert "::error::" not in out
    assert "::warning::" not in out


def test_a_case_duplicate_keeps_the_classified_row(curation):
    # Sorted, "Acme/fw" comes first: the classified row must win from either side.
    before = {"Acme/fw": cached("Acme/fw", "OCPP > Libraries"),
              "acme/fw": cached("acme/fw", "")}
    after = {"acme/fw": cached("acme/fw", "OCPP > Libraries")}
    assert pipeline.classification_diff(before, after)["repos"] == []
    assert pipeline.classification_regressions(before, after) == ([], [])


def test_the_guard_fails_on_an_unexplained_protocol_loss(tmp_path, capsys, curation):
    with pytest.raises(SystemExit) as excinfo:
        run_guard(tmp_path, [cached("acme/fw", "OCPP > Libraries")],
                  [cached("acme/fw", "Other > EVSE firmware")])
    assert excinfo.value.code == 1
    out = capsys.readouterr().out
    assert "::error::acme/fw lost its OCPP category" in out
    assert "1 unexplained protocol loss" in out
    assert "newly lost their category" not in out


def test_the_guard_reports_masked_and_accepted_losses_without_failing(tmp_path, capsys, curation):
    curation.overrides["acme/fw"] = "OCPP > Libraries"
    curation.accepted["acme/client"] = {"OCPP": "A vendor API client, not OCPP."}
    run_guard(tmp_path,
              [cached("acme/fw", "OCPP > Libraries"), cached("acme/client", "OCPP > Libraries"),
               cached("acme/sim", "OCPP > Server")],
              [cached("acme/fw", "Other > EVSE firmware"),
               cached("acme/client", "Other > Developer tools & libraries"),
               cached("acme/sim", "OCPP > Simulator")])
    out = capsys.readouterr().out
    assert "::error::" not in out
    assert "acme/fw lost OCPP in its raw categories; CATEGORY_OVERRIDES keeps it" in out
    assert "acme/client lost OCPP (accepted: A vendor API client, not OCPP.)" in out
    assert "acme/sim: + OCPP > Simulator; - OCPP > Server" in out
    assert "1 masked, 1 accepted" in out


def test_the_guard_reads_the_base_from_stdin(tmp_path, capsys, monkeypatch, curation):
    import io
    base = tmp_path / "base.csv"
    pipeline.save_classifications(base, {"Acme/FW": cached("Acme/FW", "OCPP > Libraries")})
    monkeypatch.setattr("sys.stdin", io.StringIO(base.read_text(encoding="utf-8")))
    cache = tmp_path / "classifications.csv"
    pipeline.save_classifications(cache, {"acme/fw": cached("acme/fw", "Other > EVSE firmware")})
    with pytest.raises(SystemExit) as excinfo:
        pipeline.check_classifications(types.SimpleNamespace(base="-", cache=str(cache)))
    assert excinfo.value.code == 1
    assert "::error::acme/fw lost its OCPP category" in capsys.readouterr().out


# --- The guard's Markdown report ------------------------------------------------

def guard_report(tmp_path, before, after, expect_exit=False, **extra):
    """Run the guard with `--report` and return the report it wrote."""
    base = tmp_path / "base.csv"
    cache = tmp_path / "classifications.csv"
    report = tmp_path / "report" / "classification-report.md"
    report.parent.mkdir(exist_ok=True)
    pipeline.save_classifications(base, {r["full_name"]: r for r in before})
    pipeline.save_classifications(cache, {r["full_name"]: r for r in after})
    args = types.SimpleNamespace(base=str(base), cache=str(cache), report=str(report),
                                 base_projects=None,
                                 projects=str(tmp_path / "absent-projects.json"))
    args.__dict__.update(extra)
    if expect_exit:
        with pytest.raises(SystemExit) as excinfo:
            pipeline.check_classifications(args)
        assert excinfo.value.code == 1
        # The report exists for the run that blocked, which is the one to review.
        assert report.exists()
    else:
        pipeline.check_classifications(args)
    return report.read_text(encoding="utf-8")


def section(report, title):
    """The body of the `## title` section of a report, up to the next heading."""
    lines = report.split("\n")
    start = lines.index(f"## {title}")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("#")),
               len(lines))
    return "\n".join(lines[start + 1:end])


def count(report, label):
    return next(line for line in report.split("\n") if line.startswith(f"| {label} |"))


def test_the_report_lists_each_class_with_raw_and_effective_categories(tmp_path, capsys,
                                                                        curation):
    curation.overrides["acme/sim"] = "OCPP > Simulator"
    curation.accepted["acme/client"] = {"OCPP": "A vendor API client, not OCPP."}
    before = [cached("acme/fw", "OCPP > Libraries"),
              cached("acme/sim", "OCPP > Simulator"),
              cached("acme/client", "OCPP > Misc"),
              cached("acme/move", "OCPP > Server"),
              cached("acme/empty", "OCPI > Libraries")]
    after = [cached("acme/fw", "Other > EVSE firmware|Other > Security"),
             cached("acme/sim", "Other > Developer tools & libraries"),
             cached("acme/client", "Other > Developer tools & libraries"),
             cached("acme/move", "OCPI > Libraries|OCPP > Server"),
             cached("acme/empty", ""),
             cached("acme/new", ""),
             cached("acme/bare", "Other")]
    report = guard_report(tmp_path, before, after, expect_exit=True)

    assert report.startswith("# Classification report\n\n")
    assert count(report, "Lost category") == "| Lost category | 1 |"
    assert count(report, "Unexplained protocol loss") == "| Unexplained protocol loss | 1 |"
    assert count(report, "Masked by an override") == "| Masked by an override | 1 |"
    assert count(report, "Accepted protocol loss") == "| Accepted protocol loss | 1 |"
    assert count(report, "Stale exception") == "| Stale exception | 0 |"
    assert count(report, "Primary category change") == "| Primary category change | 3 |"
    assert count(report, "Newcomer without a category") == "| Newcomer without a category | 1 |"
    assert count(report, "Bare main category") == "| Bare main category | 1 |"

    assert "| `acme/empty` | OCPI > Libraries → (none) | OCPI > Libraries → (none) |" \
        in section(report, "Lost category")
    assert ("| `acme/fw` | OCPP | OCPP > Libraries → Other > EVSE firmware\\|Other > Security"
            " | OCPP > Libraries → Other > EVSE firmware, Other > Security |") \
        in section(report, "Unexplained protocol loss")
    assert "| `acme/sim` | OCPP |" in section(report, "Masked by an override")
    assert "| `acme/client` | OCPP |" in section(report, "Accepted protocol loss")
    assert "`A vendor API client, not OCPP.` |" in section(report, "Accepted protocol loss")
    assert "| `acme/move` | OCPP > Server → OCPI > Libraries |" \
        in section(report, "Primary category change")
    # An empty cell reads `|  |`, which markdownlint's MD060 rejects.
    assert "| `acme/move` | OCPI > Libraries | (none) |" in section(report, "Category change")
    assert "|  |" not in report
    assert "| `acme/new` |" in section(report, "Newcomer without a category")
    assert "| `acme/bare` | Other |" in section(report, "Bare main category")
    # Nothing was stale: the class is counted, not given an empty table.
    assert "## Stale exception" not in report
    assert "No projects.json baseline: curation movements not reported." in report


def test_the_report_counts_stale_exceptions(tmp_path, curation):
    curation.accepted["acme/gone"] = {"OCPP": "Reviewed."}
    report = guard_report(tmp_path, [cached("acme/x", "OCPP > Server")],
                          [cached("acme/x", "OCPP > Server")])
    assert count(report, "Stale exception") == "| Stale exception | 1 |"
    assert "| `acme/gone` | OCPP |" in section(report, "Stale exception")


def test_the_report_escapes_pipes_in_every_cell(tmp_path, curation):
    curation.accepted["acme/client"] = {"OCPP": "Client | not a server."}
    report = guard_report(tmp_path, [cached("acme/client", "OCPP > Misc|Other > Security")],
                          [cached("acme/client", "Other > Security")])
    table = section(report, "Accepted protocol loss")
    assert "OCPP > Misc\\|Other > Security → Other > Security" in table
    assert "Client \\| not a server." in table
    for line in table.split("\n"):
        if line.startswith("| `acme/client`"):
            assert line.replace("\\|", "").count("|") == 6


def outside_code_spans(markdown):
    """`markdown` with every inline code span removed, as CommonMark reads them:
    a run of N backticks closes on the next run of exactly N."""
    return re.sub(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", "", markdown, flags=re.S)


def unescaped_pipes(line):
    return line.replace("\\|", "").count("|")


EVIL = "[x](https://evil) <img src=x> @someone `tick` ``ticks"


def test_the_report_neutralises_untrusted_text(tmp_path, curation):
    """Categories come from an LLM and names from GitHub; the report is published
    unescaped in the PR body and the job summary, so neither may open a link, an
    image, HTML or a mention there."""
    name = "acme/" + EVIL + " | x\\"
    before = [cached(name, "Evil<b> > Server|OCPP > Server"),
              cached("acme/bare", "OCPP > Server")]
    after = [cached(name, "OCPP > Server|Other > " + EVIL + "\nline"),
             cached("acme/bare", "`Other` @someone")]
    report = guard_report(tmp_path, before, after, expect_exit=True)

    outside = outside_code_spans(report)
    for marker in ("](", "<img", "<b>", "@someone", "evil", "tick"):
        assert marker not in outside
    # A known label stays readable; an unknown one is flagged, then quoted.
    assert "OCPP > Server" in outside
    assert "(unknown label) ```Other > [x](https://evil)" in report
    lines = report.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("| ") and lines[i - 1] == "":
            header = unescaped_pipes(line)
            j = i + 1
            while j < len(lines) and lines[j].startswith("|"):
                assert unescaped_pipes(lines[j]) == header, lines[j]
                j += 1


def test_the_bare_main_row_shows_the_bare_duplicate(tmp_path, curation):
    """An older cache may hold two spellings of one repo; the bare one is the
    one reported, so its row must show its own categories."""
    before = [cached("Acme/fw", "OCPP > Server")]
    after = [cached("Acme/fw", "OCPP > Server"), cached("acme/fw", "Other")]
    report = guard_report(tmp_path, before, after)
    assert "| `acme/fw` | Other |" in section(report, "Bare main category")


def test_the_report_is_deterministic(tmp_path, curation):
    before = [cached("b/two", "OCPP > Server"), cached("A/one", "OCPI > Libraries")]
    after = [cached("A/one", "OCPI > Hub"), cached("b/two", "OCPP > Server|OCPI > Hub")]
    runs = []
    for name in ("first", "second"):
        (tmp_path / name).mkdir()
        runs.append((tmp_path / name / "report" / "classification-report.md",
                     guard_report(tmp_path / name, before, after)))
    first = runs[0][1]
    assert runs[0][0].read_bytes() == runs[1][0].read_bytes()
    assert first.endswith("\n") and not first.endswith("\n\n")
    assert first.index("| `A/one` |") < first.index("| `b/two` |")


def test_the_report_is_markdownlint_shaped(tmp_path, curation):
    """Blank lines around headings and tables, one title, no double blank line."""
    report = guard_report(tmp_path, [cached("acme/fw", "OCPP > Libraries")],
                          [cached("acme/fw", "Other > EVSE firmware")], expect_exit=True)
    lines = report.rstrip("\n").split("\n")
    assert sum(1 for line in lines if line.startswith("# ")) == 1
    assert "\n\n\n" not in report
    for i, line in enumerate(lines):
        if line.startswith("#") and i:
            assert lines[i - 1] == "" and lines[i + 1] == ""
        if line.startswith("|") and (i == 0 or not lines[i - 1].startswith("|")):
            assert lines[i - 1] == ""
        if line.startswith("|") and i + 1 < len(lines) and not lines[i + 1].startswith("|"):
            assert lines[i + 1] == ""


def test_the_guard_writes_no_report_without_the_flag(tmp_path, curation):
    run_guard(tmp_path, [cached("acme/x", "OCPP > Server")], [cached("acme/x", "OCPP > Server")])
    assert not list(tmp_path.glob("*.md"))


# --- Curation movements from the projects.json export -----------------------------

def projects_file(path, records):
    import json
    path.write_text(json.dumps({"schema_version": "1.0", "projects": [
        {"id": full_name.lower(), "full_name": full_name, "curation": block}
        for full_name, block in records]}), encoding="utf-8")
    return str(path)


def test_the_report_lists_curation_movements(tmp_path, capsys, curation):
    base = projects_file(tmp_path / "base-projects.json",
                         [("acme/up", "to_refine"), ("acme/down", "selection"),
                          ("acme/same", "selection"), ("acme/gone", "dormant")])
    fresh = projects_file(tmp_path / "projects.json",
                          [("acme/up", "selection"), ("acme/down", "dormant"),
                           ("acme/same", "selection"), ("acme/new", "to_refine")])
    rows = [cached("acme/x", "OCPP > Server")]
    report = guard_report(tmp_path, rows, rows, base_projects=base, projects=fresh)
    assert count(report, "Curation movement") == "| Curation movement | 2 |"
    assert count(report, "Project added to the export") == "| Project added to the export | 1 |"
    assert count(report, "Project removed from the export") \
        == "| Project removed from the export | 1 |"
    moves = section(report, "Curation movement")
    assert "| `acme/down` | `selection` → `dormant` |" in moves
    assert "| `acme/up` | `to_refine` → `selection` |" in moves
    assert "acme/same" not in report
    assert "| `acme/new` | `to_refine` |" in section(report, "Project added to the export")
    assert "| `acme/gone` | `dormant` |" in section(report, "Project removed from the export")
    assert "No projects.json baseline" not in report
    # Fresh metadata moves blocks: that never fails the guard.
    assert "✅" in capsys.readouterr().out


@pytest.mark.parametrize("which", ["base", "flag"])
def test_a_missing_projects_baseline_is_reported_not_failed(tmp_path, curation, which):
    fresh = projects_file(tmp_path / "projects.json", [("acme/x", "dormant")])
    extra = {"base": {"base_projects": str(tmp_path / "nope.json"), "projects": fresh},
             "flag": {"base_projects": None, "projects": fresh}}[which]
    rows = [cached("acme/x", "OCPP > Server")]
    report = guard_report(tmp_path, rows, rows, **extra)
    assert "No projects.json baseline: curation movements not reported." in report
    assert "| Curation movement |" not in report


def test_a_missing_fresh_export_is_not_reported_as_a_missing_baseline(tmp_path, capsys,
                                                                      curation):
    base = projects_file(tmp_path / "base-projects.json", [("acme/x", "selection")])
    missing = tmp_path / "nope.json"
    rows = [cached("acme/x", "OCPP > Server")]
    report = guard_report(tmp_path, rows, rows, base_projects=base, projects=str(missing))
    # The baseline is there: saying it is not would send the reviewer the wrong way.
    assert "No projects.json baseline" not in report
    assert (f"Curation movements not reported: the fresh export {missing} is missing."
            in report)
    assert "| Curation movement |" not in report
    out = capsys.readouterr().out
    assert f"::warning::Curation movements not reported: the fresh export {missing}" in out
    assert "✅" in out


@pytest.mark.parametrize("which", ["base", "fresh"])
@pytest.mark.parametrize("content", ["{not json", '{"projects": [{"full_name": "a/b"}]}',
                                     '["a list"]'])
def test_an_invalid_projects_file_warns_without_failing_the_guard(tmp_path, capsys, curation,
                                                                  content, which):
    bad = tmp_path / f"{which}-projects-bad.json"
    bad.write_text(content, encoding="utf-8")
    good = projects_file(tmp_path / "projects.json", [("acme/x", "selection")])
    extra = {"base": {"base_projects": str(bad), "projects": good},
             "fresh": {"base_projects": good, "projects": str(bad)}}[which]
    rows = [cached("acme/x", "OCPP > Server")]
    # Curation movements are informational: a corrupt baseline or an export
    # schema change must not block the classification refresh.
    report = guard_report(tmp_path, rows, rows, **extra)
    assert f"Curation movements not reported: {bad}" in report
    assert "No projects.json baseline" not in report
    out = capsys.readouterr().out
    assert f"::warning::Curation movements not reported: {bad}" in out
    assert "::error::" not in out
    assert "✅" in out


@pytest.mark.parametrize("which", ["base", "fresh"])
def test_a_non_string_project_id_warns_without_failing_the_guard(tmp_path, capsys, curation,
                                                                 which):
    """An int id next to string ids made `curation_movements` sort mixed keys:
    an uncaught TypeError, where the guard must only warn."""
    import json
    bad = tmp_path / f"{which}-projects-bad.json"
    bad.write_text(json.dumps({"projects": [
        {"id": 1, "full_name": "acme/int", "curation": "selection"},
        {"id": "acme/y", "full_name": "acme/y", "curation": "selection"}]}), encoding="utf-8")
    good = projects_file(tmp_path / "projects.json",
                         [("acme/x", "selection"), ("acme/z", "dormant")])
    extra = {"base": {"base_projects": str(bad), "projects": good},
             "fresh": {"base_projects": good, "projects": str(bad)}}[which]
    rows = [cached("acme/x", "OCPP > Server")]
    report = guard_report(tmp_path, rows, rows, **extra)
    assert f"Curation movements not reported: {bad}" in report
    out = capsys.readouterr().out
    assert f"::warning::Curation movements not reported: {bad}" in out
    assert "✅" in out


def test_an_invalid_projects_file_leaves_a_regression_failing(tmp_path, capsys, curation):
    bad = tmp_path / "base-projects.json"
    bad.write_text("{not json", encoding="utf-8")
    fresh = projects_file(tmp_path / "projects.json", [("acme/x", "selection")])
    report = guard_report(tmp_path, [cached("acme/x", "OCPP > Server")], [cached("acme/x", "")],
                          expect_exit=True, base_projects=str(bad), projects=fresh)
    assert f"Curation movements not reported: {bad}" in report
    assert "::error::acme/x lost the category it had." in capsys.readouterr().out


def test_accepted_protocol_losses_are_keyed_lowercase_with_reasons():
    for full_name, protocols in pipeline.ACCEPTED_PROTOCOL_LOSSES.items():
        assert full_name == full_name.lower()
        assert protocols
        for protocol, reason in protocols.items():
            # A misspelt main would excuse nothing and never read as stale.
            assert protocol in pipeline.CATEGORY_TREE and protocol != "Other"
            assert reason.strip()


# --- Rendering: placement and subcategories outside the taxonomy --------------

def test_a_protocol_category_places_the_repo_before_other():
    """The README lists a repo under its first category only, so `Other` first
    pulled OCPP implementations out of the OCPP section."""
    row = {"full_name": "acme/ha", "categories": "Other > Home automation|OCPP > Server"}
    assert pipeline._row_categories(row) == [("OCPP", "Server"), ("Other", "Home automation")]


def test_an_other_only_repo_keeps_its_order():
    row = {"full_name": "acme/evcc", "categories": "Other > Energy management|Other > Mobile app"}
    assert pipeline._row_categories(row) == [("Other", "Energy management"),
                                             ("Other", "Mobile app")]


def test_a_subcategory_outside_the_taxonomy_is_reported():
    rows = [{"full_name": "a/jobs", "categories": "Other > Job portal"},
            {"full_name": "b/ha", "categories": "Other > Home Assistant Integration"},
            {"full_name": "c/srv", "categories": "OCPP > Server|OCPP > Dashboard"}]
    assert pipeline.unknown_subcategories(rows) == {"OCPP > Dashboard": ["c/srv"],
                                                    "Other > Job portal": ["a/jobs"]}


def test_render_warns_about_a_subcategory_outside_the_taxonomy(tmp_path, capsys):
    enriched = tmp_path / "repos.enriched.csv"
    fields = pipeline.CSV_FIELDS + ["categories", "ocpp_versions", "ocpi_versions"]
    with open(enriched, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerow({**repo("a/jobs", promoted="2"), "categories": "Other > Job portal"})
    pipeline.render(types.SimpleNamespace(infile=str(enriched), out=str(tmp_path / "legacy.md"),
                                          readme=None))
    assert "::warning::Other > Job portal is not in CATEGORY_TREE" in capsys.readouterr().out


# --- Parsing the classifier's answer -------------------------------------------

def test_prose_bullets_are_not_taken_for_categories():
    """The 2026-11 run filed uhi22/pyPLC under six "main categories" that were
    the model's bulleted summary of its README."""
    text = (
        "Description: A Python toolkit for ISO 15118 charging communication.\n"
        "- Implements ISO 15118 V2G communication protocols\n"
        "- Works with SLAC and V2G protocols\n"
        "Categories:\n"
        "- iso15118 > Misc\n"
        "- Other > Developer tools & libraries\n"
    )
    assert pipeline.parse_classification(text)[1] == [
        ("iso15118", "Misc"), ("Other", "Developer tools & libraries")]


def test_a_bulleted_bare_main_still_parses():
    """The contract forbids it, but dropping it would empty the category."""
    assert pipeline.parse_categories("- Other\n- OCPP") == [("Other", None), ("OCPP", None)]


# --- The taxonomy: every main offers a closed subcategory list -----------------

def test_every_main_category_offers_subcategories():
    """A main with no subcategory showed up as a bare `- Other` in the prompt,
    which the classifier answered with a bare `Other` or an invented label."""
    assert all(subs for subs in pipeline.CATEGORY_TREE.values())


def test_no_subcategory_contains_the_prompt_separator():
    """CATEGORY_TREE_TEXT joins subcategories with ", "."""
    assert not [sub for subs in pipeline.CATEGORY_TREE.values() for sub in subs if "," in sub]


def test_every_other_alias_folds_onto_the_closed_list():
    """`_sub_key` orders by exact list index, so a target spelled differently
    from its taxonomy entry would render as an unknown, trailing bucket."""
    assert set(pipeline.SUBCATEGORY_ALIASES.values()) <= set(pipeline.CATEGORY_TREE["Other"])


def test_every_alias_key_is_lowercase():
    """`_canon_sub` looks aliases up by the lowercased label."""
    assert all(key == key.lower() for key in pipeline.SUBCATEGORY_ALIASES)


def test_a_legacy_other_label_folds_onto_the_closed_list():
    row = {"full_name": "acme/ha", "categories": "Other > Home Assistant Integration"}
    assert pipeline._row_categories(row) == [("Other", "Home automation")]


def test_aliases_only_apply_under_other():
    """`simulator` and `libraries` are Other aliases, but also protocol subcategories."""
    row = {"full_name": "acme/sim", "categories": "OCPP > Simulator|OCPI > Libraries"}
    assert pipeline._row_categories(row) == [("OCPP", "Simulator"), ("OCPI", "Libraries")]


def test_a_case_variant_folds_onto_its_taxonomy_label():
    row = {"full_name": "acme/app", "categories": "Other > Mobile App|OCPP > misc"}
    assert pipeline._row_categories(row) == [("OCPP", "Misc"), ("Other", "Mobile app")]


def test_every_category_override_uses_the_taxonomy():
    for full_name, raw in pipeline.CATEGORY_OVERRIDES.items():
        for chunk in raw.split("|"):
            main, sub = map(str.strip, chunk.split(">", 1))
            assert sub in pipeline.CATEGORY_TREE[main], (full_name, chunk)


@pytest.mark.parametrize("main, sub", [
    ("OpenADR", "VEN & VTN"), ("OSCP", "Libraries"),
    ("OCPP", "Testing & conformance"), ("OCPP", "Message inspection"),
    ("OCPP", "Security testing"), ("iso15118", "EXI codecs"),
    ("iso15118", "SLAC"), ("iso15118", "Message inspection"),
    ("iso15118", "Testing & conformance"), ("iso15118", "Security testing"),
    ("Other", "Data models & identifiers"), ("Other", "Grid simulation"),
])
def test_specialist_tools_have_explicit_taxonomy_slots(main, sub):
    assert sub in pipeline.CATEGORY_TREE[main]


def test_trace_inspection_is_not_filed_as_a_protocol_library():
    assert pipeline._row_categories({"full_name": "dspace-group/dsV2Gshark"})[0] == (
        "iso15118", "Message inspection")


def test_gocpi_is_listed_as_a_go_library_despite_github_language_statistics():
    row = repo("shiv3/gocpi", categories="OCPI > Libraries", language="TypeScript",
               html_url="https://github.com/shiv3/gocpi", description="An OCPI library for Go.")
    lines = []
    pipeline._render_grouped([pipeline._apply_overrides(row)], lines)
    assert "##### Go" in lines
    assert "##### TypeScript" not in lines


def test_new_grid_protocols_keep_protocol_priority_and_single_listing():
    row = repo("acme/flex", categories="Other > Energy management|OpenADR > VEN & VTN",
               html_url="https://example.com/flex", description="Demand response service.")
    assert pipeline._row_categories(row)[0] == ("OpenADR", "VEN & VTN")
    lines = []
    pipeline._render_grouped([row], lines)
    assert sum("https://example.com/flex" in line for line in lines) == 1
    assert "### OpenADR" in lines


# --- The classifier contract: one rule in every copy ---------------------------

ROOT = pathlib.Path(__file__).resolve().parent.parent

CONTRACT_COPIES = {
    "claude agent": lambda: (ROOT / ".claude/agents/repo-classifier.md").read_text("utf-8"),
    "codex agent": lambda: (ROOT / ".codex/agents/repo-classifier.toml").read_text("utf-8"),
    "in-prompt": lambda: pipeline.CLASSIFIER_INSTRUCTIONS,
}


@pytest.mark.parametrize("copy", CONTRACT_COPIES)
def test_no_contract_copy_allows_a_bare_main(copy):
    text = CONTRACT_COPIES[copy]()
    assert "on its own" not in text
    assert "- Main\n" not in text + "\n"


@pytest.mark.parametrize("copy", CONTRACT_COPIES)
def test_every_contract_copy_keeps_protocol_categories_ahead_of_other(copy):
    text = " ".join(CONTRACT_COPIES[copy]().split())
    assert "never replaces a protocol" in text
    assert "speaks" in text  # implementing a protocol, not mentioning it, is the test
    assert "OCMF" in text  # the model filed OCMF libraries as "Other protocols"


@pytest.mark.parametrize("copy", CONTRACT_COPIES)
def test_every_contract_copy_requires_a_subcategory(copy):
    assert "always carries a subcategory" in " ".join(CONTRACT_COPIES[copy]().split())


@pytest.mark.parametrize("copy", CONTRACT_COPIES)
def test_every_contract_copy_distinguishes_developer_tools_from_certification(copy):
    text = " ".join(CONTRACT_COPIES[copy]().split())
    for rule in ("These labels do not imply official certification.",
                 "EXI encoders/decoders in EXI codecs", "ISO 15118-3 matching in SLAC",
                 "OpenADR for documented", "Other > Grid simulation"):
        assert rule in text


def test_navigation_includes_editorial_guides_without_duplicating_project_links(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# List\n\n## Contents\n\n## Regulation & Standards Bodies\n\n"
                      "### Regulatory Frameworks\n\n## Smart Charging & Grid Integration\n\n"
                      "## Testing & Conformance\n\n## Tools and Resources\n\n"
                      "### OpenADR\n\n#### VEN & VTN\n\n"
                      "- [a/b](https://example.com/project) - A tool.\n", encoding="utf-8")
    toc = pipeline._build_toc(readme)
    assert "[Regulation & Standards Bodies](#regulation--standards-bodies)" in toc
    assert "[Regulatory Frameworks](#regulatory-frameworks)" in toc
    assert "[Smart Charging & Grid Integration](#smart-charging--grid-integration)" in toc
    assert "[Testing & Conformance](#testing--conformance)" in toc
    assert "[OpenADR](#openadr)" in toc
    assert "VEN & VTN" not in toc


# --- Classifying a repo that has no README ------------------------------------

def test_a_readme_is_enough_to_classify():
    assert pipeline.has_classifiable_signal(repo(), "# Acme\nAn OCPP server.")


def test_the_github_description_alone_is_enough():
    """A repo can legitimately ship no README; the prompt still carries this."""
    assert pipeline.has_classifiable_signal(
        repo(description="EV charger firmware archive by device type"), "")


def test_the_topics_alone_are_enough():
    assert pipeline.has_classifiable_signal(repo(topics="ocpp|emobility"), "")


def test_a_repo_with_no_signal_at_all_is_not_classifiable():
    assert not pipeline.has_classifiable_signal(repo(), "")


def test_blank_text_does_not_count_as_signal():
    assert not pipeline.has_classifiable_signal(repo(description="   "), "\n \n")


def test_the_prompt_says_so_when_there_is_no_readme():
    prompt = pipeline.build_classifier_prompt(repo(description="An OCPP server"), "")
    assert "no README" in prompt


# --- Backend failure semantics ------------------------------------------------

def stub_subprocess(monkeypatch, returncode=0, stdout="", raises=None):
    def fake_run(*args, **kwargs):
        if raises:
            raise raises
        return types.SimpleNamespace(returncode=returncode, stdout=stdout, stderr="boom")
    monkeypatch.setattr(pipeline.subprocess, "run", fake_run)


@pytest.mark.parametrize("backend", [pipeline.classify_with_claude,
                                     pipeline.classify_with_codex,
                                     pipeline.classify_with_copilot])
def test_a_hard_backend_failure_is_not_an_empty_classification(monkeypatch, backend):
    """`None` (the CLI failed) must stay distinguishable from `("", [])`."""
    stub_subprocess(monkeypatch, returncode=1)
    assert backend(repo(description="An OCPP server"), "# Acme") is None


@pytest.mark.parametrize("backend", [pipeline.classify_with_claude,
                                     pipeline.classify_with_codex,
                                     pipeline.classify_with_copilot])
def test_a_backend_exception_is_a_hard_failure_too(monkeypatch, backend):
    stub_subprocess(monkeypatch, raises=TimeoutError("timed out"))
    assert backend(repo(description="An OCPP server"), "# Acme") is None


@pytest.mark.parametrize("backend", [pipeline.classify_with_claude,
                                     pipeline.classify_with_codex,
                                     pipeline.classify_with_copilot])
def test_no_signal_yields_an_empty_classification_without_calling_the_cli(monkeypatch, backend):
    def explode(*args, **kwargs):
        raise AssertionError("the CLI must not be spawned with nothing to classify")
    monkeypatch.setattr(pipeline.subprocess, "run", explode)
    assert backend(repo(), "") == ("", [])


# --- The Copilot command line -------------------------------------------------

def capture_copilot_cmd(monkeypatch):
    """Run the copilot backend against a stubbed CLI; return the argv it built."""
    seen = {}

    def fake_run(cmd, **kwargs):
        seen["cmd"] = cmd
        return types.SimpleNamespace(
            returncode=0, stdout="Description: An OCPP server.\nCategories:\n- OCPP > Server",
            stderr="")

    monkeypatch.setattr(pipeline.subprocess, "run", fake_run)
    pipeline.classify_with_copilot(repo(description="An OCPP server"), "# Acme")
    return seen["cmd"]


def test_the_copilot_backend_disables_the_builtin_mcp_servers(monkeypatch):
    """The GitHub MCP server's tool definitions ride in the system prompt.

    Measured at ~1.4k tokens of the ~17.8k every invocation pays for, and the
    prompt is self-contained — no tool has anything to add.
    """
    assert "--disable-builtin-mcps" in capture_copilot_cmd(monkeypatch)


def test_the_copilot_backend_pins_the_configured_model(monkeypatch):
    """`auto` resolved to a frontier model, which bills ~10x a lightweight one
    for a one-sentence-plus-categories answer."""
    monkeypatch.setattr(pipeline, "CLASSIFIER_COPILOT_MODEL", "gpt-5.6-luna")
    cmd = capture_copilot_cmd(monkeypatch)
    assert cmd[cmd.index("--model") + 1] == "gpt-5.6-luna"


def test_the_copilot_backend_omits_the_model_flag_when_unpinned(monkeypatch):
    monkeypatch.setattr(pipeline, "CLASSIFIER_COPILOT_MODEL", "")
    assert "--model" not in capture_copilot_cmd(monkeypatch)


# --- enrich: what reaches the durable cache -----------------------------------

def test_a_classified_repo_lands_in_the_cache(tmp_path):
    enriched, cache = run_enrich(
        tmp_path, [repo()], lambda row, readme: ("An OCPP server.", [("OCPP", "Server")]))
    assert enriched[0]["categories"] == "OCPP > Server"
    assert cache["acme/charger"]["categories"] == "OCPP > Server"
    assert cache["acme/charger"]["description"] == "An OCPP server."


def test_each_answer_is_on_disk_before_the_next_repo_is_asked(tmp_path):
    """A full re-classification outlives a 2-hour job limit, and a killed run
    runs no `finally`: an answer saved only at the end is an answer paid for
    and lost."""
    seen_on_disk = {}

    def classify(row, readme):
        seen_on_disk[row["full_name"]] = set(
            pipeline.load_classifications(tmp_path / "classifications.csv"))
        return "A charger tool.", [("OCPP", "Misc")]

    run_enrich(tmp_path, [repo("acme/first", description="x"),
                          repo("acme/second", description="y")], classify)
    assert "acme/first" in seen_on_disk["acme/second"]


def test_each_save_writes_its_own_temp_file(tmp_path, monkeypatch):
    """A shared temp name lets one save truncate another's half-written file
    before it is swapped in."""
    staged = []
    real_replace = pipeline.os.replace
    monkeypatch.setattr(pipeline.os, "replace",
                        lambda src, dst: (staged.append(src), real_replace(src, dst)))
    path = tmp_path / "classifications.csv"
    pipeline.save_classifications(path, {"acme/a": cached("acme/a", "OCPP > Misc")})
    pipeline.save_classifications(path, {"acme/b": cached("acme/b", "OCPP > Misc")})
    assert len(set(staged)) == 2
    assert all(pathlib.Path(src).parent == tmp_path for src in staged)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["classifications.csv"]
    assert set(pipeline.load_classifications(path)) == {"acme/b"}


def test_an_empty_classification_is_cached(tmp_path):
    """No README, no description, no topics: the emptiness is the answer.

    Caching it is what stops every run from re-asking about a repo that has
    nothing to read.
    """
    enriched, cache = run_enrich(tmp_path, [repo()], lambda row, readme: ("", []))
    assert enriched[0]["categories"] == ""
    assert cache["acme/charger"]["pushed_at"] == "2026-01-01T00:00:00Z"


def test_a_hard_failure_leaves_the_cache_untouched(tmp_path):
    """So the next run retries, instead of freezing the emptiness until the
    repo is pushed again."""
    previous = cached("acme/charger", "OCPP > Server", pushed_at="2025-01-01T00:00:00Z",
                      description="An OCPP server.", signals="a-stale-signature")
    enriched, cache = run_enrich(tmp_path, [repo()], lambda row, readme: None,
                                 cache=[previous], expect_exit=True)
    assert cache["acme/charger"]["pushed_at"] == "2025-01-01T00:00:00Z"
    assert cache["acme/charger"]["categories"] == "OCPP > Server"


def test_a_hard_failure_keeps_the_stale_category_in_the_listing(tmp_path):
    """A classifier outage must not blank the rendered listing."""
    previous = cached("acme/charger", "OCPP > Server", pushed_at="2025-01-01T00:00:00Z",
                      description="An OCPP server.", signals="a-stale-signature")
    enriched, _ = run_enrich(tmp_path, [repo()], lambda row, readme: None,
                             cache=[previous], expect_exit=True)
    assert enriched[0]["categories"] == "OCPP > Server"
    assert enriched[0]["description"] == "An OCPP server."


def test_a_hard_failure_on_an_unknown_repo_yields_no_category(tmp_path):
    enriched, cache = run_enrich(tmp_path, [repo()], lambda row, readme: None,
                                 expect_exit=True)
    assert enriched[0]["categories"] == ""
    assert "acme/charger" not in cache


def test_an_unchanged_repo_is_reused_without_calling_the_backend(tmp_path):
    def explode(row, readme):
        raise AssertionError("a cache hit must not reach the backend")
    entry = repo(description="An OCPP server", topics="ocpp")
    enriched, _ = run_enrich(
        tmp_path, [entry], explode,
        cache=[cached("acme/charger", "OCPP > Server",
                      signals=pipeline.classifier_signature(entry, ""))])
    assert enriched[0]["categories"] == "OCPP > Server"


def test_a_case_only_rename_reuses_the_cached_classification(tmp_path):
    """GitHub names are case-insensitive, and ingest dedups them that way.

    A cache keyed case-sensitively paid for a fresh classification when an owner
    only recased its name (`EcoG-io` -> `ecog-io`), and kept the old entry
    forever as a stale duplicate.
    """
    def explode(row, readme):
        raise AssertionError("a recased repo is the same repo")
    entry = repo("ecog-io/iso15118", description="ISO 15118 stack")
    enriched, cache = run_enrich(
        tmp_path, [entry], explode,
        cache=[cached("EcoG-io/iso15118", "iso15118 > Misc",
                      signals=pipeline.classifier_signature(entry, ""))])
    assert enriched[0]["categories"] == "iso15118 > Misc"
    assert list(cache) == ["ecog-io/iso15118"]


def test_a_case_duplicate_left_by_an_earlier_run_is_dropped(tmp_path):
    """The run's own spelling wins: it is the entry the current name maps to."""
    entry = repo("ecog-io/iso15118", description="ISO 15118 stack")
    _, cache = run_enrich(
        tmp_path, [entry], lambda row, readme: None,
        cache=[cached("EcoG-io/iso15118", "iso15118 > Misc"),
               cached("ecog-io/iso15118", "iso15118 > Plug&Charge",
                      signals=pipeline.classifier_signature(entry, ""))])
    assert list(cache) == ["ecog-io/iso15118"]
    assert cache["ecog-io/iso15118"]["categories"] == "iso15118 > Plug&Charge"


# --- enrich: a README that could not be read is not an absent README -----------

class FakeResponse:
    def __init__(self, status_code, text=""):
        self.status_code = status_code
        self.text = text

    def raise_for_status(self):
        if self.status_code >= 400:
            raise pipeline.requests.HTTPError(f"{self.status_code} Error", response=self)


@pytest.mark.parametrize("status, expected", [
    (200, "# An OCPP server"),
    (404, ""),     # the repo ships no README: a fact about the repo
    (403, None),   # rate-limited: a fact about the run
    (502, None),
])
def test_fetch_readme_content_tells_absent_from_unreadable(tmp_path, monkeypatch, status, expected):
    monkeypatch.setattr(pipeline, "CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(pipeline.requests, "get",
                        lambda *a, **k: FakeResponse(status, "# An OCPP server"))
    assert real_fetch_readme_content("acme/charger", {}) == expected


def test_a_cached_readme_is_byte_identical_to_the_fetched_one(tmp_path, monkeypatch):
    """The signature hashes the README, so the disk cache must not rewrite it.

    Reading the cache back with universal newlines turned a CRLF README into an
    LF one: CI, which always starts from an empty cache, stamped the network
    form, and any run reading the cache paid to re-classify those repos.
    """
    monkeypatch.setattr(pipeline, "CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(pipeline.requests, "get",
                        lambda *a, **k: FakeResponse(200, "# Title\r\n\r\nOCPP 1.6\r\n"))
    fetched = real_fetch_readme_content("acme/charger", {})
    monkeypatch.setattr(pipeline.requests, "get",
                        lambda *a, **k: pytest.fail("the second read must hit the cache"))
    assert real_fetch_readme_content("acme/charger", {}) == fetched


def test_an_unreadable_readme_never_reaches_the_backend(tmp_path, monkeypatch):
    """Classifying without the README would pay for an answer to a different
    question — and cache an empty category for a repo whose README is its
    only signal."""
    def explode(row, readme):
        raise AssertionError("an unreadable README must not reach the backend")
    monkeypatch.setattr(pipeline, "fetch_readme_content", lambda *a, **k: None)
    previous = cached("acme/charger", "OCPP > Server", description="An OCPP server.",
                      signals="a-signature-with-the-readme")
    enriched, cache = run_enrich(tmp_path, [repo()], explode, cache=[previous],
                                 expect_exit=True)
    assert enriched[0]["categories"] == "OCPP > Server"
    assert cache["acme/charger"]["signals"] == "a-signature-with-the-readme", \
        "the entry is left untouched, so the next run retries"


def stub_readmes(monkeypatch, readmes):
    monkeypatch.setattr(pipeline, "fetch_readme_content",
                        lambda full_name, headers, html_url=None: readmes[full_name])


def test_one_unreadable_readme_fails_a_run_that_read_the_others(tmp_path, monkeypatch):
    """Protocol versions come from the README alone and are not cached.

    A run that carried on would publish the unreadable repo without its
    versions — a transient GitHub failure rendered as empty metadata.
    """
    stub_readmes(monkeypatch, {"acme/fine": "Supports OCPP 1.6", "acme/flaky": None})
    previous = cached("acme/flaky", "OCPP > Server", signals="a-signature-with-the-readme")
    enriched, cache = run_enrich(
        tmp_path,
        [repo("acme/fine", description="An OCPP server"),
         repo("acme/flaky", description="An OCPP server")],
        lambda row, readme: ("A server.", [("OCPP", "Server")]),
        cache=[previous], expect_exit=True)
    assert enriched[0]["ocpp_versions"] == "1.6"
    assert cache["acme/fine"]["categories"] == "OCPP > Server"
    assert cache["acme/flaky"]["signals"] == "a-signature-with-the-readme"


def test_a_repo_without_a_readme_does_not_fail_the_run(tmp_path, monkeypatch):
    """A 404 is a fact about the repo: empty versions are the truth there."""
    stub_readmes(monkeypatch, {"acme/fine": "Supports OCPP 1.6", "acme/bare": ""})
    enriched, _ = run_enrich(
        tmp_path,
        [repo("acme/fine", description="An OCPP server"),
         repo("acme/bare", description="An OCPP server")],
        lambda row, readme: ("A server.", [("OCPP", "Server")]))
    assert [r["ocpp_versions"] for r in enriched] == ["1.6", ""]


def test_an_unreadable_readme_on_an_unknown_repo_is_not_cached(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline, "fetch_readme_content", lambda *a, **k: None)
    enriched, cache = run_enrich(tmp_path, [repo(description="An OCPP server")],
                                 lambda row, readme: ("A server.", [("OCPP", "Server")]),
                                 expect_exit=True)
    assert enriched[0]["categories"] == ""
    assert "acme/charger" not in cache


# --- What invalidates a cached classification ---------------------------------

def test_an_edited_github_description_forces_a_reclassification(tmp_path):
    """`pushed_at` only moves on a commit, so it cannot catch a settings edit.

    The description is a classifier input — the only one, for a repo with no
    README — so a stale classification would otherwise survive indefinitely.
    """
    stale = cached("acme/charger", "OCPP > Server",
                   signals=pipeline.classifier_signature(
                       repo(description="An OCPP server"), ""))
    enriched, _ = run_enrich(
        tmp_path, [repo(description="An OCPI client")],
        lambda row, readme: ("An OCPI client.", [("OCPI", "Client")]),
        cache=[stale])
    assert enriched[0]["categories"] == "OCPI > Client"


def test_edited_topics_force_a_reclassification(tmp_path):
    stale = cached("acme/charger", "OCPP > Server",
                   signals=pipeline.classifier_signature(repo(topics="ocpp"), ""))
    enriched, _ = run_enrich(
        tmp_path, [repo(topics="ocpp|ocpi")],
        lambda row, readme: ("An OCPI client.", [("OCPI", "Client")]),
        cache=[stale])
    assert enriched[0]["categories"] == "OCPI > Client"


def test_an_edited_readme_forces_a_reclassification(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline, "fetch_readme_content", lambda *a, **k: "# Now an OCPI client")
    stale = cached("acme/charger", "OCPP > Server",
                   signals=pipeline.classifier_signature(repo(), "# An OCPP server"))
    enriched, _ = run_enrich(
        tmp_path, [repo()],
        lambda row, readme: ("An OCPI client.", [("OCPI", "Client")]),
        cache=[stale])
    assert enriched[0]["categories"] == "OCPI > Client"


def test_an_entry_predating_the_signals_column_is_still_reused(tmp_path):
    """Re-classifying the whole listing at once would blow the workflow timeout."""
    def explode(row, readme):
        raise AssertionError("a legacy cache entry must not reach the backend")
    enriched, cache = run_enrich(tmp_path, [repo(description="An OCPP server")], explode,
                                 cache=[cached("acme/charger", "OCPP > Server")])
    assert enriched[0]["categories"] == "OCPP > Server"
    assert cache["acme/charger"]["signals"], "a reused entry is stamped for the next run"


@pytest.mark.parametrize("signals", ["", "matching"])
def test_an_empty_category_is_not_reused_when_there_is_something_to_classify(tmp_path, signals):
    """An empty answer is only ever the answer when there is nothing to read.

    Earlier runs cached empty categories for repos that did have a description
    or topics (the missing-README bail-out, an unparseable reply). The
    pre-`signals` reuse rule kept them, the first stamping run fingerprinted
    them, and from then on they were frozen until the repo changed.
    """
    entry = repo(description="A lightweight OCPP 1.6J central system", topics="ocpp")
    stamp = pipeline.classifier_signature(entry, "") if signals else ""
    enriched, cache = run_enrich(
        tmp_path, [entry], lambda row, readme: ("An OCPP server.", [("OCPP", "Server")]),
        cache=[cached("acme/charger", "", signals=stamp)])
    assert enriched[0]["categories"] == "OCPP > Server"
    assert cache["acme/charger"]["categories"] == "OCPP > Server"


def test_an_empty_category_with_nothing_to_classify_is_still_reused(tmp_path):
    def explode(row, readme):
        raise AssertionError("re-asking a repo with nothing to read is pointless")
    entry = repo()
    enriched, _ = run_enrich(
        tmp_path, [entry], explode,
        cache=[cached("acme/charger", "", signals=pipeline.classifier_signature(entry, ""))])
    assert enriched[0]["categories"] == ""


def test_a_commit_that_changes_no_classifier_input_reuses_the_cache(tmp_path):
    """A push is not a reason to re-ask: the signature covers every model input.

    Most commits touch code, not the README — and `pushed_at` moves on all of
    them. Keying reuse on it too spent an LLM call per active repo per run for
    an answer that could not have changed.
    """
    def explode(row, readme):
        raise AssertionError("an unchanged prompt must not reach the backend")
    entry = repo(description="An OCPP server", topics="ocpp")
    enriched, _ = run_enrich(
        tmp_path, [entry], explode,
        cache=[cached("acme/charger", "OCPP > Server", pushed_at="2020-01-01T00:00:00Z",
                      signals=pipeline.classifier_signature(entry, ""))])
    assert enriched[0]["categories"] == "OCPP > Server"


def test_a_reused_entry_records_the_current_pushed_at(tmp_path):
    """The column stays a truthful record of the repo, even though reuse no
    longer keys on it."""
    entry = repo(description="An OCPP server")
    _, cache = run_enrich(
        tmp_path, [entry], lambda row, readme: None,
        cache=[cached("acme/charger", "OCPP > Server", pushed_at="2020-01-01T00:00:00Z",
                      signals=pipeline.classifier_signature(entry, ""))])
    assert cache["acme/charger"]["pushed_at"] == "2026-01-01T00:00:00Z"


def test_a_taxonomy_change_invalidates_every_classification():
    """The taxonomy is in the prompt, so it is part of what the model was asked.

    Keying reuse on the repo's own text alone froze every cached category
    against a taxonomy that had since moved — and nothing re-asked, because a
    push no longer invalidates either.
    """
    before = pipeline.classifier_signature(repo(description="An OCPP server"), "")
    pipeline.CATEGORY_TREE_TEXT += "\n- Roaming: Hubs"
    try:
        after = pipeline.classifier_signature(repo(description="An OCPP server"), "")
    finally:
        pipeline.CATEGORY_TREE_TEXT = pipeline.CATEGORY_TREE_TEXT.rsplit("\n", 1)[0]
    assert before != after


def test_a_contract_change_invalidates_every_classification(monkeypatch):
    """The role and output contract is duplicated across four places on purpose
    (see AGENTS.md); hashing the in-repo copy tracks it for every backend."""
    before = pipeline.classifier_signature(repo(description="An OCPP server"), "")
    monkeypatch.setattr(pipeline, "CLASSIFIER_INSTRUCTIONS",
                        pipeline.CLASSIFIER_INSTRUCTIONS + "\nAlso name the licence.")
    assert pipeline.classifier_signature(repo(description="An OCPP server"), "") != before


def test_the_chosen_model_does_not_invalidate_the_cache(monkeypatch):
    """Deliberate: the model is who answers, not what was asked.

    Local runs default to the `claude` backend and CI uses `copilot`; keying on
    the backend would make the two thrash each other's cache, and a model swap
    would force a paid re-classification of the whole listing. `--refresh` is
    the way to ask for that on purpose.
    """
    before = pipeline.classifier_signature(repo(description="An OCPP server"), "")
    monkeypatch.setattr(pipeline, "CLASSIFIER_COPILOT_MODEL", "some-other-model")
    assert pipeline.classifier_signature(repo(description="An OCPP server"), "") == before


# --- enrich --restamp: keeping answers a prompt edit cannot have changed ------

def never_asked(row, readme):
    raise AssertionError("a restamped entry must not reach the backend")


def ocpp_server(row, readme):
    return ("A fresh answer.", [("OCPP", "Server")])


def test_restamp_adopts_a_stale_answer_without_asking(tmp_path):
    """An edit to the taxonomy or the contract changes every signature at once.

    Re-asking ~680 repos costs hours of paid calls for answers most of which
    cannot have moved; `--restamp` keeps them and stamps them as current.
    """
    entry = repo(description="An OCPP server")
    enriched, cache = run_enrich(
        tmp_path, [entry], never_asked, restamp=True,
        cache=[cached("acme/charger", "OCPP > Server", description="An OCPP server.",
                      signals="a-stale-signature")])
    assert enriched[0]["categories"] == "OCPP > Server"
    assert enriched[0]["description"] == "An OCPP server."
    assert cache["acme/charger"]["categories"] == "OCPP > Server"
    assert cache["acme/charger"]["description"] == "An OCPP server."
    assert cache["acme/charger"]["signals"] == pipeline.classifier_signature(entry, "")


def test_restamp_is_counted_apart_from_reuse(tmp_path, capsys):
    run_enrich(tmp_path, [repo(description="An OCPP server")], never_asked, restamp=True,
               cache=[cached("acme/charger", "OCPP > Server", signals="a-stale-signature")])
    assert "restamped: 1" in capsys.readouterr().out


def test_without_restamp_a_stale_answer_is_still_asked_again(tmp_path):
    enriched, _ = run_enrich(
        tmp_path, [repo(description="An OCPP server")], ocpp_server,
        cache=[cached("acme/charger", "OCPP > Misc", signals="a-stale-signature")])
    assert enriched[0]["categories"] == "OCPP > Server"


def test_restamp_re_asks_a_stale_answer_in_a_split_bucket(tmp_path):
    """The edit split `OCPP > Misc`: the old answer is the one that may move."""
    enriched, cache = run_enrich(
        tmp_path, [repo(description="An OCPP server")], ocpp_server, restamp=True,
        reask_category=["OCPP > Misc"],
        cache=[cached("acme/charger", "Other > Tools| OCPP > Misc ",
                      signals="a-stale-signature")])
    assert enriched[0]["categories"] == "OCPP > Server"
    assert cache["acme/charger"]["categories"] == "OCPP > Server"


def test_restamp_keeps_a_stale_answer_outside_the_split_buckets(tmp_path):
    enriched, _ = run_enrich(
        tmp_path, [repo(description="An OCPP server")], never_asked, restamp=True,
        reask_category=["OCPP > Misc"],
        cache=[cached("acme/charger", "OCPP > Miscellaneous", signals="a-stale-signature")])
    assert enriched[0]["categories"] == "OCPP > Miscellaneous"


def test_restamp_does_not_re_ask_a_repo_pinned_by_an_override(tmp_path, monkeypatch):
    """A pinned repo renders from CATEGORY_OVERRIDES whatever the model says."""
    monkeypatch.setattr(pipeline, "CATEGORY_OVERRIDES", {"acme/charger": "OCPP > Server"})
    enriched, cache = run_enrich(
        tmp_path, [repo("Acme/Charger", description="An OCPP server")], never_asked,
        restamp=True, reask_category=["OCPP > Misc"],
        cache=[cached("Acme/Charger", "OCPP > Misc", signals="a-stale-signature")])
    assert enriched[0]["categories"] == "OCPP > Misc"
    assert cache["Acme/Charger"]["signals"] != "a-stale-signature"


def test_restamp_reuses_a_current_answer_even_in_a_split_bucket(tmp_path):
    """A matching signature was asked under the current prompt already."""
    entry = repo(description="An OCPP server")
    enriched, _ = run_enrich(
        tmp_path, [entry], never_asked, restamp=True, reask_category=["OCPP > Misc"],
        cache=[cached("acme/charger", "OCPP > Misc",
                      signals=pipeline.classifier_signature(entry, ""))])
    assert enriched[0]["categories"] == "OCPP > Misc"


def test_restamp_classifies_a_repo_missing_from_the_cache(tmp_path):
    enriched, cache = run_enrich(
        tmp_path, [repo(description="An OCPP server")], ocpp_server, restamp=True)
    assert enriched[0]["categories"] == "OCPP > Server"
    assert cache["acme/charger"]["categories"] == "OCPP > Server"


def test_restamp_re_asks_a_stale_empty_answer_with_something_to_read(tmp_path):
    """An empty category there is a leftover failure, not an answer to keep."""
    enriched, _ = run_enrich(
        tmp_path, [repo(description="An OCPP server")], ocpp_server, restamp=True,
        cache=[cached("acme/charger", "", signals="a-stale-signature")])
    assert enriched[0]["categories"] == "OCPP > Server"


def test_restamp_leaves_an_unreadable_readme_entry_untouched(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline, "fetch_readme_content", lambda *a, **k: None)
    _, cache = run_enrich(
        tmp_path, [repo(description="An OCPP server")], never_asked, restamp=True,
        cache=[cached("acme/charger", "OCPP > Server", signals="a-stale-signature")],
        expect_exit=True)
    assert cache["acme/charger"]["signals"] == "a-stale-signature"


@pytest.mark.parametrize("argv", [
    ["--reask-category", "OCPP > Misc"],
    ["--restamp", "--refresh"],
])
def test_restamp_flag_combinations_are_rejected(monkeypatch, capsys, argv):
    def never(args):
        raise AssertionError("a rejected command line must not run enrich")
    monkeypatch.setattr(pipeline, "enrich", never)
    monkeypatch.setattr(pipeline.sys, "argv", ["pipeline.py", "enrich", *argv])
    with pytest.raises(SystemExit) as exit_info:
        pipeline.main()
    assert exit_info.value.code == 2
    err = capsys.readouterr().err
    # Rejected as a combination, not as an option argparse does not know.
    assert "unrecognized" not in err
    assert all(flag in err for flag in argv if flag.startswith("--"))


def test_restamp_accepts_repeated_reask_categories(monkeypatch):
    seen = []
    monkeypatch.setattr(pipeline, "enrich", seen.append)
    monkeypatch.setattr(pipeline.sys, "argv", [
        "pipeline.py", "enrich", "--restamp",
        "--reask-category", "OCPP > Misc", "--reask-category", "ISO 15118 > Misc"])
    pipeline.main()
    assert seen[0].restamp is True
    assert seen[0].reask_category == ["OCPP > Misc", "ISO 15118 > Misc"]


# --- enrich: a dead backend must not pass for a refresh -----------------------

def test_a_total_classifier_outage_fails_the_run(tmp_path):
    """Stale categories are kept so the listing cannot blank — but the run must
    not then report success and open a PR claiming a refresh happened.

    A retired model id or an unauthenticated CLI fails every repo identically,
    and every one of them keeps its cached category, so the regression guard
    downstream sees nothing wrong.
    """
    run_enrich(tmp_path, [repo(description="An OCPP server")],
               lambda row, readme: None, expect_exit=True)


def test_a_partial_classifier_outage_does_not_fail_the_run(tmp_path):
    """One flaky repo is not an outage; its cache entry is left for a retry."""
    def flaky(row, readme):
        return None if row["full_name"] == "acme/flaky" else ("A server.", [("OCPP", "Server")])
    enriched, _ = run_enrich(
        tmp_path,
        [repo("acme/flaky", description="An OCPP server"),
         repo("acme/fine", description="An OCPP server")],
        flaky)
    assert [r["categories"] for r in enriched] == ["", "OCPP > Server"]


def test_a_run_that_classified_nothing_at_all_does_not_fail(tmp_path):
    """The steady state now that reuse keys on the prompt: no attempts, no
    verdict to draw about the backend."""
    def explode(row, readme):
        raise AssertionError("a cache hit must not reach the backend")
    entry = repo(description="An OCPP server")
    enriched, _ = run_enrich(
        tmp_path, [entry], explode,
        cache=[cached("acme/charger", "OCPP > Server",
                      signals=pipeline.classifier_signature(entry, ""))])
    assert enriched[0]["categories"] == "OCPP > Server"


def test_readme_text_the_model_never_sees_does_not_invalidate(tmp_path):
    padding = "x" * pipeline.README_PROMPT_CHARS
    assert (pipeline.classifier_signature(repo(), padding + "trailing")
            == pipeline.classifier_signature(repo(), padding + "different"))


# --- Protocol versions read from the README -----------------------------------

@pytest.mark.parametrize("text, expected", [
    ("Supports OCPP 1.6", "1.6"),
    ("OCPP 1.6-J and OCPP 2.0.1 over WebSocket", "1.6,2.0.1"),
    # A list after one keyword used to stop at its first item.
    ("OCPP 1.2 and 1.5 are supported", "1.2,1.5"),
    ("speaks OCPP 2.0.1 / 2.1 (WebSocket) and OCPP 1.2 / 1.5 / 1.6S (SOAP)",
     "1.2,1.5,1.6,2.0.1,2.1"),
    ("supports OCPP 1.6J, 2.0.1, and 2.1.", "1.6,2.0.1,2.1"),
    ("OCPP 1.6 or 2.0.1", "1.6,2.0.1"),
    ("OCPP 1.6 + 2.0.1 support", "1.6,2.0.1"),
    # Not versions: a wildcard, a power rating, an unknown number.
    ("OCPP 1.6 and 2.x", "1.6"),
    ("OCPP 1.6 and 22 kW chargers", "1.6"),
    ("OCPP 1.6 and 3.11", "1.6"),
    ("written in Python 3.11 with OCPP", ""),
])
def test_extract_ocpp_versions(text, expected):
    assert pipeline.extract_versions(text, "ocpp", pipeline.OCPP_VERSIONS) == expected


def test_extract_ocpi_versions_from_a_list():
    assert pipeline.extract_versions(
        "Implements OCPI 2.1.1 / 2.2.1 and 2.3.0", "ocpi", pipeline.OCPI_VERSIONS
    ) == "2.1.1,2.2.1,2.3.0"


# --- Codeberg: repositories hosted outside GitHub -------------------------------

# Trimmed from the real response of GET /api/v1/repos/slash909uk/ocpp-domoticz-bridge.
FORGEJO_REPO = {
    "full_name": "slash909uk/ocpp-domoticz-bridge",
    "html_url": "https://codeberg.org/slash909uk/ocpp-domoticz-bridge",
    "description": "A bridge to allow domoticz to control an EVSE via OCPP.",
    "language": "Python",
    "stars_count": 1,
    "forks_count": 0,
    "open_issues_count": 0,
    "topics": [],
    "updated_at": "2026-09-09T01:09:14+02:00",
    "created_at": "2026-09-09T00:40:32+02:00",
    "default_branch": "main",
    "empty": False,
    "archived": False,
    "fork": False,
    "parent": None,
    "mirror": False,
}

REPO_URL = "/repos/slash909uk/ocpp-domoticz-bridge"
BRANCH_URL = REPO_URL + "/branches/main"


def forgejo_branch(timestamp):
    """GET /api/v1/repos/{repo}/branches/{branch}, trimmed to what is read."""
    return {"name": "main", "commit": {"id": "c0ffee", "timestamp": timestamp}}


def _iso_days_ago(days):
    return (datetime.now(timezone.utc)
            - timedelta(days=days)).isoformat(timespec="seconds")


class FakeJsonResponse(FakeResponse):
    def __init__(self, status_code, body):
        super().__init__(status_code, pipeline.json.dumps(body))


def stub_codeberg(monkeypatch, tmp_path, routes):
    """Serve `routes` (URL suffix -> response) and record every request's headers."""
    monkeypatch.setattr(pipeline, "CACHE_DIR", str(tmp_path))
    sent = []

    def get(url, headers=None, **kwargs):
        sent.append((url, dict(headers or {})))
        for suffix, response in routes.items():
            if url.endswith(suffix):
                return response
        return FakeResponse(404)
    monkeypatch.setattr(pipeline.requests, "get", get)
    return sent


def test_a_forgejo_repo_is_mapped_onto_the_github_shape():
    obj = pipeline.forgejo_repo_as_github(FORGEJO_REPO)
    assert obj["stargazers_count"] == 1
    assert obj["html_url"] == "https://codeberg.org/slash909uk/ocpp-domoticz-bridge"
    # days_since_push only reads UTC `Z` timestamps: an offset left as is would
    # make every Codeberg repo look active forever.
    assert obj["updated_at"] == "2026-09-08T23:09:14Z"
    assert obj["created_at"] == "2026-09-08T22:40:32Z"


def test_a_forgejo_repo_update_is_not_taken_for_a_push():
    """`updated_at` also moves on a description or topic edit: it is the last
    known modification, not the last commit."""
    assert not pipeline.forgejo_repo_as_github(FORGEJO_REPO).get("pushed_at")


def test_a_codeberg_repo_is_dated_by_its_last_commit(tmp_path, monkeypatch):
    stub_codeberg(monkeypatch, tmp_path, {
        REPO_URL: FakeJsonResponse(200, dict(FORGEJO_REPO, updated_at="2026-11-06T13:59:02+01:00")),
        BRANCH_URL: FakeJsonResponse(200, forgejo_branch("2026-11-06T13:31:20+01:00"))})
    record = pipeline.codeberg_record("slash909uk/ocpp-domoticz-bridge")
    assert record["pushed_at"] == "2026-11-06T12:31:20Z"
    assert record["updated_at"] == "2026-11-06T12:59:02Z"


def test_a_metadata_edit_leaves_a_stale_codeberg_repo_dormant(tmp_path, monkeypatch):
    stub_codeberg(monkeypatch, tmp_path, {
        REPO_URL: FakeJsonResponse(200, dict(FORGEJO_REPO, updated_at=_iso_days_ago(1))),
        BRANCH_URL: FakeJsonResponse(200, forgejo_branch("2020-01-01T12:00:00+01:00"))})
    record = pipeline.codeberg_record("slash909uk/ocpp-domoticz-bridge")
    assert record["pushed_at"] == "2020-01-01T11:00:00Z"
    assert record["dormant"] == "true"


def test_a_recent_commit_keeps_a_codeberg_repo_active(tmp_path, monkeypatch):
    stub_codeberg(monkeypatch, tmp_path, {
        REPO_URL: FakeJsonResponse(200, FORGEJO_REPO),
        BRANCH_URL: FakeJsonResponse(200, forgejo_branch(_iso_days_ago(3)))})
    record = pipeline.codeberg_record("slash909uk/ocpp-domoticz-bridge")
    assert record["days_since_push"] in (2, 3)
    assert record["dormant"] == "false"


@pytest.mark.parametrize("repo_obj, routes", [
    # The default branch answers 404: there is no commit to date.
    (FORGEJO_REPO, {}),
    # Forgejo flags a repository without any commit as empty: nothing to read.
    (dict(FORGEJO_REPO, empty=True), {}),
])
def test_a_codeberg_repo_without_commits_has_no_push_date(tmp_path, monkeypatch, repo_obj, routes):
    sent = stub_codeberg(monkeypatch, tmp_path, dict(routes, **{
        REPO_URL: FakeJsonResponse(200, repo_obj)}))
    record = pipeline.codeberg_record("slash909uk/ocpp-domoticz-bridge")
    assert record["pushed_at"] == ""
    assert record["days_since_push"] == ""
    # An unknown push date does not make a repo dormant: only archiving does.
    assert record["dormant"] == "false"
    assert record["updated_at"] == "2026-09-08T23:09:14Z"
    if repo_obj.get("empty"):
        assert not any(url.endswith(BRANCH_URL) for url, _ in sent)


@pytest.mark.parametrize("branch_response", [FakeResponse(503), FakeResponse(429)])
def test_an_unreadable_codeberg_branch_fails_the_run(tmp_path, monkeypatch, branch_response):
    """Writing the row without its push date would publish a dormancy verdict
    nothing supports; abort like an unreadable repo does."""
    stub_codeberg(monkeypatch, tmp_path, {
        REPO_URL: FakeJsonResponse(200, FORGEJO_REPO), BRANCH_URL: branch_response})
    with pytest.raises(SystemExit, match="slash909uk/ocpp-domoticz-bridge"):
        pipeline.codeberg_record("slash909uk/ocpp-domoticz-bridge")


def test_a_codeberg_record_is_built_without_the_github_token(tmp_path, monkeypatch):
    sent = stub_codeberg(monkeypatch, tmp_path, {
        REPO_URL: FakeJsonResponse(200, FORGEJO_REPO),
        BRANCH_URL: FakeJsonResponse(200, forgejo_branch("2026-09-09T01:00:00+02:00"))})
    record = pipeline.codeberg_record("slash909uk/ocpp-domoticz-bridge")
    assert record["full_name"] == "slash909uk/ocpp-domoticz-bridge"
    assert record["source"] == "codeberg"
    assert record["stars"] == 1
    assert record["dormant"] in ("true", "false")
    # Nobody starred it: the column records a fact, not the curation.
    assert record["starred_by"] == ""
    assert [url for url, _ in sent] == [
        "https://codeberg.org/api/v1" + REPO_URL, "https://codeberg.org/api/v1" + BRANCH_URL]
    # Not even an Accept header: Codeberg gets nothing the GitHub calls carry.
    assert all(headers == {} for _, headers in sent)


def test_a_github_record_carries_its_last_update():
    record = pipeline.build_repo_record(
        {"full_name": "acme/charger", "pushed_at": "2026-01-01T00:00:00Z",
         "updated_at": "2026-02-01T00:00:00Z"}, "topic", set(), set(), set())
    assert record["pushed_at"] == "2026-01-01T00:00:00Z"
    assert record["updated_at"] == "2026-02-01T00:00:00Z"
    assert "updated_at" in pipeline.CSV_FIELDS
    assert set(record) == set(pipeline.CSV_FIELDS)


def test_a_record_without_a_push_date_is_not_dormant_unless_archived():
    assert pipeline.days_since_push("") is None
    assert pipeline.days_since_push(None) is None
    active = pipeline.build_repo_record({"full_name": "a/b"}, "topic", set(), set(), set())
    assert (active["pushed_at"], active["days_since_push"], active["dormant"]) == ("", "", "false")
    archived = pipeline.build_repo_record(
        {"full_name": "a/b", "archived": True}, "topic", set(), set(), set())
    assert archived["dormant"] == "true"


def test_a_deleted_codeberg_repo_is_skipped_with_a_warning(tmp_path, monkeypatch, capsys):
    stub_codeberg(monkeypatch, tmp_path, {})  # every URL answers 404
    assert pipeline.codeberg_record("gone/away") is None
    assert "::warning::gone/away" in capsys.readouterr().out


def _connection_refused(*args, **kwargs):
    raise pipeline.requests.ConnectionError("connection refused")


@pytest.mark.parametrize("get", [
    lambda *a, **k: FakeResponse(503),   # Codeberg is down
    lambda *a, **k: FakeResponse(429),   # rate-limited
    _connection_refused,                 # network error
])
def test_an_unreadable_codeberg_repo_fails_the_run(tmp_path, monkeypatch, get):
    """Skipping it would drop the repo from repos.csv, then from the README at
    the next render: its GitHub mirror is excluded, and no guard counts rows."""
    monkeypatch.setattr(pipeline, "CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(pipeline.requests, "get", get)
    with pytest.raises(SystemExit, match="acme/bridge"):
        pipeline.codeberg_record("acme/bridge")


def test_ingest_keeps_the_previous_csv_when_a_codeberg_repo_is_unreadable(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline, "CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(pipeline, "STARRED_USERS", set())
    monkeypatch.setattr(pipeline, "CODEBERG_REPOS", {"acme/bridge"})
    monkeypatch.setattr(pipeline, "get_contributors", lambda repo, headers: set())
    monkeypatch.setattr(pipeline, "collect_candidates", lambda headers: {})
    monkeypatch.setattr(pipeline.requests, "get", lambda *a, **k: FakeResponse(503))
    out = tmp_path / "repos.csv"
    out.write_text("previous run\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        pipeline.ingest(pipeline.argparse.Namespace(token=None, out=str(out)))
    assert out.read_text(encoding="utf-8") == "previous run\n"


def test_a_codeberg_repo_is_promoted_to_the_selection():
    """A GitHub Stars list cannot hold a Codeberg repo, so listing it in
    CODEBERG_REPOS is the curation itself."""
    assert pipeline._promotion(repo(source="codeberg")) == 1
    assert pipeline._promotion(repo(source="manual")) == -1
    assert pipeline._promotion(repo(source="codeberg", starred_by="juherr|mateogreil")) == 2


@pytest.mark.parametrize("routes, expected", [
    ({"/contents": FakeJsonResponse(200, [{"name": "LICENSE", "type": "file"},
                                          {"name": "README.md", "type": "file"}]),
      "/raw/README.md": FakeResponse(200, "# An OCPP bridge")}, "# An OCPP bridge"),
    # No README file at the root: a fact about the repo.
    ({"/contents": FakeJsonResponse(200, [{"name": "server.py", "type": "file"},
                                          {"name": "readme", "type": "dir"}])}, ""),
    # The listing could not be read: a fact about the run.
    ({"/contents": FakeResponse(502)}, None),
    ({"/contents": FakeJsonResponse(200, [{"name": "Readme.rst", "type": "file"}]),
      "/raw/Readme.rst": FakeResponse(503)}, None),
    # The listing names a README the raw endpoint no longer serves: the cached
    # listing is stale, which says nothing about whether the repo has a README.
    ({"/contents": FakeJsonResponse(200, [{"name": "README.md", "type": "file"}]),
      "/raw/README.md": FakeResponse(404)}, None),
])
def test_a_codeberg_readme_is_read_from_codeberg(tmp_path, monkeypatch, routes, expected):
    sent = stub_codeberg(monkeypatch, tmp_path, routes)
    readme = real_fetch_readme_content(
        "slash909uk/ocpp-domoticz-bridge", {"Authorization": "token ghp_secret"},
        html_url="https://codeberg.org/slash909uk/ocpp-domoticz-bridge")
    assert readme == expected
    assert all("Authorization" not in headers for _, headers in sent)
    assert all(url.startswith("https://codeberg.org/api/v1/") for url, _ in sent)


def test_a_github_readme_is_still_read_from_github(tmp_path, monkeypatch):
    sent = stub_codeberg(monkeypatch, tmp_path, {"/readme": FakeResponse(200, "# GitHub")})
    assert real_fetch_readme_content(
        "acme/charger", {}, html_url="https://github.com/acme/charger") == "# GitHub"
    assert sent[0][0] == f"{pipeline.BASE_URL}/repos/acme/charger/readme"


def test_enrich_reads_the_readme_from_the_repo_host(tmp_path, monkeypatch):
    seen = []
    monkeypatch.setattr(pipeline, "fetch_readme_content",
                        lambda full_name, headers, html_url=None: seen.append(html_url) or "")
    url = "https://codeberg.org/slash909uk/ocpp-domoticz-bridge"
    run_enrich(tmp_path, [repo("slash909uk/ocpp-domoticz-bridge", html_url=url)],
               lambda row, readme: ("", []))
    assert seen == [url]


def test_a_codeberg_repo_wins_over_its_github_mirror(monkeypatch):
    """A project that moved to Codeberg often leaves an archived GitHub mirror
    under the same owner/repo, which also keys the classification cache. The
    Codeberg entry is the live one; the mirror must not reach the listing."""
    monkeypatch.setattr(pipeline, "CODEBERG_REPOS", {"tandemdrive/ocpi-tariffs"})
    monkeypatch.setattr(pipeline, "search_topic_repo_names",
                        lambda topic, headers: ["TandemDrive/ocpi-tariffs", "acme/charger"])
    monkeypatch.setattr(pipeline, "ADDITIONAL_REPOS", set())
    monkeypatch.setattr(pipeline, "readme_repo_names", lambda: [])
    monkeypatch.setattr(pipeline, "get_starred_list_repos", lambda user, slug, headers: [])
    candidates = pipeline.collect_candidates({})
    assert set(candidates) == {"acme/charger"}
