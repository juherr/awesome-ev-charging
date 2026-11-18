"""Every internal link in the repository's own Markdown resolves to a tracked path.

An internal link is a relative link (`docs/x.md`, `../csms.md`, an image) or an
absolute link into this repository on github.com
(`https://github.com/juherr/awesome-ev-charging/tree/main/<path>`). Both are
resolved against the set `git ls-files` returns, not against the disk: macOS
resolves a path case-insensitively and CI runs on Linux, and an untracked local
file is not something a reader of the repository can open.

Links are read from Markdown inline links and images, reference definitions,
`href` / `src` attributes of inline HTML tags, and `<scheme:...>` autolinks.
Fenced code blocks, inline code spans and HTML comments are skipped.
"""

import functools
import posixpath
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# Verbatim upstream Markdown from the Open Charge Alliance. Their bytes are
# never edited, so a broken link in them is not ours to fix. Keep this list in
# step with the exact-path exemptions in .markdownlint-cli2.jsonc.
VENDORED_VERBATIM_MARKDOWN = frozenset(
    {
        "ocpp/OCPP-2.0/ReadMe.md",
        "ocpp/OCPP-2.0.1/ReadMe.md",
        "ocpp/OCPP-2.1/ReadMe.md",
    }
)

# What link_path returns for a relative link that climbs above the root.
ESCAPES_ROOT = "<escapes the repository root>"

REPO_URL = re.compile(
    r"^https://github\.com/juherr/awesome-ev-charging/(?:tree|blob)/main(?:/(.*))?$"
)
URL_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
CODE_SPAN = re.compile(r"(`+)(?!`).*?(?<!`)\1(?!`)")
# `](target)` or `](target "title")`, the target optionally in angle brackets
# and allowed one level of balanced parentheses.
INLINE_LINK = re.compile(
    r"\]\(\s*(?:<([^>\n]*)>|([^\s()<>]+(?:\([^\s()]*\)[^\s()<>]*)*))"
    r"(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)"
)
# `[label]: target` — but not a footnote definition `[^1]: text`.
REFERENCE_DEFINITION = re.compile(r"^ {0,3}\[(?!\^)[^\]]+\]:\s*(?:<([^>]*)>|(\S+))")
# An inline HTML tag on one line, and its `href` / `src` attribute values.
HTML_TAG = re.compile(r"<[A-Za-z][A-Za-z0-9-]*(?:\s[^<>]*)?>")
HTML_LINK_ATTRIBUTE = re.compile(
    r"\s(?:href|src)\s*=\s*(?:\"([^\"]*)\"|'([^']*)')", re.IGNORECASE
)
# A CommonMark URI autolink `<scheme:...>`; `](<target>)` is a link
# destination, already matched by INLINE_LINK.
AUTOLINK = re.compile(r"(?<!\()<([A-Za-z][A-Za-z0-9+.-]{1,31}:[^\s<>]*)>")
COMMENT_OPEN = "<!--"
COMMENT_CLOSE = "-->"


def _blank(text):
    return " " * len(text)


def _strip_comments(line, in_comment):
    """Blank out HTML comments; return the line and whether one is still open."""
    result = []
    position = 0
    while position < len(line):
        if in_comment:
            end = line.find(COMMENT_CLOSE, position)
            if end < 0:
                result.append(_blank(line[position:]))
                return "".join(result), True
            end += len(COMMENT_CLOSE)
            result.append(_blank(line[position:end]))
            position = end
            in_comment = False
        else:
            start = line.find(COMMENT_OPEN, position)
            if start < 0:
                result.append(line[position:])
                break
            result.append(line[position:start])
            position = start
            in_comment = True
    return "".join(result), in_comment


def _line_links(line):
    """`(column, target)` for every link on a line with code and comments blanked."""
    found = []
    definition = REFERENCE_DEFINITION.match(line)
    if definition:
        found.append((definition.start(), definition.group(1) or definition.group(2)))
    for match in INLINE_LINK.finditer(line):
        target = match.group(1) if match.group(1) is not None else match.group(2)
        found.append((match.start(), target))
    for tag in HTML_TAG.finditer(line):
        for attribute in HTML_LINK_ATTRIBUTE.finditer(tag.group(0)):
            target = attribute.group(1)
            if target is None:
                target = attribute.group(2)
            found.append((tag.start() + attribute.start(), target))
    for match in AUTOLINK.finditer(line):
        found.append((match.start(), match.group(1)))
    return sorted(found, key=lambda item: item[0])


def extract_links(text):
    """Return `(line number, target)` for every link outside code and comments."""
    links = []
    fence = None
    in_comment = False
    for number, line in enumerate(text.splitlines(), start=1):
        opening = FENCE.match(line)
        if fence is not None:
            closing = opening and opening.group(1)
            if (
                closing
                and closing[0] == fence[0]
                and len(closing) >= len(fence)
                and not line[opening.end() :].strip()
            ):
                fence = None
            continue
        if opening and not in_comment:
            fence = opening.group(1)
            continue
        line = CODE_SPAN.sub(lambda m: _blank(m.group(0)), line)
        line, in_comment = _strip_comments(line, in_comment)
        links.extend((number, target) for _, target in _line_links(line))
    return links


def link_path(source, target):
    """Repository path a link from `source` points at, or None if not internal.

    Returns ESCAPES_ROOT for a relative link that climbs above the root.
    """
    target = target.strip()
    from_root = False
    repo_url = REPO_URL.match(target)
    if repo_url:
        target = repo_url.group(1) or ""
        from_root = True
    elif target.startswith("#") or target.startswith("//") or URL_SCHEME.match(target):
        return None
    path = target.split("#", 1)[0].split("?", 1)[0]
    path = unquote(path)
    if path.startswith("/"):
        path = path.lstrip("/")
        from_root = True
    base = "" if from_root else posixpath.dirname(source)
    resolved = posixpath.normpath(posixpath.join(base, path))
    if resolved == ".." or resolved.startswith("../"):
        return ESCAPES_ROOT
    return "" if resolved == "." else resolved


def is_tracked(path, tracked):
    """Whether `path` is a tracked file, or a directory holding one.

    The comparison is case-sensitive, as on the Linux CI runner.
    """
    if path == ESCAPES_ROOT:
        return False
    if path == "" or path in tracked:
        return True
    prefix = path + "/"
    return any(candidate.startswith(prefix) for candidate in tracked)


def broken_links(source, text, tracked):
    """`file:line -> target` for every internal link that does not resolve."""
    broken = []
    for number, target in extract_links(text):
        path = link_path(source, target)
        if path is not None and not is_tracked(path, tracked):
            broken.append(f"{source}:{number} -> {target}")
    return broken


def _git_ls_files(*pathspec):
    output = subprocess.run(
        ["git", "ls-files", "-z", "--", *pathspec],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    ).stdout.decode("utf-8")
    return [name for name in output.split("\0") if name]


@functools.cache
def tracked_paths():
    """Every tracked path, Markdown or not: a link may point at a PDF."""
    return frozenset(_git_ls_files())


def first_party_markdown():
    return sorted(
        name
        for name in _git_ls_files("*.md")
        if name not in VENDORED_VERBATIM_MARKDOWN
    )


# --- Unit tests: link extraction --------------------------------------------


def test_extracts_inline_image_and_reference_links():
    text = (
        "See [the docs](docs/a.md) and ![logo](img/logo.png).\n"
        "[ref]: emi3/README.md\n"
        '[titled](csms.md "The catalogue")\n'
        "[angle](<docs/with space.md>)\n"
    )
    assert extract_links(text) == [
        (1, "docs/a.md"),
        (1, "img/logo.png"),
        (2, "emi3/README.md"),
        (3, "csms.md"),
        (4, "docs/with space.md"),
    ]


def test_skips_links_inside_fenced_code_blocks():
    text = (
        "[before](a.md)\n"
        "```markdown\n"
        "[inside](missing.md)\n"
        "~~~\n"
        "[still inside](missing.md)\n"
        "```\n"
        "~~~\n"
        "[tilde inside](missing.md)\n"
        "~~~\n"
        "[after](b.md)\n"
    )
    assert extract_links(text) == [(1, "a.md"), (10, "b.md")]


def test_skips_links_inside_inline_code_spans():
    text = "Use `[x](missing.md)` or ``[y](missing.md)`` but [z](real.md).\n"
    assert extract_links(text) == [(1, "real.md")]


def test_extracts_href_and_src_from_inline_html():
    text = (
        '<a href="docs/a.md">A</a> and <img alt="logo" src=\'img/logo.png\'>\n'
        '<p align="center"><a class="x" HREF="csms.md"><b>c</b></a></p>\n'
    )
    assert extract_links(text) == [
        (1, "docs/a.md"),
        (1, "img/logo.png"),
        (2, "csms.md"),
    ]


def test_extracts_angle_bracket_autolinks():
    base = "https://github.com/juherr/awesome-ev-charging"
    text = (
        f"See <{base}/blob/main/csms.md> and [x](docs/a.md).\n"
        "Mail <someone@example.org>, not a link: <docs/not-a-link.md>.\n"
    )
    assert extract_links(text) == [
        (1, f"{base}/blob/main/csms.md"),
        (1, "docs/a.md"),
    ]


def test_an_angle_bracket_link_destination_is_not_an_autolink_too():
    text = "[x](<https://example.org/a b>)\n"
    assert extract_links(text) == [(1, "https://example.org/a b")]


def test_skips_html_and_autolinks_inside_code():
    text = (
        '`<a href="missing.md">` and `<https://github.com/x>`\n'
        "```html\n"
        '<img src="missing.png">\n'
        "```\n"
    )
    assert extract_links(text) == []


def test_skips_links_inside_html_comments():
    text = (
        "<!-- [one](missing.md) --> [kept](a.md) <!-- <a href=\"x.md\"> -->\n"
        "<!--\n"
        "[two](missing.md)\n"
        '<img src="missing.png">\n'
        "-->[after](b.md)\n"
        "`<!--` is code, so [c](c.md) still counts\n"
    )
    assert extract_links(text) == [(1, "a.md"), (5, "b.md"), (6, "c.md")]


def test_broken_html_and_autolink_targets_are_reported():
    base = "https://github.com/juherr/awesome-ev-charging"
    text = (
        '<img src="nope.png">\n'
        f"<{base}/tree/main/missing-dir>\n"
        f"<{base}/blob/main/csms.md>\n"
    )
    assert broken_links("README.md", text, TRACKED) == [
        "README.md:1 -> nope.png",
        f"README.md:2 -> {base}/tree/main/missing-dir",
    ]


# --- Unit tests: target resolution ------------------------------------------

TRACKED = frozenset(
    {
        "README.md",
        "csms.md",
        "docs/content-taxonomy-audit.md",
        "docs/with space.md",
        "ocpp/OCPP-1.6/schemas/README.md",
        "ocpp/OCPP-1.6/schemas/Authorize.json",
    }
)


def test_skips_anchor_only_mailto_and_external_urls():
    for target in (
        "#scope",
        "mailto:someone@example.org",
        "https://example.org/docs/missing.md",
        "http://example.org",
        "//cdn.example.org/x.png",
        "https://github.com/someone-else/repo/tree/main/missing",
    ):
        assert link_path("README.md", target) is None, target


def test_strips_anchor_and_query_before_resolving():
    assert link_path("README.md", "csms.md#features") == "csms.md"
    assert link_path("README.md", "csms.md?plain=1") == "csms.md"
    assert link_path("README.md", "csms.md?plain=1#L3") == "csms.md"


def test_resolves_relative_to_the_linking_file():
    assert link_path("docs/x.md", "../csms.md") == "csms.md"
    assert link_path("docs/x.md", "content-taxonomy-audit.md") == (
        "docs/content-taxonomy-audit.md"
    )
    assert link_path("docs/x.md", "/csms.md") == "csms.md"


def test_percent_decodes_the_path():
    assert link_path("README.md", "docs/with%20space.md") == "docs/with space.md"
    assert is_tracked("docs/with space.md", TRACKED)


def test_resolves_repository_urls_on_github():
    base = "https://github.com/juherr/awesome-ev-charging"
    assert link_path("docs/x.md", f"{base}/blob/main/csms.md") == "csms.md"
    assert link_path("docs/x.md", f"{base}/tree/main/ocpp/OCPP-1.6/") == (
        "ocpp/OCPP-1.6"
    )
    assert link_path("docs/x.md", f"{base}/tree/main/ocpp#readme") == "ocpp"


def test_a_directory_resolves_when_a_tracked_path_lives_under_it():
    assert is_tracked("ocpp/OCPP-1.6", TRACKED)
    assert is_tracked("ocpp/OCPP-1.6/schemas", TRACKED)
    assert is_tracked("ocpp", TRACKED)
    assert not is_tracked("ocpp/OCPP-1.5", TRACKED)
    # A prefix of a name is not a directory.
    assert not is_tracked("ocpp/OCPP-1", TRACKED)


def test_a_case_mismatch_does_not_resolve():
    assert not is_tracked("readme.md", TRACKED)
    assert not is_tracked("OCPP/OCPP-1.6", TRACKED)


def test_a_link_escaping_the_repository_root_is_broken():
    assert link_path("docs/x.md", "../../outside.md") == ESCAPES_ROOT
    assert not is_tracked(ESCAPES_ROOT, TRACKED)


def test_broken_links_lists_every_failure_with_its_line():
    text = "[ok](csms.md)\n[bad](nope.md)\n\n[Bad](Csms.md)\n"
    assert broken_links("README.md", text, TRACKED) == [
        "README.md:2 -> nope.md",
        "README.md:4 -> Csms.md",
    ]


# --- The real repository ----------------------------------------------------


def test_first_party_markdown_list_is_not_empty():
    files = first_party_markdown()
    assert "README.md" in files
    assert "CONTRIBUTING.md" in files
    for exempt in VENDORED_VERBATIM_MARKDOWN:
        assert exempt not in files


@pytest.mark.parametrize("md_file", first_party_markdown())
def test_internal_links_resolve(md_file):
    text = (REPO_ROOT / md_file).read_text(encoding="utf-8")
    broken = broken_links(md_file, text, tracked_paths())
    assert not broken, "broken internal links:\n" + "\n".join(broken)
