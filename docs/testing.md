# Tests

What each file of the pytest suite in `tests/` covers. `AGENTS.md` keeps the
commands and one line per file.

`tests/test_csms.py` covers `csms.py`: the controlled feature vocabulary,
certificate derivation, product/company identity, merge precedence, table rendering, the curated-CSV
validations and render determinism. It needs no network — the one GitHub call
`merge` can make is monkeypatched — and it also validates the committed CSVs, so
a bad curated row fails there as well as at render time. `tests/test_pipeline.py`
covers `pipeline.py`'s classification layer — the CI guard, the "is there
anything to classify" rule, the backends' failure contract and what `enrich`
writes to the durable cache — with the backend and the README fetch stubbed, so
it needs no network and spawns no LLM CLI. The same file also covers category
parsing and the taxonomy aliases, README fetching over mocked HTTP (absent
versus unreadable, the byte-identical cache, the repo's host), protocol version
extraction, GitHub and Codeberg record building (`build_repo_record`,
`days_since_push`, dormancy), `ingest` keeping its previous CSV when a Codeberg
repo is unreadable, and the promotion of a Codeberg repo to the Selection.

`tests/test_discovery.py` covers `discovery.py` with `requests.get` stubbed
and the HTTP cache in a temporary directory, so it needs no network and never
writes `cache_github/`: the sources configuration (and that the committed
`discovery-sources.toml` monitors the Andrei Besleaga fork), a deleted source
told from a failed fetch, the token sent only to the GitHub API, URL
normalization, extraction and deduplication with provenance, the tracked sets,
every status rule (aliases merged by canonical name, the stale side of a
`changed`), the report's fields and byte-identical re-runs, and the CLI's exit
codes and that it writes nothing but `--report`.

`tests/test_vendored_assets.py` pins every vendored third-party file under
`ocpp/`, `ocpi/`, `oicp/`, `emi3/`, `eichrecht/`, `nemo/` and `oscp/` with the
SHA-256 manifest `tests/vendored_assets.sha256` (`shasum -a 256` format, so
`shasum -a 256 -c tests/vendored_assets.sha256` checks it too). One case per
directory fails on a file added, missing or modified. The repository's own
files there (the provenance READMEs, `ocpp/OCPP-1.6-configuration-keys.md`)
are listed in `FIRST_PARTY` in `tests/vendored_manifest.py` and not pinned;
the verbatim OCA `ReadMe.md` files are. It also checks that the Allowed and
Unknown counts of `docs/third-party-assets.md` add up to the manifest. After a
deliberate addition, removal or upgrade, update the inventory and run
`python tests/vendored_manifest.py --write`; never regenerate to silence an
unexplained change. Both the test and `--write` list files with `git ls-files`,
so `git add` a new file first: an untracked one is neither pinned nor reported.

`tests/test_oscp_schemas.py` takes the `oscp/OSCP-2.0/` schema set from that
manifest and proves each defect listed in its README, and that the local
patches suffice, with `jsonschema` in memory.

The public JSON export is covered by three test files: `tests/test_public_export.py`
(`projects.json` from fixture renders), `tests/test_csms_export.py`
(`csms.json`, plus the committed `data/csms.json` and its manifest entry
against a fresh export of the committed CSVs) and `tests/test_public_data.py`
(both payloads against `data/schema/*.json` with `jsonschema`, from
`requirements-dev.txt`, the export agreeing with the Markdown tiers, and a
committed `data/projects.json` matching its `projects` manifest entry — skipped
until #98 commits it, and exercised on a fixture render meanwhile).

`tests/test_markdown_links.py` checks that every relative link, and every
`https://github.com/juherr/awesome-ev-charging/(tree|blob)/main/…` link, in
every tracked Markdown file resolves to a path `git ls-files` lists — a
tracked file, or a directory holding one — compared case-sensitively as on the
Linux runner, so a link that only works on macOS fails. It reads Markdown links
and images, reference definitions, `href` / `src` in inline HTML and
`<https://…>` autolinks. Anchors are not checked, and links in code or in HTML
comments are skipped, as is an `href` / `src` in an HTML tag split across
lines: tags are matched one line at a time. The three verbatim OCA `ReadMe.md`
files are checked too, though markdownlint skips them (see `AGENTS.md`): a link that only
an edit of their bytes could fix goes in `VENDORED_LINK_EXCEPTIONS` as an exact
`(file, target)` pair (empty today), never by skipping the file.
