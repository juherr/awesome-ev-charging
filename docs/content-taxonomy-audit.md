# Content taxonomy audit

Reviewed on 2026-11-15. This record explains editorial decisions; it is not a
second project registry. Project identity, descriptions and classifications stay
in the existing pipeline inputs.

## Existing coverage and gaps

| Area | Existing coverage | Gap and decision |
| --- | --- | --- |
| Regulation | Eichrecht specification notes | Add official jurisdiction-specific references for the EU, France, Germany and covered US federal projects. |
| Standards | OCPP, OCPI, OICP, ISO 15118 and other protocol specifications | Cross-reference existing protocol sections; add electrical safety, connectors, DIN communication and accessibility guidance. |
| Grid integration | OpenEMS under Energy management; EEBUS and OpenADR under Other protocols; OSCP in the pending catalogue | Add OpenADR and OSCP protocol mains; retain EMS under Other and add a focused charging-network simulation slot. |
| Testing | Protocol Simulator groups, miscellaneous tools and libraries | Distinguish Message inspection, Testing & conformance and Security testing within the relevant protocol. |
| ISO 15118 | Stacks, Plug&Charge, simulators, pyslac and trace tools | Separate EXI codecs and SLAC from stacks; move trace decoders out of Libraries. |
| Security & PKI | Other > Security, ISO 15118 > Plug&Charge and protocol tools | Keep existing categories; use a transverse guide instead of a competing security main. |
| Metering & Billing | Eichrecht, OCMF, signed meter values and OCPI tariff/CDR tooling | Keep these protocol categories and explain their distinct evidence and billing roles. |
| Data models | IRVE, OECS, DATEX II and identifier tools dispersed across Other | Add Other > Data models & identifiers; keep datasets under Analytics & data. |

`iso15118` and `Plug&Charge` retain their existing machine identifiers. Editorial
prose uses ISO 15118 and Plug & Charge. Renaming those identifiers would need a
cache migration without improving the current renderer's capabilities.

## Authority and generation boundaries

- README prose, including the new guides, is hand-authored outside generated
  markers. Its Contents and project listing are generated.
- `CATEGORY_TREE` is the taxonomy authority; `ADDITIONAL_REPOS` supplies explicit
  discovery candidates. `CATEGORY_OVERRIDES` pins reviewed placement across
  future enrichment runs, without changing project identity or promotion rules.
- `classifications.csv` is the committed description/category cache. Existing
  `signals` values must not be stamped as current merely to suppress model work.
- `repos.csv`, `repos.enriched.csv` and `cache_github/` are disposable artifacts;
  `legacy-projects.md` is generated. No new durable data store is introduced.
- The independent CSMS catalogue and its curated CSVs are unchanged.

The first-category-only renderer remains unchanged: a protocol primary wins
over Other, and each project is listed once. Hand-authored guides explain the
cross-cutting concerns instead of rendering duplicate project links. New
categories do not automatically promote a candidate into Selection.

Changing the taxonomy and classifier contract intentionally invalidates cached
prompt signatures for the next enrichment. A full automatic reclassification
is a separate, potentially lengthy monthly operation. Reviewed overrides
survive that operation; unreviewed entries keep their previous cached answer
until it is performed.

## Verification and editorial decisions

Capabilities below come from the named project's own README, not a third-party
awesome list. Readmes and GitHub repository metadata were inspected together:
a recent push does not override an explicit maintenance or archive statement.
Descriptions are original summaries. No content was imported from the
andreibesleaga awesome-list fork.

| Resource | Evidence and treatment |
| --- | --- |
| [OpenLEADR Rust](https://github.com/OpenLEADR/openleadr-rs) | README documents OpenADR 3.1 VEN library and VTN server, with 3.0 in earlier releases; add as a maintained candidate. Do not copy its broad CRA compliance claim. |
| [OpenLEADR Python](https://github.com/OpenLEADR/openleadr-python) | Documents OpenADR 2.0b client/server roles; [LF Energy](https://lfenergy.org/projects/openleadr/) explicitly calls it currently unmaintained. Retain as a historical candidate, not a maintained recommendation. |
| [hupe1980/openadr](https://github.com/hupe1980/openadr) | Documents 3.1 VEN/VTN and developer conformance checks; move from Other protocols to OpenADR. No certification claim is inferred. |
| [ChargePi/oscp-go](https://github.com/ChargePi/oscp-go) | README support table specifies OSCP 2.0 generated client/server code; move to OSCP > Libraries. |
| [evcc](https://github.com/evcc-io/evcc) | Solar-aware charging, load management and documented OCPP support; keep OCPP primary and Energy management as a secondary facet. |
| [ACN Portal](https://github.com/zach401/acnportal) | Caltech charging-data client, charging algorithm simulation and network constraints; add under Grid simulation. Does not claim general power-flow analysis or a VEN/VTN implementation. |
| [libcbv2g](https://github.com/EVerest/libcbv2g) | README specifies EXI encoding/decoding for DIN 70121, ISO 15118-2 and -20; add under EXI codecs. |
| [pyslac](https://github.com/ecog-io/pyslac) | ISO 15118-3 matching implementation; move from Libraries to SLAC. |
| [libslac](https://github.com/EVerest/libslac), [libiso15118](https://github.com/EVerest/libiso15118) | Both standalone repositories are archived; do not add them as maintained recommendations. The latter's feature matrix also marks Plug & Charge as work in progress. |
| [dsV2Gshark](https://github.com/dspace-group/dsV2Gshark), [Zelos V2G extension](https://github.com/zeloscloud/zelos-extension-v2g) | Trace decoding/inspection, not full communication stacks; move to Message inspection. |
| [DebugKit toolkit](https://github.com/ocpp-debugkit/toolkit), [Studio](https://github.com/ocpp-debugkit/studio), [CheckOCPP](https://github.com/vfg27/CheckOCPP) | Inspection, replay or schema checks; classify as Message inspection, not certification systems. DebugKit's umbrella repository remains distinct from its two products. |
| [VolatileOCPP](https://github.com/brandonprry/VolatileOCPP) | Documents partially implemented compliance-document scenarios; classify as developer Testing & conformance, not an official certification tool. |
| [tzi-OCTT](https://github.com/tzi-app/tzi-OCTT) | Documents a Python implementation of CSMS test scenarios; move from Simulator to Testing & conformance. Its name is not evidence of OCA recognition. |
| [SAP simulator](https://github.com/SAP/e-mobility-charging-stations-simulator), [OCPP Central System Tool](https://github.com/brunoluiz/ocpp-server-tool), [Simulator Lab](https://github.com/PlugSecure-Inc/ocpp-simulator-lab) | Own READMEs document charger, historical central-system and dual-role simulation respectively; explain these endpoint roles in the guide without splitting every protocol's existing Simulator bucket. |
| [ChargingStationApp](https://github.com/OpenChargingCloud/ChargingStationApp) | README states a testing/certification focus, but that is not official recognition; remove the ambiguous certification claim and identify newer protocol support as under development. |
| [nocpp](https://github.com/leonard-voss/nocpp), [OCPP fuzzer](https://github.com/OCPP-fuzzer/ocpp-fuzzer) | OCPP security-testing resources; the nocpp README announces continuing development on GitLab. GitHub inactivity must not be interpreted as project abandonment. |
| [V2GInjector](https://github.com/FlUxIuS/V2GInjector), [ChargeSploit](https://github.com/konicst1/ChargeSploit) | Packet injection and controllable EVCC/SECC behavior respectively; protocol-specific Security testing, with no certification claim. |
| [ISO15118ConformanceTests](https://github.com/OpenChargingCloud/ISO15118ConformanceTests) | Developer codec, session and cross-stack tests; the repository metadata does not identify a license and ISO schemas have separate terms. Retain as a source-available testing resource without asserting an open-source license or official recognition. |
| [OECS](https://github.com/ChargePi/oecs), [IRVE schemas](https://github.com/etalab/schema-irve), [mobilityid](https://github.com/juherr/mobilityid), [datex2-ts](https://github.com/ducminhquan/datex2-ts) | Schemas, data models or identifier utilities; move to Data models & identifiers. OECS remains a community specification. |
| [CharIN Unified Error Codes](https://github.com/charinev/unified-error-codes), [duplicate specification](https://github.com/unified-error-codes/specification) | The two READMEs are byte-identical and present the same draft; retain the CharIN-owned upstream listing and exclude the duplicate at render/ingest. Preserve both durable cache entries. |

## Official references and publication status

The README links directly to EUR-Lex, Légifrance, Gesetze im Internet, eCFR,
IEC, ISO and DIN Media. Publisher metadata was checked rather than extrapolated
from repository badges or filenames. In particular:

- DIN SPEC 70121:2014-12 is withdrawn and replaced by DIN/TS 70121:2024-11.
- IEC 61851-1:2017 is edition 3; IEC 62196-1:2025 is edition 5.
- ISO 15118-2:2014 is published and was confirmed in 2024; a revision draft is
  not the published replacement. ISO 15118-20:2022 is published, with a 2026
  amendment listed by ISO.
- CRA general application is in December 2027; earlier phased provisions exist.
  No blanket present-day requirement for every charger is asserted.
- AFIREV merged with Avere-France in 2024. Its identifier service is not a
  separate formal standards body.
- US Access Board recommendations distinguish existing accessibility duties
  from additional recommendations. NEVI-related applicability comes from
  23 CFR 680.102, not from a rule for every US installation.
- OCA's FAQ and CharIN's conformance page describe recognized programs.
  Community tests, simulators and trace validators remain separate.

Context7 CLI lookup was attempted for OpenLEADR using both the project name
and protocol name. Its results did not contain the project; no unrelated
library documentation was used. Project-owned READMEs and protocol-owner
publications supply the capability evidence instead. No external API syntax
or setup instructions are introduced by this change.

## Remaining limits

- Legal applicability still requires national provisions, equipment scope,
  assessment scope and current amendments; this catalogue is a source index.
- No claim is made that all editions in multipart standards families, all
  regional accessibility standards, or every grid interface are covered.
- A general grid power-flow simulator is not added solely because it can
  model electrical networks; ACN-Sim supplies the directly relevant charging
  simulation resource. Further additions need an EV-specific use case.
- The existing publication policy uses a one-year no-push threshold and archives
  for Dormant. This is a catalogue filter, not evidence of abandonment.
- A missing license declaration on a testing repository remains unresolved;
  public source access alone does not establish open-source licensing.

## Generation and validation record

The initial local ingest retrieved 644 repository records. For this editorial change,
the rendering input projects existing cached answers onto those real signals
and adds four individually reviewed answers. It deliberately does not introduce
the other newly discovered, unreviewed candidates or stamp existing signatures
as if a full LLM reclassification had happened. The disposable projection script
and downloaded evidence are under `.context/`; they are not publication inputs
or a replacement for the monthly pipeline.

GitHub redirects `evlinked/ocpi-rs` and `evlinked/ocpp-rs` to `mobilityhub-vn`.
Their existing displayed identifiers and working redirect URLs were retained
for this content-only pass. `SukritJaAIproject/EV_Charger_Fault_Detection_AI`
returns HTTP 404 and is omitted by ingestion; its cache entry is preserved.
The fresh metadata also moves `gertjana/ocpp-backend` across the existing
one-year dormancy threshold and restores two active entries to Selection.

Validation:

- 174 pytest tests pass after rebasing onto PR #76, including specialist placement, protocol priority,
  single listing, classifier-contract guidance and guide navigation.
- Markdown lint passes across the authored documentation.
- Awesome-list lint passes. In a new branch without tracking configuration,
  its remote-detection rule needs an ephemeral `branch.<name>.remote=origin`
  configuration for the check; no persistent Git setting was changed.
- The classification regression guard passes with 675 cache entries and no
  newly empty classification.
- Rendering twice from the same enriched input produces byte-identical README
  and legacy catalogue output.
- The renderer still warns about three pre-existing unreviewed rows under
  `Other > Misc` or `Other > Other`; these are retained for later curation
  rather than guessed into a category during this pass.

After rebasing onto PR #76, the final render uses that PR's enriched metadata
snapshot plus the four reviewed additions, preserving its new projects,
promotion decisions and parser fix. The final catalogue contains 204 Selection
entries, 155 Dormant entries and 287 candidates awaiting refinement.
