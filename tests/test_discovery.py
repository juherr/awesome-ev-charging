"""Tests for external-list discovery: configuration, source fetching, extraction.

No test reaches the network: `requests.get` is stubbed and the HTTP cache
points at a temporary directory, so `cache_github/` is never written.
"""

import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys

import pytest

import discovery
import pipeline


class Calls(list):
    """The (url, headers) pairs requests.get saw, plus its canned answers."""
    answers: dict


class FakeResponse:
    def __init__(self, status_code, text=""):
        self.status_code = status_code
        self.text = text

    def raise_for_status(self):
        if self.status_code >= 400:
            raise pipeline.requests.HTTPError(f"{self.status_code} Error", response=self)


@pytest.fixture
def http(tmp_path, monkeypatch):
    """Stub requests.get; return the list of (url, headers) calls it saw."""
    monkeypatch.setattr(pipeline, "CACHE_DIR", str(tmp_path))
    calls, answers = Calls(), {}

    def get(url, headers=None, **kwargs):
        calls.append((url, headers or {}))
        return answers.get(url, FakeResponse(404))

    monkeypatch.setattr(pipeline.requests, "get", get)
    calls.answers = answers
    return calls


# --- Configuration ------------------------------------------------------------

def write_config(tmp_path, body):
    path = tmp_path / "discovery-sources.toml"
    path.write_text(body, encoding="utf-8")
    return str(path)


def test_load_sources_reads_repo_and_url_sources_in_file_order(tmp_path):
    path = write_config(tmp_path, """
[[sources]]
name = "fork"
repo = "andreibesleaga/awesome-ev-charging"

[[sources]]
name = "list"
url = "https://example.org/list.md"
""")
    assert discovery.load_sources(path) == [
        discovery.Source("fork", repo="andreibesleaga/awesome-ev-charging"),
        discovery.Source("list", url="https://example.org/list.md"),
    ]


@pytest.mark.parametrize("body", [
    "sources = [",                                            # not TOML
    "",                                                       # no source
    '[[sources]]\nrepo = "a/b"',                              # no name
    '[[sources]]\nname = "x"',                                # neither repo nor url
    '[[sources]]\nname = "x"\nrepo = "a/b"\nurl = "https://e.org"',  # both
    '[[sources]]\nname = "x"\nrepo = "not-a-repo"',
    '[[sources]]\nname = "x"\nurl = "ftp://e.org/list.md"',
    '[[sources]]\nname = "x"\nrepo = "a/b"\nbranch = "main"',  # unknown key
    '[[sources]]\nname = "x"\nrepo = "a/b"\n[[sources]]\nname = "x"\nrepo = "c/d"',
    '[[sources]]\nname = "a | b"\nrepo = "a/b"',             # breaks the source table
    '[[sources]]\nname = "a`b"\nrepo = "a/b"',               # breaks a code span
])
def test_load_sources_rejects_an_invalid_config(tmp_path, body):
    with pytest.raises(discovery.ConfigError):
        discovery.load_sources(write_config(tmp_path, body))


def test_load_sources_rejects_a_missing_file(tmp_path):
    with pytest.raises(discovery.ConfigError):
        discovery.load_sources(str(tmp_path / "absent.toml"))


def test_committed_sources_monitor_the_andrei_besleaga_fork():
    path = pathlib.Path(__file__).parent.parent / "discovery-sources.toml"
    sources = discovery.load_sources(str(path))
    assert "andreibesleaga/awesome-ev-charging" in {s.repo for s in sources}


# --- Fetching -----------------------------------------------------------------

REPO = discovery.Source("fork", repo="acme/list")
URL = discovery.Source("list", url="https://example.org/list.md")


@pytest.mark.parametrize("source, status, expected", [
    (REPO, 200, ("# List", None)),
    (REPO, 404, (None, "not found")),     # deleted source: never "0 links"
    (REPO, 403, (None, "fetch failed")),  # rate limit
    (URL, 200, ("# List", None)),
    (URL, 404, (None, "not found")),
    (URL, 502, (None, "fetch failed")),
])
def test_fetch_source_tells_a_deleted_source_from_a_failed_fetch(http, source, status, expected):
    for url in ("https://api.github.com/repos/acme/list/readme", URL.url):
        http.answers[url] = FakeResponse(status, "# List")
    assert discovery.fetch_source(source, {"Authorization": "token T"}) == expected


def test_only_github_api_requests_carry_the_token(http):
    http.answers[URL.url] = FakeResponse(200, "# List")
    discovery.fetch_source(URL, {"Authorization": "token T"})
    discovery.fetch_source(REPO, {"Authorization": "token T"})
    assert [("Authorization" in h) for _, h in http] == [False, True]


@pytest.mark.parametrize("error", [pipeline.requests.Timeout, pipeline.requests.ConnectionError])
def test_a_url_source_that_does_not_answer_is_a_failed_fetch(monkeypatch, error):
    def get(url, **kwargs):
        raise error("no answer")
    monkeypatch.setattr(pipeline.requests, "get", get)
    assert discovery.fetch_source(URL, {"Authorization": "token T"}) == (None, "fetch failed")


@pytest.mark.parametrize("status, text, expected", [
    (200, "", (None, "not found")),
    (429, "", (None, "fetch failed")),
])
def test_a_url_source_maps_empty_bodies_and_rate_limits(http, status, text, expected):
    http.answers[URL.url] = FakeResponse(status, text)
    assert discovery.fetch_source(URL, {"Authorization": "token T"}) == expected


def test_a_url_source_is_fetched_with_a_timeout_and_no_auth(monkeypatch):
    seen = []

    def get(url, **kwargs):
        seen.append(kwargs)
        return FakeResponse(200, "# List")
    monkeypatch.setattr(pipeline.requests, "get", get)
    assert discovery.fetch_source(URL, {"Authorization": "token T"}) == ("# List", None)
    [kwargs] = seen
    assert kwargs.get("timeout") == discovery.URL_TIMEOUT
    assert "Authorization" not in (kwargs.get("headers") or {})


def test_fetch_sources_keeps_going_past_a_failed_source(http):
    http.answers[URL.url] = FakeResponse(200, "# List")
    texts, failures = discovery.fetch_sources([REPO, URL], {})
    assert texts == {"list": "# List"}
    assert failures == {"fork": "not found"}


# --- URL normalization --------------------------------------------------------

@pytest.mark.parametrize("raw, expected", [
    ("HTTPS://Example.ORG/Docs/", "https://example.org/Docs"),
    ("https://example.org/", "https://example.org"),
    ("https://www.example.org/a#section", "https://www.example.org/a"),
    ("https://example.org/a?utm_source=x&b=2&a=1&fbclid=y", "https://example.org/a?a=1&b=2"),
    ("https://example.org/a?ref=awesome&gclid=1&mc_cid=2&mc_eid=3&ref_src=4",
     "https://example.org/a"),
    ("https://example.org/a).", "https://example.org/a"),
    ("https://example.org/a;", "https://example.org/a"),
])
def test_normalize_url(raw, expected):
    assert discovery.normalize_url(raw) == expected


# --- Extraction and dedupe ----------------------------------------------------

FORK = """\
# Awesome

[![CI](https://img.shields.io/badge/ci-green.svg)](https://github.com/andreibesleaga/awesome-ev-charging)
- [ocmf-js](https://github.com/road-labs/ocmf-js/tree/main) - OCMF in JS.
- [Tariffs](https://github.com/TandemDrive/ocpi-tariffs) and [docs](https://tandemdrive.com/ocpi?utm_source=gh).
- ![logo](https://example.org/logo.png) [EVRoaming](https://evroaming.org/#top)
- <img src="https://user-images.githubusercontent.com/1/2.png"> [raw](https://raw.githubusercontent.com/a/b/main/x.md)
"""

OTHER = """\
* [OCMF JS](https://github.com/Road-Labs/OCMF-JS) again.
* [EVRoaming](https://evroaming.org) site.
"""


def test_extract_links_reads_repos_and_external_urls_with_their_line():
    repos, urls = discovery.extract_links(FORK)
    assert repos == {
        "andreibesleaga/awesome-ev-charging":
            "[![CI](https://img.shields.io/badge/ci-green.svg)]"
            "(https://github.com/andreibesleaga/awesome-ev-charging)",
        "road-labs/ocmf-js": "- [ocmf-js](https://github.com/road-labs/ocmf-js/tree/main) - OCMF in JS.",
        "TandemDrive/ocpi-tariffs":
            "- [Tariffs](https://github.com/TandemDrive/ocpi-tariffs) and "
            "[docs](https://tandemdrive.com/ocpi?utm_source=gh).",
    }
    # Images, badges and GitHub asset hosts are not candidates.
    assert sorted(urls) == ["https://evroaming.org", "https://tandemdrive.com/ocpi"]
    assert urls["https://evroaming.org"].startswith("- ![logo]")


def test_extract_links_skips_images_attachments_and_gists():
    text = """\
- ![shot](https://github.com/acme/screens/raw/main/a.png) [Tool](https://github.com/acme/tool)
- <img src="https://github.com/acme/logos/blob/main/l.png" width="20">
- See https://github.com/user-attachments/assets/0b1c-2d3e for a demo.
- [Gist](https://gist.github.com/someone/0123abcd) and gist.github.com/other/4567ef.
"""
    repos, urls = discovery.extract_links(text)
    assert list(repos) == ["acme/tool"]
    assert urls == {}


def test_collect_candidates_dedupes_across_sources_with_provenance():
    repos, urls = discovery.collect_candidates({"other": OTHER, "fork": FORK})
    assert [c.key for c in repos] == [
        "andreibesleaga/awesome-ev-charging", "road-labs/ocmf-js", "tandemdrive/ocpi-tariffs"]
    ocmf = repos[1]
    assert ocmf.name == "road-labs/ocmf-js"  # first source in sorted name order
    assert ocmf.sources == ["fork", "other"]
    assert ocmf.context["other"] == "* [OCMF JS](https://github.com/Road-Labs/OCMF-JS) again."
    assert [(c.name, c.sources) for c in urls] == [
        ("https://evroaming.org", ["fork", "other"]),
        ("https://tandemdrive.com/ocpi", ["fork"]),
    ]


def test_collect_candidates_is_deterministic():
    texts = {"other": OTHER, "fork": FORK}
    assert discovery.collect_candidates(texts) == discovery.collect_candidates(dict(reversed(texts.items())))


# --- Tracked sets, resolution and statuses ------------------------------------
# Modelled on the andreibesleaga fork: names and classifications as read in
# classifications.csv at the base commit, deprecated rows included.

def row(description="A library."):
    return {"description": description}


CLASSIFIED = {
    "road-labs/ocmf-js": row(),
    "matth-x/MicroOcpp": row(),
    "argonne-vci/node-red-contrib-ocpp": row(),
    "andreibesleaga/ocm-sdk": row("A deprecated TypeScript SDK."),
    "other/ocpp-proxy": row(),
}
CATALOGUE_README = """\
- [Dead](https://github.com/dead/tracked) gone since.
- [EVRoaming](https://evroaming.org/) and [ref][r].

[r]: https://Docs.Example.org/spec#intro
"""
LIST = """\
# Fork
- [ocmf-js](https://github.com/road-labs/ocmf-js)
- [Tariffs](https://github.com/TandemDrive/ocpi-tariffs)
- [ArduinoOcpp](https://github.com/matth-x/arduinoocpp)
- [Node-RED](https://github.com/argonne-national-laboratory/node-red-contrib-ocpp)
- [OpenADR 3](https://github.com/oadr3-org/openadr3-openapi)
- [ocm-sdk](https://github.com/andreibesleaga/ocm-sdk)
- [Zephyr](https://github.com/zephyrproject-rtos/zephyr)
- [Upstream](https://github.com/juherr/awesome-ev-charging)
- [Dead](https://github.com/dead/tracked)
- [Flaky](https://github.com/flaky/tracked) and [flaky too](https://github.com/flaky/untracked)
- [OCPP proxy](https://github.com/acme/ocpp-proxy) - routes `OCPP` frames.
- [EVRoaming](https://evroaming.org) and [new doc](https://new.example.org/doc/?utm_medium=x)
"""
OTHER_LIST = """\
* [Node-RED VCI](https://github.com/argonne-vci/node-red-contrib-ocpp)
* [ts-rpc](https://github.com/rohittiwari-dev/ocpp-ts-rpc)
* [Fork](https://github.com/andreibesleaga/awesome-ev-charging)
"""
SOURCES = [discovery.Source("fork", repo="andreibesleaga/awesome-ev-charging"),
           discovery.Source("other", url="https://example.org/list.md")]
NEW_REPO = {"full_name": "acme/ocpp-proxy", "html_url": "https://github.com/acme/ocpp-proxy",
            "description": "An OCPP <proxy>.", "archived": False,
            "pushed_at": "2026-05-01T10:00:00Z", "license": None}
# What GET /repos/{name} answers; absent names 404, None fails transiently.
LOOKUPS = {
    "road-labs/ocmf-js": {"full_name": "road-labs/ocmf-js"},
    "tandemdrive/ocpi-tariffs": {"full_name": "tandemdrive/ocpi-tariffs"},
    "matth-x/arduinoocpp": {"full_name": "matth-x/MicroOcpp"},
    "argonne-national-laboratory/node-red-contrib-ocpp":
        {"full_name": "argonne-vci/node-red-contrib-ocpp"},
    "argonne-vci/node-red-contrib-ocpp": {"full_name": "argonne-vci/node-red-contrib-ocpp"},
    "andreibesleaga/ocm-sdk": {"full_name": "andreibesleaga/ocm-sdk"},
    "zephyrproject-rtos/zephyr": {"full_name": "zephyrproject-rtos/zephyr"},
    "juherr/awesome-ev-charging": {"full_name": "juherr/awesome-ev-charging"},
    "andreibesleaga/awesome-ev-charging": {"full_name": "andreibesleaga/awesome-ev-charging"},
    "flaky/tracked": None,
    "flaky/untracked": None,
    "acme/ocpp-proxy": NEW_REPO,
}


def tracked():
    return discovery.build_tracked(CLASSIFIED, [CATALOGUE_README],
                                   additional={"flaky/tracked"},
                                   codeberg={"tandemdrive/ocpi-tariffs"})


def lookups_for(candidates):
    return {c.key: LOOKUPS.get(c.key, discovery.NOT_FOUND) for c in candidates}


@pytest.fixture(scope="module")
def results():
    repos, urls = discovery.collect_candidates({"fork": LIST, "other": OTHER_LIST})
    found = discovery.classify(repos, urls, lookups_for(repos), tracked(),
                               source_repos={"andreibesleaga/awesome-ev-charging"})
    return {r.name: r for r in found}


def test_build_tracked_gathers_every_catalogue_dataset():
    t = tracked()
    assert {"road-labs/ocmf-js", "matth-x/microocpp", "dead/tracked", "flaky/tracked",
            "tandemdrive/ocpi-tariffs"} <= t.repos
    assert {"https://evroaming.org", "https://docs.example.org/spec",
            "https://codeberg.org/tandemdrive/ocpi-tariffs"} <= t.urls


@pytest.mark.parametrize("missing", [pipeline.CLASSIFICATIONS_PATH, *discovery.CATALOGUE_FILES])
def test_load_tracked_names_a_missing_catalogue_file(tmp_path, missing):
    repo = pathlib.Path(discovery.__file__).parent
    header = (repo / pipeline.CLASSIFICATIONS_PATH).read_text(encoding="utf-8").splitlines()[0]
    (tmp_path / pipeline.CLASSIFICATIONS_PATH).write_text(header + "\n", encoding="utf-8")
    for name in discovery.CATALOGUE_FILES:
        (tmp_path / name).write_text("# Catalogue\n", encoding="utf-8")
    (tmp_path / missing).unlink()
    with pytest.raises(discovery.ConfigError) as error:
        discovery.load_tracked(tmp_path)
    assert str(tmp_path / missing) in str(error.value)


@pytest.mark.parametrize("name, status, reason", [
    ("road-labs/ocmf-js", "existing", ""),
    ("tandemdrive/ocpi-tariffs", "existing", ""),
    ("matth-x/MicroOcpp", "changed", "source"),
    ("argonne-vci/node-red-contrib-ocpp", "changed", "source"),
    ("oadr3-org/openadr3-openapi", "unavailable", "not found"),
    ("rohittiwari-dev/ocpp-ts-rpc", "unavailable", "not found"),
    ("dead/tracked", "unavailable", "not found (tracked)"),
    ("flaky/untracked", "unavailable", "lookup failed"),
    ("flaky/tracked", "existing", ""),
    ("andreibesleaga/ocm-sdk", "excluded", "deprecated"),
    ("zephyrproject-rtos/zephyr", "excluded", "EXCLUDED_REPOS"),
    ("juherr/awesome-ev-charging", "excluded", "EXCLUDED_REPOS"),
    ("andreibesleaga/awesome-ev-charging", "excluded", "discovery source"),
    ("acme/ocpp-proxy", "new", ""),
    ("https://evroaming.org", "existing", ""),
    ("https://new.example.org/doc", "new", ""),
])
def test_classify_status(results, name, status, reason):
    result = results[name]
    assert (result.status, result.reason or result.stale) == (status, reason)


def test_aliases_resolving_to_one_repo_merge_into_one_candidate(results):
    merged = results["argonne-vci/node-red-contrib-ocpp"]
    assert merged.aliases == ["argonne-national-laboratory/node-red-contrib-ocpp",
                              "argonne-vci/node-red-contrib-ocpp"]
    assert merged.sources == ["fork", "other"]
    assert merged.old == ["argonne-national-laboratory/node-red-contrib-ocpp"]
    assert "argonne-national-laboratory/node-red-contrib-ocpp" not in results


def _classify_one(link, lookups):
    """The single result for a source linking `link`, with old/name classified."""
    repos, urls = discovery.collect_candidates({"fork": link})
    t = discovery.build_tracked({"old/name": row()}, [])
    [result] = discovery.classify(repos, urls, lookups, t)
    return result


def test_a_stale_catalogue_name_is_changed_on_the_catalogue_side():
    result = _classify_one("https://github.com/old/name", {"old/name": {"full_name": "new/Name"}})
    assert (result.status, result.stale, result.old, result.name) == (
        "changed", "catalogue", ["old/name"], "new/Name")


def test_a_stale_catalogue_name_the_source_does_not_link_is_still_changed():
    lookups = {"new/name": {"full_name": "new/Name"}, "old/name": {"full_name": "new/Name"}}
    result = _classify_one("https://github.com/new/Name", lookups)
    assert (result.status, result.stale, result.old, result.name, result.related) == (
        "changed", "catalogue", ["old/name"], "new/Name", [])


@pytest.mark.parametrize("answer", [None, discovery.NOT_FOUND, {"full_name": "old/name"}])
def test_a_related_name_that_does_not_resolve_to_the_candidate_leaves_it_new(answer):
    lookups = {"new/name": {"full_name": "new/Name"}, "old/name": answer}
    result = _classify_one("https://github.com/new/Name", lookups)
    assert (result.status, result.related) == ("new", ["old/name"])


def test_run_looks_up_the_related_names_of_a_new_candidate(http):
    http.answers["https://example.org/list.md"] = FakeResponse(200, "https://github.com/new/Name")
    for name in ("new/Name", "old/name"):
        http.answers[f"https://api.github.com/repos/{name}"] = FakeResponse(
            200, json.dumps({"full_name": "new/Name"}))
    t = discovery.build_tracked({"old/name": row()}, [])
    report, _ = discovery.run([discovery.Source("other", url="https://example.org/list.md")], t, {})
    assert "- old/name -> new/Name, stale in the catalogue (sources: other)" in report


def test_run_excludes_a_renamed_source_under_its_current_name(http):
    http.answers["https://api.github.com/repos/old/list/readme"] = FakeResponse(
        200, "https://github.com/new/List")
    for name in ("old/list", "new/List"):
        http.answers[f"https://api.github.com/repos/{name}"] = FakeResponse(
            200, json.dumps({"full_name": "new/List"}))
    report, _ = discovery.run([discovery.Source("fork", repo="old/list")],
                              discovery.build_tracked({}, []), {})
    assert "- new/List: discovery source (sources: fork)" in report


def test_run_keeps_the_configured_source_name_when_its_lookup_fails(http):
    http.answers["https://api.github.com/repos/old/list/readme"] = FakeResponse(
        200, "https://github.com/old/list")
    http.answers["https://api.github.com/repos/old/list"] = FakeResponse(500)
    report, _ = discovery.run([discovery.Source("fork", repo="old/list")],
                              discovery.build_tracked({}, []), {})
    assert "- old/list: discovery source (sources: fork)" in report


def test_a_new_candidate_carries_metadata_context_and_related_projects(results):
    new = results["acme/ocpp-proxy"]
    assert new.data == NEW_REPO
    assert new.related == ["other/ocpp-proxy"]
    assert new.context == {
        "fork": "- [OCPP proxy](https://github.com/acme/ocpp-proxy) - routes `OCPP` frames."}


# --- Report -------------------------------------------------------------------

def fork_answers():
    """The README, the other list and every repo lookup of the fixture, by URL."""
    answers = {
        "https://api.github.com/repos/andreibesleaga/awesome-ev-charging/readme":
            FakeResponse(200, LIST),
        "https://example.org/list.md": FakeResponse(200, OTHER_LIST),
    }
    repos, _ = discovery.collect_candidates({"fork": LIST, "other": OTHER_LIST})
    for c in repos:  # the stub is case-sensitive, GitHub is not: answer as linked
        data = LOOKUPS.get(c.key, discovery.NOT_FOUND)
        if data is discovery.NOT_FOUND:
            continue
        answers[f"https://api.github.com/repos/{c.name}"] = (
            FakeResponse(500) if data is None else FakeResponse(200, json.dumps(data)))
    return answers


@pytest.fixture
def fork_http(http):
    """Answer the README, the other list and every repo lookup of the fixture."""
    http.answers.update(fork_answers())
    return http


def test_report_lists_each_status_with_its_fields(fork_http):
    report, read = discovery.run(SOURCES, tracked(), {})
    assert read
    for line in [
        "# Discovery report", "## Summary", "| new | 1 | 1 |", "| existing | 3 | 1 |",
        "| fork | 2 | 2 | 3 | 3 | 4 |", "| other | 0 | 1 | 1 | 1 | 0 |",
        "## Failed sources\n\nNone.",
        "#### [acme/ocpp-proxy](https://github.com/acme/ocpp-proxy)",
        "- Description: An OCPP &lt;proxy>.", "- Archived: no",
        "- Last push: 2026-05-01T10:00:00Z", "- Licence:\n", "- Related tracked projects: other/ocpp-proxy",
        "- Context (fork): ``[OCPP proxy](https://github.com/acme/ocpp-proxy) - routes `OCPP` frames.``",
        "- <https://new.example.org/doc> (sources: fork)",
        "- matth-x/arduinoocpp -> matth-x/MicroOcpp, stale in the source (sources: fork)",
        "- dead/tracked: not found (tracked) (sources: fork)",
        "- andreibesleaga/ocm-sdk: deprecated (sources: fork)",
        "Already tracked: 3 GitHub repositories, 1 other URLs.",
    ]:
        assert line in report
    headings = [l for l in report.splitlines() if l.startswith("## ")]
    assert headings == ["## Summary", "## Failed sources", "## New", "## Changed",
                        "## Unavailable", "## Excluded", "## Existing"]


def test_report_is_byte_identical_across_runs(fork_http):
    assert discovery.run(SOURCES, tracked(), {}) == discovery.run(SOURCES, tracked(), {})


# Renders the fixture report in a fresh interpreter, HTTP stubbed; run with
# the scratch directory as cwd so the HTTP cache never lands in the repo.
RENDER_IN_SUBPROCESS = """\
import sys
sys.path[:0] = [sys.argv[1], sys.argv[1] + "/tests"]
import discovery, pipeline, test_discovery as t
pipeline.CACHE_DIR = "."
answers = t.fork_answers()
pipeline.requests.get = lambda url, headers=None, **kw: answers.get(url, t.FakeResponse(404))
open("report.md", "w", encoding="utf-8", newline="").write(discovery.run(t.SOURCES, t.tracked(), {})[0])
"""


def test_report_does_not_depend_on_the_hash_seed(tmp_path):
    root = str(pathlib.Path(__file__).parent.parent)
    reports = []
    for seed in ("1", "7"):  # these two seeds order {"fork", "other"} differently
        cwd = tmp_path / seed
        cwd.mkdir()
        subprocess.run([sys.executable, "-c", RENDER_IN_SUBPROCESS, root], cwd=cwd,
                              env={**os.environ, "PYTHONHASHSEED": seed},
                              capture_output=True, check=True)
        reports.append((cwd / "report.md").read_bytes())
    assert reports[0].startswith(b"# Discovery report")
    assert reports[0] == reports[1]


def test_failed_and_deleted_sources_are_reported_and_the_others_processed(http):
    http.answers["https://example.org/list.md"] = FakeResponse(200, OTHER_LIST)
    http.answers["https://api.github.com/repos/gone/list/readme"] = FakeResponse(500)
    sources = [*SOURCES, discovery.Source("flaky", repo="gone/list")]
    report, read = discovery.run(sources, tracked(), {})
    assert read
    assert "- `flaky`: fetch failed\n- `fork`: not found" in report
    assert "rohittiwari-dev/ocpp-ts-rpc: not found (sources: other)" in report


# --- CLI ----------------------------------------------------------------------

TRACKED_FILES = ("classifications.csv", "README.md", "legacy-projects.md", "csms.md")


def snapshot(root):
    return {p.relative_to(root): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


@pytest.fixture
def repo_copy(fork_http, tmp_path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    for name in TRACKED_FILES:
        shutil.copy(pathlib.Path(__file__).parent.parent / name, root / name)
    (root / "discovery-sources.toml").write_text(
        '[[sources]]\nname = "fork"\nrepo = "andreibesleaga/awesome-ev-charging"\n'
        '[[sources]]\nname = "other"\nurl = "https://example.org/list.md"\n', encoding="utf-8")
    monkeypatch.chdir(root)
    return root


def test_cli_writes_nothing_but_the_report(repo_copy):
    before = snapshot(repo_copy)
    code = discovery.main(["--sources", "discovery-sources.toml", "--report", "out/report.md",
                           "--token", "T"])
    after = snapshot(repo_copy)
    assert code == 0
    assert set(after) - set(before) == {pathlib.Path("out/report.md")}
    assert {k: after[k] for k in before} == before
    report = (repo_copy / "out/report.md").read_text(encoding="utf-8")
    assert "road-labs/ocmf-js" not in report.split("## Existing")[0]  # tracked, never new


@pytest.mark.parametrize("config, expected", [
    ('[[sources]]\nname = "gone"\nrepo = "gone/list"\n', 1),  # every source failed
    ("[[sources]]\n", 2),                                     # config error
])
def test_cli_exit_codes(repo_copy, config, expected):
    (repo_copy / "bad.toml").write_text(config, encoding="utf-8")
    code = discovery.main(["--sources", "bad.toml", "--report", "report.md"])
    assert code == expected
    assert (repo_copy / "report.md").exists() == (expected == 1)


def test_cli_writes_the_issue_body_next_to_the_report(repo_copy):
    before = snapshot(repo_copy)
    code = discovery.main(["--sources", "discovery-sources.toml", "--report", "out/report.md",
                           "--issue-body", "out/issue.md", "--workflow-url", WORKFLOW_URL])
    after = snapshot(repo_copy)
    assert code == 0
    assert set(after) - set(before) == {pathlib.Path("out/report.md"), pathlib.Path("out/issue.md")}
    report = (repo_copy / "out/report.md").read_text(encoding="utf-8")
    assert (repo_copy / "out/issue.md").read_text(encoding="utf-8") == \
        discovery.issue_body(report, WORKFLOW_URL)


@pytest.mark.parametrize("flags", [["--issue-body", "issue.md"], ["--workflow-url", "https://x"]])
def test_cli_needs_both_issue_flags(repo_copy, flags):
    with pytest.raises(SystemExit) as e:
        discovery.main(["--sources", "discovery-sources.toml", "--report", "report.md", *flags])
    assert e.value.code == 2
    assert not (repo_copy / "report.md").exists()
    assert not (repo_copy / "issue.md").exists()


# --- Issue body ---------------------------------------------------------------

WORKFLOW_URL = "https://github.com/juherr/awesome-ev-charging/actions/workflows/discovery.yml"


def synthetic_report(**sizes):
    """A report shaped like `render_report`, with `sizes[section]` filler lines."""
    def section(title):
        n = sizes.get(title.lower(), 1)
        return [f"## {title}", "", *(f"- {title.lower()} item {i}" for i in range(n)), ""]
    out = ["# Discovery report", "", "Intro.", "", "## Summary", "",
           "| Status | GitHub repos | Other URLs |", "| --- | --- | --- |", "| new | 1 | 0 |", ""]
    for title in ("Failed sources", "New", "Changed", "Unavailable", "Excluded", "Existing"):
        out += section(title)
    return "\n".join(out).rstrip("\n") + "\n"


def test_issue_body_is_the_marker_the_workflow_link_and_the_report(fork_http):
    report, _ = discovery.run(SOURCES, tracked(), {})
    body = discovery.issue_body(report, WORKFLOW_URL)
    first, second, blank, rest = body.split("\n", 3)
    assert first == "<!-- discovery-report -->"
    assert f"[weekly discovery workflow]({WORKFLOW_URL})" in second
    assert "`discovery-report` artifact" in second
    assert blank == ""
    assert rest == report  # under the limit: the whole report, untouched
    assert "Truncated" not in body


def test_issue_body_is_deterministic():
    report = synthetic_report(existing=5000)
    assert discovery.issue_body(report, WORKFLOW_URL, limit=2000) == \
        discovery.issue_body(report, WORKFLOW_URL, limit=2000)


@pytest.mark.parametrize("limit", [65536, 600])  # whole and truncated
def test_issue_body_depends_only_on_the_report_and_the_workflow_url(limit):
    """Nothing run-specific: an unchanged report leaves the issue body unchanged."""
    report = synthetic_report(new=100)
    body = discovery.issue_body(report, WORKFLOW_URL, limit=limit)
    other = "x" * len(WORKFLOW_URL)  # same length: the same lines fit
    assert body.replace(WORKFLOW_URL, other) == discovery.issue_body(report, other, limit=limit)
    assert body.count(WORKFLOW_URL) == (1 if limit == 65536 else 2)
    assert "/actions/runs/" not in body


def test_text_neutralises_mentions_and_issue_references():
    zw = "​"
    out = discovery._text("@octocat fixes #1 and a/b#2, mail me@x.org")
    assert out == f"@{zw}octocat fixes #{zw}1 and a/b#{zw}2, mail me@{zw}x.org"
    for sign_then_alnum in ("@o", "#1", "#2", "@x"):
        assert sign_then_alnum not in out


@pytest.mark.parametrize("value", ["An OCPP proxy.", "C# and @ alone, # 1", "Ünïcode ok"])
def test_text_leaves_values_without_a_mention_or_reference_unchanged(value):
    assert discovery._text(value) == value


def test_report_neutralises_mentions_in_new_repo_metadata():
    lines = discovery._new_repo(discovery.Result(
        "new", "repo", "acme/x", ["fork"], {}, data={"description": "by @octocat, see #12"}))
    assert "- Description: by @​octocat, see #​12" in lines


def test_issue_body_over_the_limit_keeps_the_counts_and_actionable_sections():
    report = synthetic_report(new=3, changed=2, unavailable=2, excluded=500, existing=500)
    limit = 1000
    assert len(discovery.issue_body(report, WORKFLOW_URL, limit=len(report) * 2)) > limit
    body = discovery.issue_body(report, WORKFLOW_URL, limit=limit)
    assert len(body) <= limit
    assert body.startswith("<!-- discovery-report -->\n")
    assert "| new | 1 | 0 |" in body
    headings = [l for l in body.splitlines() if l.startswith("## ")]
    assert headings == ["## Summary", "## New", "## Changed", "## Unavailable"]
    for title in ("new", "changed", "unavailable"):
        assert all(f"- {title} item {i}" in body for i in range(2))
    assert "- new item 2" in body
    last = body.rstrip("\n").splitlines()[-1]
    assert "Truncated" in last and WORKFLOW_URL in last and "`discovery-report` artifact" in last
    assert body.endswith("\n")


def test_issue_body_keeps_whole_sections_while_they_fit():
    report = synthetic_report(new=2, changed=2, unavailable=400)
    body = discovery.issue_body(report, WORKFLOW_URL, limit=1500)
    assert len(body) <= 1500
    assert "- changed item 1" in body  # the sections before it stay whole
    assert "- unavailable item 0" in body
    assert "- unavailable item 399" not in body
    assert "## Excluded" not in body and "## Existing" not in body


def test_issue_body_never_exceeds_the_limit_even_for_one_huge_section():
    report = synthetic_report(new=20000)
    for limit in (600, 65536):
        body = discovery.issue_body(report, WORKFLOW_URL, limit=limit)
        assert len(body) <= limit
        lines = body.splitlines()
        assert "## Changed" not in lines
        kept = [l for l in lines if l.startswith("- new item ")]
        assert kept and kept == [f"- new item {i}" for i in range(len(kept))]  # whole lines, in order
        assert "Truncated" in lines[-1]
    assert len(discovery.issue_body(report, WORKFLOW_URL)) <= 65536
