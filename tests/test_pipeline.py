"""Tests for the discovery pipeline's classification layer.

Nothing here reaches the network or spawns a classifier CLI: `enrich` runs
against a stubbed backend and a stubbed README fetch, and the backends
themselves are exercised through a stubbed `subprocess.run`.
"""

import csv
import types

import pytest

import pipeline


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


def run_enrich(tmp_path, rows, classify, cache=(), **overrides):
    """Run `enrich` with a stubbed backend; return (enriched rows, written cache)."""
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
    )
    args.__dict__.update(overrides)

    pipeline.CLASSIFIERS["stub"] = classify
    try:
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
                                 cache=[previous])
    assert cache["acme/charger"]["pushed_at"] == "2025-01-01T00:00:00Z"
    assert cache["acme/charger"]["categories"] == "OCPP > Server"


def test_a_hard_failure_keeps_the_stale_category_in_the_listing(tmp_path):
    """A classifier outage must not blank the rendered listing."""
    previous = cached("acme/charger", "OCPP > Server", pushed_at="2025-01-01T00:00:00Z",
                      description="An OCPP server.", signals="a-stale-signature")
    enriched, _ = run_enrich(tmp_path, [repo()], lambda row, readme: None,
                             cache=[previous])
    assert enriched[0]["categories"] == "OCPP > Server"
    assert enriched[0]["description"] == "An OCPP server."


def test_a_hard_failure_on_an_unknown_repo_yields_no_category(tmp_path):
    enriched, cache = run_enrich(tmp_path, [repo()], lambda row, readme: None)
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


def test_readme_text_the_model_never_sees_does_not_invalidate(tmp_path):
    padding = "x" * pipeline.README_PROMPT_CHARS
    assert (pipeline.classifier_signature(repo(), padding + "trailing")
            == pipeline.classifier_signature(repo(), padding + "different"))
