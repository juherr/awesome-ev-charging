"""Every internal link in the tracked Markdown resolves to a tracked path.

An internal link is a relative link (`docs/x.md`, `../csms.md`, an image) or an
absolute link into this repository on github.com
(`https://github.com/juherr/awesome-ev-charging/tree/main/<path>`). Both are
resolved against the set `git ls-files` returns, not against the disk: macOS
resolves a path case-insensitively and CI runs on Linux, and an untracked local
file is not something a reader of the repository can open.

Links are read from Markdown inline links and images, reference definitions,
`href` / `src` attributes of inline HTML tags, and `<scheme:...>` autolinks.
Fenced code blocks, inline code spans and HTML comments are skipped. A code
span may wrap onto the following lines of its paragraph; an HTML comment may
span any number of lines.
"""

import functools
import posixpath
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

import pytest

import pipeline

REPO_ROOT = Path(__file__).resolve().parent.parent

# Verbatim upstream Markdown from the Open Charge Alliance. Their bytes are
# never edited, and markdownlint skips them by the exact-path exemptions in
# .markdownlint-cli2.jsonc: keep this list in step. Their links are checked
# like any other file's.
VENDORED_VERBATIM_MARKDOWN = frozenset(
    {
        "ocpp/OCPP-2.0/ReadMe.md",
        "ocpp/OCPP-2.0.1/ReadMe.md",
        "ocpp/OCPP-2.1/ReadMe.md",
    }
)

# Broken links that only an edit of vendored bytes could fix, as
# `(file, target)` pairs. Empty today. Should a re-vendoring break a link in
# one of the files above, add that exact pair here rather than editing the
# file or skipping it whole.
VENDORED_LINK_EXCEPTIONS = frozenset()

# What link_path returns for a relative link that climbs above the root.
ESCAPES_ROOT = "<escapes the repository root>"

REPO_URL = re.compile(
    r"^https://github\.com/juherr/awesome-ev-charging/(?:tree|blob)/main(?:/(.*))?$"
)
URL_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
BACKTICK_RUN = re.compile(r"`+")
# A line that starts a block, which ends the paragraph a code span lives in: an
# ATX heading, a list item, a blockquote or a table row. Fences are FENCE.
BLOCK_START = re.compile(
    r"^ {0,3}(?:#{1,6}(?:\s|$)|[-+*](?:\s|$)|\d{1,9}[.)](?:\s|$)|>|\|)"
)
# `](target)` or `](target "title")`, the target optionally in angle brackets
# and allowed one level of balanced parentheses.
INLINE_LINK = re.compile(
    r"\]\(\s*(?:<([^>\n]*)>|([^\s()<>]+(?:\([^\s()]*\)[^\s()<>]*)*))"
    r"(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)"
)
# `[label]: target` — but not a footnote definition `[^1]: text`.
REFERENCE_DEFINITION = re.compile(r"^ {0,3}\[(?!\^)[^\]]+\]:\s*(?:<([^>]*)>|(\S+))")
# An inline HTML tag on one line, and its `href` / `src` attribute values:
# double-quoted, single-quoted, or unquoted (no whitespace nor "'=<>`, as
# the HTML spec defines an unquoted attribute value).
HTML_TAG = re.compile(r"<[A-Za-z][A-Za-z0-9-]*(?:\s[^<>]*)?>")
HTML_LINK_ATTRIBUTE = re.compile(
    r"\s(?:href|src)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s\"'=<>`]+))",
    re.IGNORECASE,
)
# A CommonMark URI autolink `<scheme:...>`; `](<target>)` is a link
# destination, already matched by INLINE_LINK.
AUTOLINK = re.compile(r"(?<!\()<([A-Za-z][A-Za-z0-9+.-]{1,31}:[^\s<>]*)>")
COMMENT_OPEN = "<!--"
COMMENT_CLOSE = "-->"


def _blank(text):
    return " " * len(text)


def _blank_range(lines, start_line, start_col, end_line, end_col):
    """Blank `lines` from (start_line, start_col) to (end_line, end_col)."""
    for number in range(start_line, end_line + 1):
        line = lines[number]
        begin = start_col if number == start_line else 0
        end = end_col if number == end_line else len(line)
        lines[number] = line[:begin] + _blank(line[begin:end]) + line[end:]


def _closing_run(lines, number, run):
    """`(line, end column)` of the run closing the code span `run` opens, or None.

    A CommonMark code span may wrap onto the next lines of its paragraph, so
    the search stops at a blank line and at a line that starts a block: pairing
    backticks across table rows or list items would blank real links.
    """
    width = len(run.group(0))
    column = run.end()
    while True:
        for match in BACKTICK_RUN.finditer(lines[number], column):
            if len(match.group(0)) == width:
                return number, match.end()
        number += 1
        column = 0
        if number >= len(lines):
            return None
        line = lines[number]
        if not line.strip() or BLOCK_START.match(line) or FENCE.match(line):
            return None


def _blank_code_and_comments(text):
    """The lines of `text` with fenced code, code spans and HTML comments blanked.

    One left-to-right scan, so whichever of a code span and a comment opens
    first wins: backticks inside a comment are comment text, and a `<!--`
    inside a code span is code. An unmatched backtick run stays literal.
    """
    lines = text.splitlines()
    fence = None
    in_comment = False
    number = 0
    column = 0
    while number < len(lines):
        line = lines[number]
        if column == 0 and not in_comment:
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
                lines[number] = ""
                number += 1
                continue
            if opening:
                fence = opening.group(1)
                lines[number] = ""
                number += 1
                continue
        if in_comment:
            end = line.find(COMMENT_CLOSE, column)
            if end < 0:
                _blank_range(lines, number, column, number, len(line))
                number += 1
                column = 0
                continue
            end += len(COMMENT_CLOSE)
            _blank_range(lines, number, column, number, end)
            column = end
            in_comment = False
            continue
        comment = line.find(COMMENT_OPEN, column)
        run = BACKTICK_RUN.search(line, column)
        if run and (comment < 0 or run.start() < comment):
            closing = _closing_run(lines, number, run)
            if closing is None:
                column = run.end()
                continue
            end_line, end_column = closing
            _blank_range(lines, number, run.start(), end_line, end_column)
            number, column = end_line, end_column
            continue
        if comment >= 0:
            column = comment
            in_comment = True
            continue
        number += 1
        column = 0
    return lines


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
            target = next(
                value for value in attribute.groups() if value is not None
            )
            found.append((tag.start() + attribute.start(), target))
    for match in AUTOLINK.finditer(line):
        found.append((match.start(), match.group(1)))
    return sorted(found, key=lambda item: item[0])


def extract_links(text):
    """Return `(line number, target)` for every link outside code and comments."""
    links = []
    for number, line in enumerate(_blank_code_and_comments(text), start=1):
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


def broken_links(source, text, tracked, exceptions=frozenset()):
    """`file:line -> target` for every internal link that does not resolve.

    A `(source, target)` pair listed in `exceptions` is not reported.
    """
    broken = []
    for number, target in extract_links(text):
        if (source, target) in exceptions:
            continue
        path = link_path(source, target)
        if path is not None and not is_tracked(path, tracked):
            broken.append(f"{source}:{number} -> {target}")
    return broken


# The same heading pattern `pipeline._build_toc` slugs, and the explicit
# anchor `pipeline._render_grouped` emits before each generated subcategory.
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
EXPLICIT_ID = re.compile(r'<a\s+id="([^"]+)"\s*>')
GENERATED_PROJECTS = ("<!-- BEGIN GENERATED PROJECTS -->", "<!-- END GENERATED PROJECTS -->")
GENERATED_TOC = ("<!-- BEGIN GENERATED TOC -->", "<!-- END GENERATED TOC -->")


def page_anchors(text):
    """`(heading slugs, explicit ids)`, each mapping an anchor to its line.

    Heading slugs are GitHub's, deduplicated in document order with one shared
    `seen`, as `pipeline._slugify` computes them for the Contents list.
    """
    seen = {}
    headings = {}
    explicit = {}
    for number, line in enumerate(_blank_code_and_comments(text), start=1):
        heading = HEADING.match(line)
        if heading:
            headings[pipeline._slugify(heading.group(2).strip(), seen)] = number
        for match in EXPLICIT_ID.finditer(line):
            explicit[match.group(1)] = number
    return headings, explicit


def marker_lines(text, markers):
    """The 1-based line numbers of the two markers, as a range."""
    begin, end = (text[: text.index(marker)].count("\n") + 1 for marker in markers)
    return range(begin, end + 1)


def in_page_links(text):
    """`(line number, fragment)` for every `#fragment`-only link."""
    return [
        (number, target[1:])
        for number, target in extract_links(text)
        if target.startswith("#")
    ]


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


def tracked_markdown():
    return sorted(_git_ls_files("*.md"))


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


def test_extracts_unquoted_href_and_src_from_inline_html():
    text = (
        "<img src=missing.png> and <a class=x HREF=docs/x.md>X</a>\n"
        '<a href="quoted.md">Q</a> <img SRC=img/logo.png alt=logo>\n'
    )
    assert extract_links(text) == [
        (1, "missing.png"),
        (1, "docs/x.md"),
        (2, "quoted.md"),
        (2, "img/logo.png"),
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


def test_skips_links_inside_a_code_span_that_spans_lines():
    text = (
        "Run `[x](missing.md)\n"
        "and [y](missing.md)` then [z](a.md).\n"
        "A ``double\n"
        "[w](missing.md)`` span, then [v](b.md).\n"
    )
    assert extract_links(text) == [(2, "a.md"), (4, "b.md")]


def test_a_code_span_does_not_cross_a_blank_line():
    text = "An unmatched ` opens here\n\n[a](a.md) then ` is unmatched too\n"
    assert extract_links(text) == [(3, "a.md")]


@pytest.mark.parametrize(
    "block",
    [
        "- [a](a.md) list item `",
        "1. [a](a.md) ordered item `",
        "| [a](a.md) | table row ` |",
        "> [a](a.md) blockquote `",
        "# [a](a.md) heading `",
    ],
    ids=["list", "ordered", "table", "quote", "heading"],
)
def test_a_code_span_does_not_cross_into_a_new_block(block):
    text = f"An unmatched ` opens here\n{block}\n"
    assert extract_links(text) == [(2, "a.md")]


def test_a_code_span_does_not_swallow_a_fence():
    text = "An unmatched ` opens here\n```\n[a](missing.md) `\n```\n[b](b.md)\n"
    assert extract_links(text) == [(5, "b.md")]


def test_backticks_inside_a_comment_do_not_hide_its_end():
    text = (
        "<!-- a ` inside -->[after](a.md) and ` later\n"
        "<!--\n"
        "``\n"
        "-->[next](b.md) ``\n"
    )
    assert extract_links(text) == [(1, "a.md"), (4, "b.md")]


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


def test_page_anchors_dedupe_heading_slugs_and_collect_explicit_ids():
    text = (
        "## Server\n"
        "<!-- <a id=\"hidden\"></a> -->\n"
        '<a id="ocpp-server"></a>\n'
        "\n"
        "#### Server\n"
        "`<a id=\"code\"></a>`\n"
    )
    headings, explicit = page_anchors(text)
    assert headings == {"server": 1, "server-1": 5}
    assert explicit == {"ocpp-server": 3}
    assert in_page_links("[a](#server-1) [b](other.md#x)\n") == [(1, "server-1")]


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


def test_broken_links_skips_only_the_excepted_file_and_target():
    text = "[a](nope.md)\n[b](gone.md)\n"
    exceptions = frozenset({("README.md", "nope.md")})
    assert broken_links("README.md", text, TRACKED, exceptions) == [
        "README.md:2 -> gone.md",
    ]
    assert broken_links("docs/x.md", text, TRACKED, exceptions) == [
        "docs/x.md:1 -> nope.md",
        "docs/x.md:2 -> gone.md",
    ]


# --- The real repository ----------------------------------------------------


def test_markdown_list_includes_the_vendored_oca_files():
    files = tracked_markdown()
    assert "README.md" in files
    assert "CONTRIBUTING.md" in files
    for vendored in VENDORED_VERBATIM_MARKDOWN:
        assert vendored in files


@pytest.mark.parametrize("md_file", tracked_markdown())
def test_internal_links_resolve(md_file):
    text = (REPO_ROOT / md_file).read_text(encoding="utf-8")
    broken = broken_links(md_file, text, tracked_paths(), VENDORED_LINK_EXCEPTIONS)
    assert not broken, "broken internal links:\n" + "\n".join(broken)


# --- The README's in-page anchors -------------------------------------------


def _readme():
    return (REPO_ROOT / "README.md").read_text(encoding="utf-8")


def test_readme_in_page_links_resolve():
    text = _readme()
    headings, explicit = page_anchors(text)
    broken = [
        f"README.md:{number} -> #{fragment}"
        for number, fragment in in_page_links(text)
        if fragment not in headings and fragment not in explicit
    ]
    assert not broken, "unresolved in-page links:\n" + "\n".join(broken)


def test_readme_prose_links_into_generated_projects_use_explicit_ids():
    # A generated heading's slug is positional (`#server-1`): it moves to
    # another section as soon as a protocol gains or loses a subcategory.
    # Hand-written prose must link the stable id `_render_grouped` emits.
    text = _readme()
    headings, _ = page_anchors(text)
    projects = marker_lines(text, GENERATED_PROJECTS)
    toc = marker_lines(text, GENERATED_TOC)
    positional = [
        f"README.md:{number} -> #{fragment}"
        for number, fragment in in_page_links(text)
        if number not in projects
        and number not in toc
        and headings.get(fragment) in projects
    ]
    assert not positional, (
        "prose links to generated headings by slug:\n" + "\n".join(positional)
    )


LEGACY_LINK = re.compile(r"^legacy-projects\.md#(.+)$")


def explicit_ids(text):
    """Every explicit id of `text`, duplicates kept, outside code and comments."""
    return [
        match.group(1)
        for line in _blank_code_and_comments(text)
        for match in EXPLICIT_ID.finditer(line)
    ]


@pytest.mark.parametrize("md_file", ["README.md", "legacy-projects.md"])
def test_generated_explicit_ids_are_unique_and_never_shadow_a_heading_slug(md_file):
    text = (REPO_ROOT / md_file).read_text(encoding="utf-8")
    ids = explicit_ids(text)
    assert ids, "no explicit ids: _render_grouped emits one per subcategory"
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    assert not duplicates, f"ids repeated in {md_file}: {duplicates}"
    headings, _ = page_anchors(text)
    assert not set(headings) & set(ids)


def test_readme_links_into_legacy_projects_use_its_explicit_ids():
    # Every heading of legacy-projects.md is generated, Dormant and To refine
    # repeat the same ones, so a heading slug there is positional too.
    headings, explicit = page_anchors(
        (REPO_ROOT / "legacy-projects.md").read_text(encoding="utf-8"))
    wrong = []
    for number, target in extract_links(_readme()):
        link = LEGACY_LINK.match(target)
        if link and link.group(1) not in explicit:
            kind = "heading slug" if link.group(1) in headings else "unresolved"
            wrong.append(f"README.md:{number} -> {target} ({kind})")
    assert not wrong, "README links into legacy-projects.md:\n" + "\n".join(wrong)
