"""Tests for external-list discovery: configuration, source fetching, extraction.

No test reaches the network: `requests.get` is stubbed and the HTTP cache
points at a temporary directory, so `cache_github/` is never written.
"""

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
])
def test_load_sources_rejects_an_invalid_config(tmp_path, body):
    with pytest.raises(discovery.ConfigError):
        discovery.load_sources(write_config(tmp_path, body))


def test_load_sources_rejects_a_missing_file(tmp_path):
    with pytest.raises(discovery.ConfigError):
        discovery.load_sources(str(tmp_path / "absent.toml"))


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
