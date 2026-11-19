# Third-party assets: rights and licences

This repository vendors third-party specifications as reference material, under
`ocpp/`, `oscp/`, `ocpi/`, `oicp/`, `eichrecht/`, `emi3/` and `nemo/`. This file
records, per file or directory, the rights holder, the licence and whether a
verbatim copy may be redistributed, with the evidence for each answer.

The repository's own CC0 licence (the root `LICENSE`) does **not** cover these
files. Each one stays under its rights holder's terms.

The repository convention applies: an empty or "unknown" value means we could
not verify it, never "no". A file marked Unknown is not forbidden, and one marked
Allowed is not free of conditions.

Research date: 2026-11-15, updated 2026-11-18 (OSCP evidence). This is a
record of what was found, not legal advice.

## Archival policy

This repository keeps copies of third-party specifications to preserve them.
eMI³, NeMo and OIOI documents have already vanished from their original sites,
and archived copies were the only remaining source. The purpose is
preservation and reference, not appropriation: files are kept byte-identical,
with their notices, attributed to their rights holders, and are never
relicensed.

Permission is not sought file by file. Instead, any rights holder who objects
to a file being here can open an issue or contact the maintainer, and the file
will be removed from the repository promptly. The verdicts below record what
each file's own notice says, so that such a request can be handled quickly.

## How to read the verdicts

- **Allowed** - a notice in the file, or a licence stated by the rights holder,
  permits verbatim redistribution. Every Allowed file is CC BY-ND 4.0: it may be
  shared only **unmodified** (no re-compression, page extraction or annotation),
  with the copyright notice, a reference to the licence and its URI kept
  (CC BY-ND 4.0 §2(a)(1) and §3(a),
  <https://creativecommons.org/licenses/by-nd/4.0/legalcode.en>). Every Allowed
  file carries its own notice.
- **Unknown** - no licence or permission was found, or the evidence is
  conditional. Nothing here concludes that redistribution is forbidden.

The repository's own files are not rated: `ocpp/OCPP-1.6-configuration-keys.md`
(a hand-written table, see the follow-up question on it below), the provenance
`README.md` of each OCPP schema folder (`ocpp/OCPP-1.6/schemas/`,
`ocpp/OCPP-2.0.1/OCPP-2.0.1_part3_JSON_schemas/`,
`ocpp/OCPP-2.1/OCPP-2.1_part3_JSON_schemas/` and
`ocpp/Whitepapers/OCPP-1.6-security-whitepaper-edition-4/schema/`),
`oscp/OSCP-2.0/README.md`, `emi3/README.md`, `nemo/README.md`, and the
`README.md` of `ocpp/OCPP-1.2/` and of `ocpp/OCPP-1.5/`. A licence
sentence in one of these READMEs is the repository's statement, not evidence of
the rights holder's; it is weighed as such below.

## Summary by verdict

| Verdict | Files | Paths |
| --- | --- | --- |
| Allowed | 215 | `ocpp/OCPP-1.6/*.pdf` (7), `ocpp/OCPP-1.6/schemas/soap/` (2), `ocpp/OCPP-2.0/*.pdf` (4), `ocpp/OCPP-2.0.1/*.pdf` (8), `ocpp/OCPP-2.1/*.pdf` (8), `ocpp/OCPP-2.1/OCPP-2.1_part3_JSON_schemas/` (181), `ocpp/Whitepapers/` (3 PDFs), `oscp/OSCP-2.0/OSCP 2.0 Specification.pdf`, `eichrecht/signed_meter_values-v10.pdf` |
| Unknown | 285 | `ocpp/OCPP-1.2/` (specification PDF and 2 WSDLs), `ocpp/OCPP-1.5/` (Specification PDF, Technical Description and 2 WSDLs), `ocpp/OCPP-1.6/schemas/json/` (56), `ocpp/OCPP-2.0/ReadMe.md`, `ocpp/OCPP-2.0.1/` (ReadMe, `Appendices_CSV_v1.5/` and the 128 JSON schemas, 136 files), `ocpp/OCPP-2.1/Appendices_CSV_v2.1/` and `ReadMe.md` (16), `ocpp/Whitepapers/OCPP-1.6-security-whitepaper-edition-4/schema/` (22), `oscp/OSCP-2.0/schemas/` (26), `ocpi/` (1), `oicp/` (4), `eichrecht/Presentation_Eichrecht_Plugfest.pdf`, `emi3/` (6 PDFs), `nemo/` (9 PDFs) |

The two verdicts add up to 500 files: every vendored file under the seven
directories except the ten repository files listed above. On 2026-11-18 the
OSCP schemas moved from Allowed to Unknown (26 files): none carries a notice,
and the only statement of a licence for them was the repository's own README.

These 500 files are pinned byte for byte by `tests/vendored_assets.sha256`
(SHA-256, checked by `tests/test_vendored_assets.py`, which also checks the
counts above against it). Adding, removing or replacing a vendored file
means recording it in this inventory, counts included, and regenerating the
manifest with `python tests/vendored_manifest.py --write`.

## OCPP (`ocpp/`)

Evidence was read in the files first (`pdftotext`, file headers), then on
openchargealliance.org. Counts in the Path column are files. The four OCA
download bundles behind the JSON schemas and the CSVs were also listed with
`unzip -l` (see the Open Charge Alliance follow-up).

| Path | Rights holder | Licence | Verbatim redistribution | Evidence |
| --- | --- | --- | --- | --- |
| `ocpp/OCPP-1.2/OCPP 1.2 specification.pdf.pdf` | Not stated | Not stated | **Unknown** | Historical OCPP release, superseded. |
| `ocpp/OCPP-1.2/*.wsdl.wsdl` (2) | Not stated | Not stated | **Unknown** | Historical OCPP release, superseded. |
| `ocpp/OCPP-1.5/OCPP 1.5 Specification.pdf` | Not stated | Not stated | **Unknown** | Historical OCPP release, superseded. |
| `ocpp/OCPP-1.5/OCPP 1.5 Technical Description.pdf` | Unknown. PDF author metadata: "Klaas van Zuuren"; the text says OCPP "is an open standard initiated by E-laad" | Unknown, no notice in the 7 pages | **Unknown** | `pdfinfo`: Author "Klaas van Zuuren", Creator "Microsoft Word 2010"; `pdftotext` finds no copyright or licence line. |
| `ocpp/OCPP-1.5/*_1.5_FINAL.wsdl.wsdl` (2) | e-laad.nl | Ad hoc: "Free to use without modifications." | **Unknown**: "use" does not clearly cover redistribution; the "without modifications" condition is met by a verbatim copy | Header comment: "Version 1.5 draft for approval (1.5 RC4) / Copyright e-laad.nl. Free to use without modifications." |
| `ocpp/OCPP-1.6/*.pdf` (7: edition 2, OCPP-J, OCPP-S, three errata sheets, ISO 15118 whitepaper) | Open Charge Alliance | CC BY-ND 4.0 | **Allowed** (CC BY-ND), notice in file | e.g. `ocpp-1.6 edition 2.pdf`: "Copyright © 2010 – 2017 Open Charge Alliance. All rights reserved. This document is made available under the *Creative Commons Attribution-NoDerivatives 4.0 International Public License*". Same in OCPP-J and OCPP-S (2010–2015), the errata sheets (OCPP and OCPP-J 2010–2025, OCPP-S 2010–2019) and `ocpp_1_6_ISO_15118_v10.pdf` (© 2020). |
| `ocpp/OCPP-1.6/schemas/soap/*.wsdl` (2) | Open Charge Alliance | CC BY-ND 4.0 | **Allowed** (CC BY-ND), notice in file | Header comment: "Copyright © 2010 – 2015 Open Charge Alliance. All rights reserved. This document is made available under the Creative Commons Attribution-NoDerivatives 4.0 International Public License". |
| `ocpp/OCPP-1.6/schemas/json/` (56) | Open Charge Alliance per [`schemas/README.md`](../ocpp/OCPP-1.6/schemas/README.md), which cites no notice for it | Unknown: no notice in any file or in the download bundle; the OCA pages state none | **Unknown** | 0 of 56 files match `copyright\|licen\|©\|creative`; the header is only `"id": "urn:OCPP:1.6:2019:12:…"`. The bundle `OCPP_1.6_documentation.zip` (SHA-256 `2a1d8028…`, as in the README) holds the PDFs, `schemas/soap/` and `schemas/json/`, and no licence file. Until 2026-11-18 the README claimed CC BY-ND 4.0 for the whole folder; it now states the licence of these files as not established. The only notices in the bundle are those of the PDFs and WSDLs. |
| `ocpp/OCPP-2.0/*.pdf` (4: changelog 2.0 to 2.0.1, part 1, 2 and 4 errata) | Open Charge Alliance | CC BY-ND 4.0 | **Allowed** (CC BY-ND), notice in file | PDF p. 1–2: "Copyright © 2010 – 2020 Open Charge Alliance. All rights reserved. This document is made available under the *Creative Commons Attribution-NoDerivatives 4.0 International Public License*". |
| `ocpp/OCPP-2.0/ReadMe.md` | Open Charge Alliance (zip readme, verbatim) | Unknown, no notice | **Unknown** | The file says "This zip contains the changelog and errata documents…"; no licence text. |
| `ocpp/OCPP-2.0.1/*.pdf` (8: Edition 4 parts 0, 1, 2 specification, 2 appendices v15, 4, 5, 6, errata 2026-09) | Open Charge Alliance | CC BY-ND 4.0 | **Allowed** (CC BY-ND), notice in file | Every PDF: "Copyright © 2010 – 2025 Open Charge Alliance. All rights reserved. This document is made available under the *Creative Commons Attribution-NoDerivatives 4.0 International Public License*" (errata: 2010 – 2026; part 6: "2010 - 2025"; part 2 specification: notice after the front matter). |
| `ocpp/OCPP-2.0.1/OCPP-2.0.1_part3_JSON_schemas/` (128) | Open Charge Alliance per [its README](../ocpp/OCPP-2.0.1/OCPP-2.0.1_part3_JSON_schemas/README.md), which cites no notice for it | Unknown: no notice in any file or in the download bundle; the OCA pages state none | **Unknown** | All 128 carry only `"comment": "OCPP 2.0.1 FINAL"`; 0 of 128 match `copyright\|licen\|©\|creative`. The bundle `OCPP-2.0.1_all_files.zip` (SHA-256 `9e025b7d…`, as in the README) holds the Edition 4 PDFs, the schemas zip, the CSV zip and `ReadMe.md`, and no licence file. The schemas date from 2020-03-31 and Edition 4 did not reissue them. |
| `ocpp/OCPP-2.0.1/Appendices_CSV_v1.5/` (6 CSV, 1 xlsx) | Unknown (presumably OCA; xlsx `dc:creator` "Buve, Franc") | Unknown, no notice in the CSVs or the xlsx (`sharedStrings.xml`, `core.xml`) | **Unknown** | 0 of 7 files match `copyright\|licen\|©` (the xlsx was read inside its archive); the bundle holds no licence file. |
| `ocpp/OCPP-2.0.1/ReadMe.md` | Open Charge Alliance (zip readme, verbatim) | Unknown, no notice | **Unknown** | "This zip contains the latest version of all OCPP 2.0.1 specification parts…" (Edition 4 changelog inside); no licence text. |
| `ocpp/OCPP-2.1/*.pdf` (8: Edition 2 parts 0, 1, 2 specification, 2 appendices v21, 4, 5, 6, errata 2026-09) | Open Charge Alliance | CC BY-ND 4.0 | **Allowed** (CC BY-ND), notice in file | "Copyright © 2010 – 2025 Open Charge Alliance. All rights reserved. This document is made available under the *Creative Commons Attribution-NoDerivatives 4.0 International Public License*" (errata: 2010 – 2026; part 6: "2010 - 2025"). |
| `ocpp/OCPP-2.1/OCPP-2.1_part3_JSON_schemas/` (181) | Open Charge Alliance | CC BY-ND 4.0 | **Allowed** (CC BY-ND), notice in file | 181 of 181: `"comment": "OCPP 2.1 Edition 1 (c) OCA, Creative Commons Attribution-NoDerivatives 4.0 International Public License"`. The schemas are the 2025-01-23 files, which Edition 2 did not reissue (README of the folder). |
| `ocpp/OCPP-2.1/Appendices_CSV_v2.1/` (14 CSV, 1 xlsx) | Unknown (presumably OCA; xlsx `dc:creator` "Buve, Franc") | Unknown, no notice in the CSVs or the xlsx | **Unknown** | 0 of 15 files match `copyright\|licen\|©`; the bundle `OCPP-2.1_all_files.zip` (SHA-256 `2774ada2…`) holds no licence file. |
| `ocpp/OCPP-2.1/ReadMe.md` | Open Charge Alliance (zip readme, verbatim) | Unknown, no notice | **Unknown** | "This zip contains the latest version of the OCPP 2.1 Edition 2 specification parts…"; no licence text. |
| `ocpp/Whitepapers/OCPP-1.6-security-whitepaper-edition-4/OCPP 1.6 security whitepaper edition 4.pdf` | Open Charge Alliance | CC BY-ND 4.0 | **Allowed** (CC BY-ND), notice in file | PDF p. 1: "Copyright © 2026 Open Charge Alliance. All rights reserved. This document is made available under the *Creative Commons Attribution-NoDerivatives 4.0 International Public License*" (edition 4, 2026-02-05). |
| `ocpp/Whitepapers/OCPP-1.6-security-whitepaper-edition-4/schema/` (22) | Open Charge Alliance per [its README](../ocpp/Whitepapers/OCPP-1.6-security-whitepaper-edition-4/schema/README.md), which cites no notice for it | Unknown: no notice in any file or in the download bundle | **Unknown** | 0 of 22 match `copyright\|licen\|©\|creative`; the header is only `"$id": "urn:OCPP:Cp:1.6:2020:3:…"`. The bundle `OCPP-1.6-security-whitepaper-edition-4.zip` (SHA-256 `158b883e…`) holds the PDF and `JSON_schemas.zip` only. |
| `ocpp/Whitepapers/improving_uptime_with_ocpp_v1_1.pdf` | Open Charge Alliance | CC BY-ND 4.0 | **Allowed** (CC BY-ND), notice in file | "Copyright © 2024 Open Charge Alliance. All rights reserved. This document is made available under the *Creative Commons Attribution-NoDerivatives 4.0 International Public License*". |
| `ocpp/Whitepapers/ocpp_1_x_multiple_connectors_per_evse.pdf` | Open Charge Alliance | CC BY-ND 4.0 | **Allowed** (CC BY-ND), notice in file | Same notice, © 2024 (v1.2 Final, 2024-03-25). |
| `ocpp/OCPP-1.6-configuration-keys.md` | Repository author (Julien Herr, commits `2d0b37d`, `7e732ab`); not an OCA file | The repository's root `LICENSE`: CC0 1.0 Universal (added in `aaa1bb9`) | Not applicable (own work), see the follow-up question below | `git log`. The file is a hand-written reference table that "reflects the OCPP 1.6 specification (edition 2) and the Security Whitepaper (edition 3)". |

Publisher pages checked. None of them states a licence for the downloads:

- <https://openchargealliance.org/protocols/open-charge-point-protocol/> lists
  only OCPP 1.6, 2.0.1 and 2.1 ("At the moment there are three versions of OCPP
  available."). Older versions sit behind
  <https://openchargealliance.org/protocols/archive/>, which served a "Sign in"
  page. The only rights text is the footer "© 2026 - All rights reserved".
- <https://openchargealliance.org/download-ocpp/> says "Create an account or
  proceed without one". <https://openchargealliance.org/my-oca/ocpp/> shows
  plain download links, with no form, no terms and no licence text. The
  `/download/…` links themselves were not followed.
- <https://openchargealliance.org/terms-of-service/> governs the "account area"
  and member profiles only. It says nothing on copying or redistributing
  documents.
- <https://openchargealliance.org/ocpp-info-whitepapers/> says "You can download
  all whitepapers for free." It states no licence.

## OSCP (`oscp/`)

Evidence read in the files on 2026-11-18 (`pdftotext`, `grep`). The folder's
[`README.md`](../oscp/OSCP-2.0/README.md) used to claim CC BY-ND 4.0 for all
its files; it now states what the files show.

| Path | Rights holder | Licence | Verbatim redistribution | Evidence |
| --- | --- | --- | --- | --- |
| `oscp/OSCP-2.0/OSCP 2.0 Specification.pdf` | Open Charge Alliance | CC BY-ND 4.0 | **Allowed** (CC BY-ND), notice in file | PDF p. 4: "Copyright © 2010 – 2020 Open Charge Alliance. All rights reserved. This document is made available under the *Creative Commons Attribution-NoDerivatives 4.0 International Public License* (<https://creativecommons.org/licenses/by-nd/4.0/legalcode>)." |
| `oscp/OSCP-2.0/schemas/` (26) | Open Charge Alliance per the folder README, which cites no notice for it | Unknown: no notice in any file (the download bundle was not re-opened) | **Unknown** | 0 of 26 files match `copyright\|licen\|©\|creative\|(c)`. They ship in the same `OSCP_2.0_Specification.zip` as the PDF, whose notice covers "this document" only. |

## OCPI (`ocpi/`)

| Path | Rights holder | Licence | Verbatim redistribution | Evidence |
| --- | --- | --- | --- | --- |
| `ocpi/OCPI-2.2.1.pdf` | EVRoaming Foundation | CC BY-ND 4.0 | **Unknown**: allowed for a licensor-issued build, but this copy is not the build upstream serves today and its provenance is not established (see Follow-ups) | PDF p. 9 (after the table of contents): "Copyright © 2014 – 2021 EVRoaming Foundation. All rights reserved. This document is made available under the Creative Commons Attribution- NoDerivatives 4.0 International Public License (<https://creativecommons.org/licenses/by-nd/4.0/legalcode>)." Same text in <https://github.com/ocpi/ocpi/blob/master/copyright.asciidoc> (GitHub reports the repository licence as `NOASSERTION`). CC BY-ND 4.0 §2(a)(1)(A) grants "reproduce and Share the Licensed Material, in whole or in part"; §3(a) sets the attribution conditions. |

## OICP (`oicp/`)

All four files are byte-identical (SHA-256) to release assets of
<https://github.com/hubject/oicp>, a repository licensed CC BY-SA 4.0. Whether
that repository licence covers these earlier assets is not established (see
Follow-ups).

| Path | Rights holder | Licence | Verbatim redistribution | Evidence |
| --- | --- | --- | --- | --- |
| `oicp/OICP-CPO-2.1.pdf` | Hubject GmbH | Unknown: the PDF states none | **Unknown** | Cover and every page footer: "© Hubject GmbH" (no licence, no "all rights reserved", no confidentiality notice in the text). SHA-256 `99a43382…` identical to the asset of <https://github.com/hubject/oicp/releases/tag/v2.1> (published 2019-06-11). |
| `oicp/OICP-EMP-2.1.pdf` | Hubject GmbH | Unknown | **Unknown** | Cover and footers: "© Hubject GmbH". SHA-256 `b3b63b6e…` identical to the v2.1 release asset of `hubject/oicp`. |
| `oicp/OICP-CPO-2.2.pdf` | Hubject GmbH | Unknown | **Unknown** | Cover: "VERSION 2.2 / MARCH 2018 ©HUBJECT GMBH"; footers "© Hubject GmbH". SHA-256 `f30c7882…` identical to the asset of <https://github.com/hubject/oicp/releases/tag/v2.2> (published 2019-06-11). |
| `oicp/OICP-EMP-2.2.pdf` | Hubject GmbH | Unknown | **Unknown** | Cover: "VERSION 2.2 / MARCH 2018 ©HUBJECT GMBH"; footers "© Hubject GmbH". SHA-256 `a9292976…` identical to the v2.2 release asset of `hubject/oicp`. |

## Eichrecht (`eichrecht/`)

Both PDFs name the Open Charge Alliance as rights holder. S.A.F.E. e.V. appears
only as a reference (`[S.A.F.E.], https://safe-ev.org/en/`) in
`signed_meter_values-v10.pdf`.

| Path | Rights holder | Licence | Verbatim redistribution | Evidence |
| --- | --- | --- | --- | --- |
| `eichrecht/signed_meter_values-v10.pdf` | Open Charge Alliance | CC BY-ND 4.0 | **Allowed** (CC BY-ND), notice in file | PDF p. 3: "OCA Application Note … Copyright © 2025 Open Charge Alliance. All rights reserved. This document is made available under the *Creative Commons Attribution-NoDerivatives 4.0 International Public License* (<https://creativecommons.org/licenses/by-nd/4.0/legalcode>)." SHA-256 `9cd62854…` identical to <https://openchargealliance.org/wp-content/uploads/2025/02/signed_meter_values-v10.pdf>. |
| `eichrecht/Presentation_Eichrecht_Plugfest.pdf` | Open Charge Alliance (per slide footer; PDF author metadata: Patrick Rademakers) | None found | **Unknown**: no licence or permission found | Every slide footer: "Open Charge Alliance © 2014-2021"; title slide "Eichrecht Whitepaper — OCPP Plugfest @ PIONIX 29-Feb-24". No licence text in the 12 pages. SHA-256 `817492bf…` identical to <https://openchargealliance.org/wp-content/uploads/2024/03/Presentation_Eichrecht_Plugfest.pdf>. OCA site: only "© 2026 - All rights reserved" in the footer; <https://openchargealliance.org/terms-of-service/> covers the member area only and says nothing about document reuse. |

## eMI³ (`emi3/`)

None of the six PDFs carries a copyright notice or a licence, and no publisher
page found grants one.

Common facts for all six files:

- Every file carries the same "Notice and Disclaimer" (liability and warranty
  disclaimers only). It says eMI³ "administers the process … it does not write
  the document". There is no © line, no licence and no reproduction clause
  anywhere in the text (full-text grep).
- The publisher is eMI³ AISBL. The standards carry the address line "eMI³ AISBL
  c/o ERTICO – ITS Europe, 326 Ave Louise, Brussels" (seen in v1.1 Part 1), and
  the QoS statement's footer reads "eMI³ c/o ERTICO – ITS Europe".
- The archived "How to join" page
  (<https://web.archive.org/web/20231206015919/https://emi3group.com/how-to-join/>)
  says "eMI³ strives to develop license-free standards" and "IPR rules and
  conditions are based on Fair, Reasonable and Non-Discriminatory (FRAND)
  policies". Both are about **implementing** the standard (essential IPR).
  Neither is a copyright licence for the document.
- The archived "Documents" page
  (<https://web.archive.org/web/20231206012317/https://emi3group.com/documents-links/>)
  offered each file as a public "Download", with no terms attached.
- The archived home page
  (<https://web.archive.org/web/20230925033629/http://emi3group.com/>) has no
  copyright footer and no legal or terms link.
- The Statutes and Internal Regulations might contain copyright rules. They
  were only shipped in `eMI3_Info_Package_2020.zip`, and the Wayback Machine
  holds no capture of it.

| Path | Rights holder | Licence | Verbatim redistribution | Evidence |
| --- | --- | --- | --- | --- |
| `emi3/eMI3-statement-on-QoS-2020-final.pdf` | Not stated. The publisher is eMI³ (c/o ERTICO). | None stated | **Unknown** | PDF p. 3 has the Notice and Disclaimer text only. The footer reads "eMI³ c/o ERTICO – ITS Europe … `www.emi3group.com`". There is no circulation table. |
| `emi3/emi3-1.0/eMI3-standard-TermsAndDefinitions-v1.0.pdf` | Not stated. The publisher is eMI³ AISBL. | None stated | **Unknown** | PDF p. 3, circulation: "Public". PDF p. 6 has the Notice and Disclaimer, no ©. |
| `emi3/emi3-1.0/eMI3-standard-v1.0-Part-1.pdf` | Not stated. The publisher is eMI³ AISBL. | None stated | **Unknown** | PDF p. 4, circulation: "Public". PDF p. 7 has the Notice and Disclaimer, no ©. |
| `emi3/emi3-1.0/eMI3-standard-v1.0-Part-2.pdf` | Not stated. The publisher is eMI³ AISBL. | None stated | **Unknown** | PDF p. 3, circulation: "Public". PDF p. 7 has the Notice and Disclaimer, no ©. |
| `emi3/emi3-1.1/eMI3-standard-TermsAndDefinitions-v1.4.pdf` | Not stated. The publisher is eMI³ AISBL. | None stated | **Unknown** | PDF p. 3, circulation: "Public (v1.0, eMI3 website)", "Public (v1.4, eMI3 website)". **However, the running header of every page from PDF p. 2 on reads "-IN WORK - Confidential"**, which contradicts the circulation table. PDF p. 6 has the Notice and Disclaimer, no ©. |
| `emi3/emi3-1.1/eMI3-standard-v1.1-Part-1.pdf` | Not stated. The publisher is eMI³ AISBL. The authors listed include IBM, CNR, Afirev, Allego, E.ON, ChargePoint, EDF, Bosch, Siemens, TNO and others. | None stated | **Unknown** | PDF p. 4, circulation: "Public (eMI3 website)", dated 11/12/2018. PDF p. 7: "While eMI3 administers the process … it does not write the document". No ©. |

## NeMo (`nemo/`)

None of the nine PDFs carries a © line or a licence (full-text grep), and no
publisher page found grants one. "Public (PU)" is a dissemination level: it says
the document was meant to be published, not that third parties may re-publish it.

Common facts for all nine files:

- NeMo was an H2020 project (grant 713794), coordinated by ICCS and running from
  2016-10-01 to 2019-09-30. The 37 participants include GIREVE, Hubject, IBM,
  ICOOR, UNIMORE, Renault, CRF, TomTom, Mosaic Factor and TU Berlin
  (<https://cordis.europa.eu/project/id/713794>).
- The deliverables carry "This project has received funding from the European
  Union's Horizon 2020 research and innovation programme under grant agreement
  no 713794". All seven deliverables and the CIM edition end (last PDF page)
  with "Disclaimer: Content reflects only the authors' view and European
  Commission is not responsible for any use that may be made of the information
  it contains."
- The H2020 Model Grant Agreement, Art. 26.1, says "Results are owned by the
  beneficiary that generates them". Art. 38.2.1(b) gives the **Commission** (not
  third parties) the right of "distribution to the public" of public
  deliverables. Source:
  <https://ec.europa.eu/research/participants/data/ref/h2020/mga/gga/h2020-mga-gga-multi_en.pdf>,
  v5.0 of 18.10.2017. NeMo's own grant agreement is not public and may follow an
  earlier version, so this is the template, not NeMo's text.
- The CORDIS legal notice (<https://cordis.europa.eu/about/legal/en>) says
  "Materials provided by beneficiaries receiving EU funding may only be used
  according to the terms" of the grant. The CORDIS `llms.txt`
  (<https://cordis.europa.eu/llms.txt>) says CC BY 4.0 "does NOT cover
  deliverables or publications uploaded by project beneficiaries". So the CC BY
  4.0 on CORDIS editorial content does **not** extend to these files.
- The CORDIS results page (<https://cordis.europa.eu/project/id/713794/results>)
  lists the deliverables. It states no licence and no dissemination level.
- The archived nemo-emobility.eu home page
  (<https://web.archive.org/web/20230205021136/https://nemo-emobility.eu/>) and
  its publications page have no copyright footer and no legal, terms or imprint
  link.

| Path | Rights holder | Licence | Verbatim redistribution | Evidence |
| --- | --- | --- | --- | --- |
| `nemo/NeMo-Common-Information-Models-1.pdf` | Not stated. Authors: ICCS, GIREVE, MOSAIC, CRF, fKA, TomTom. Under MGA Art. 26 the owners would be the generating beneficiaries (inference from the template). | None stated | **Unknown** | PDF p. 1 (printed "i"): "Version 1.0 Date 07/09/2017", with the H2020 grant line and no dissemination level. The last page has the EC disclaimer. |
| `nemo/NeMo-D1.1-Use-Cases-and-Actors_Final.pdf` | Not stated. Authors: ICOOR, GIREVE. | None stated | **Unknown** (PU is not a licence) | Cover: "Dissemination level Public (PU)", "Status Final", "Version number 2.0". |
| `nemo/NeMo-D1.3-Interoperability-and-Regulation-Requirements_Final.pdf` | Not stated. Author: Hubject. | None stated | **Unknown** (PU is not a licence) | Cover: "Dissemination level Public (PU)", "Status Final", "Version 1.0". |
| `nemo/NeMo-D2.3-Standards-and-protocols_Final-subject-to-EC-approval.pdf` | Not stated. Authors: IREN, IBM and others. | None stated | **Unknown** (PU is not a licence) | Cover: "Dissemination level Public (PU)", "Status Final". The filename says "subject to EC approval". |
| `nemo/NeMo-D3.2-Open-European-InterRoaming-Protocol_Final.pdf` | Not stated. Authors: GIREVE, Hubject. | None stated ("Open" in the title is not a licence) | **Unknown** (PU is not a licence) | Cover: "Dissemination level Public (PU)", "Status **Draft**", "Version 1.0" (despite `_Final` in the filename). The last page has the EC disclaimer. |
| `nemo/NeMo-D3.3-Common-Information-Models_Final.pdf` | Not stated. Authors: ICCS, GIREVE and others. | None stated | **Unknown** (PU is not a licence) | Cover: "Dissemination level Public (PU)", "Status Final". The last page has the EC disclaimer. |
| `nemo/NeMo-D6.3-Hyper-Network-Validation_Final.pdf` | Not stated. Author: ICOOR. | None stated | **Unknown** (PU is not a licence) | Cover: "Dissemination level Public (PU)", "Status Final", "Version 1.4". |
| `nemo/NeMo-D7.1-Global-adoption-and-self-cert-methodology_Final-subject-to-EC-approval.pdf` | Not stated. Authors: ICOOR – UNIMORE, Renault. | None stated | **Unknown** ("Public" is not a licence) | Cover: "Dissemination level Public" (no "PU" code), "Status Final version", "Version 1.2". The last page has the EC disclaimer. |
| `nemo/NeMo_ServiceCreation_Manual_05_2018-1.pdf` | Not stated. Authors: Nils Masuch, Johannes Fähndrich, Tobias Küster (TU Berlin, a NeMo participant per CORDIS). | None stated | **Unknown** | PDF p. 1: "NeMo Service Creation Tools - Manual … (TU Berlin) May 2018". The full text has no grant line, no dissemination level, no disclaimer and no ©. |

## Follow-ups

These are open points. Removing, replacing or relinking a file is left to a
separate editorial decision.

### Files with a conditional or contradictory marking

- `ocpi/OCPI-2.2.1.pdf` differs from the current upstream release asset. The
  asset of <https://github.com/ocpi/ocpi/releases/tag/2.2.1> was re-uploaded on
  2021-12-31 (SHA-256 `de16aff6…`, PDF created 2021-11-25). The vendored copy
  (`a322c477…`, PDF created 2021-11-11, committed here in `700fcb4` on
  2022-12-06) is an earlier build. Both state document version 2.2.1,
  2021-10-06, and carry the same CC BY-ND 4.0 notice. A `pdftotext` diff shows
  314 changed lines: shifted table-of-contents page numbers, a reordered
  changelog table, and one changelog entry present only upstream
  ("2.2.1-dX 202X-XX-XX Rudolph Froger … clarified use of Base64 for credentials
  token"). So it is a content difference, not only a format one, and CC BY-ND
  §2(a)(4) (technical modifications "never produces Adapted Material") does not
  cover it. Nothing found shows the licensor published this exact build (an
  earlier release asset is plausible but unverified;
  `https://evroaming.org/wp-content/uploads/2024/11/OCPI-2.2.1.pdf` answered
  404). Replacing the file with the current release asset would settle it.
- `emi3/emi3-1.1/eMI3-standard-TermsAndDefinitions-v1.4.pdf` is marked
  "-IN WORK - Confidential" in the running header of every page from PDF p. 2
  on. Its own circulation table (PDF p. 3) lists "Public (v1.4, eMI3 website)"
  on 11/12/2018, and eMI³ offered it for download on its Documents page. The
  header looks like a leftover from the drafting template; that is an
  inference. It is the only marking in the 15 eMI³ and NeMo files that points
  away from publication.

### Uncertainties by rights holder

What the research left uncertain, grouped by rights holder.

#### Open Charge Alliance

Files without an in-file notice: 257 in all, 231 from the OCPP bundles (the
1.6 and 2.0.1 JSON schemas, both `Appendices_CSV_*`, the three `ReadMe.md`,
the security-whitepaper schemas) and the 26 OSCP 2.0 schemas. They ship in
the same OCA bundles whose PDFs are CC BY-ND 4.0, but each PDF notice says
"This document is made available…", and no publisher page extends it to the
bundle. Whether CC BY-ND covers them is not established.

- Checked on 2026-11-15: `unzip -l` of the four OCPP bundles
  (`OCPP_1.6_documentation.zip`, `OCPP-2.0.1_all_files.zip`,
  `OCPP-2.1_all_files.zip`, `OCPP-1.6-security-whitepaper-edition-4.zip`,
  SHA-256 equal to those in the folder READMEs) lists the PDFs, the schema and
  CSV archives and `ReadMe.md`, and no licence or notice file. The nested
  schema and CSV archives were not opened: their extracted content is what
  the repository holds, and it has none. The OSCP bundle was not re-opened;
  its 26 extracted schemas carry no notice (checked 2026-11-18).
- The OCPP 2.1 schemas are the exception: their own `comment` carries the
  CC BY-ND 4.0 notice.
- Until 2026-11-18, the READMEs of `ocpp/OCPP-1.6/schemas/`,
  `ocpp/OCPP-2.0.1/OCPP-2.0.1_part3_JSON_schemas/`,
  `ocpp/Whitepapers/OCPP-1.6-security-whitepaper-edition-4/schema/` and
  `oscp/OSCP-2.0/` stated "© Open Charge Alliance and published under"
  CC BY-ND 4.0 for all their files, citing only the OCA download page, which
  states no licence. They now say what the files show: the PDFs and the 1.6
  WSDLs carry CC BY-ND 4.0, the other files carry no notice and their licence
  is not established, and they are kept verbatim.
- Other OCA points:
  - The Eichrecht Plugfest presentation has no licence. Neither the file nor
    any OCA page read (home, terms of service, privacy policy, search for
    "eichrecht") grants a reuse right. No source forbidding it was found
    either. The README already links the OCA URL, which serves the same bytes.
  - `ocpp/OCPP-1.5/OCPP 1.5 Technical Description.pdf` has no notice at all,
    and its publisher is not established.
  - The OCPP 1.5 WSDLs say "Free to use without modifications." Whether "use"
    includes public redistribution is unknown.
  - Whether the rights in OCPP 1.2 and 1.5 passed to the OCA is not
    established: the OCA page of older versions
    (<https://openchargealliance.org/protocols/archive/>) is login-gated and
    could not be read.

#### e-laad.nl and Logica, or their successors (OCPP 1.2 and 1.5)

The OCPP 1.2 and 1.5 specification PDFs come from e-laad.nl and the two
OCPP 1.2 WSDLs from Logica. Which organisation holds the rights in them today
was not researched; whether they passed to the OCA is one of the OCA points
above.

#### Hubject (OICP 2.1 and 2.2)

Does the CC BY-SA 4.0 licence of <https://github.com/hubject/oicp> cover the
OICP 2.1 and 2.2 PDFs?

- `License.md` was created on 2020-04-16 (commit "SE-3036 created
  License.md"), ten months after the v2.1 and v2.2 releases (2019-06-11).
- The `v2.1` and `v2.2` tag trees contain only a `README.md`, with no licence
  mention.
- The PDFs are release assets, not files in the tree, and carry only
  "© Hubject GmbH".
- The master tree today holds only OICP 2.3 (AsciiDoc); 2.1 was retired on
  2023-04-13 per the README.
- The release bodies say only "This is OICP v2.1 release." and "This is the
  OICP 2.2 protocol specification.", with no licence.
- The README that states CC BY-SA also links the v2.2 release, which supports
  reading the licence as covering it, but nothing states that the later
  repository licence extends to the earlier assets. If it does, CC BY-SA 4.0
  §2(a)(1)(A) allows verbatim sharing with attribution and a licence notice,
  which would have to be added next to the files since the PDFs carry none.
- `Hubject Acceptable Use Policy v1-0.asciidoc` in that repository governs use
  of Hubject's services, not the documents.

#### ERTICO – ITS Europe (eMI³ and NeMo)

- **eMI³** (ERTICO – ITS Europe is the address on the documents): the
  Statutes and Internal Regulations may contain a copyright or document-use
  clause. They were only in `eMI3_Info_Package_2020.zip`, which the Wayback
  Machine never captured. emi3group.com no longer answers. Whether eMI³
  AISBL still exists was not checked.
- **NeMo consortium** (the coordinator, ICCS, or ERTICO – ITS Europe, a NeMo
  participant per CORDIS): NeMo's actual grant and consortium agreements.
  Under the MGA template, ownership is per generating beneficiary. Any
  licence to the public would sit in the consortium agreement or a project
  decision, and neither is public. The site was still serving the files on
  2026-11-02 per `nemo/README.md`.

#### The repository's own table

- **CC BY-ND and `ocpp/OCPP-1.6-configuration-keys.md`**: it is the repository
  owner's own table of facts drawn from CC BY-ND documents. Whether it counts as
  "Adapted Material" (CC BY-ND §1: "translated, altered, arranged, transformed,
  or otherwise modified in a manner requiring permission") is a legal question
  not answered here.

### Fidelity and currency (informational, not licensing)

- The NeMo deliverables D2.3 and D7.1 are "subject to EC approval" and D3.2 is
  marked "Draft". They may differ from the versions the EC accepted. CORDIS's
  download module failed on 2026-11-02 (`nemo/README.md`), so this was not
  compared.
- The repository now holds OCPP 2.0.1 Edition 4, OCPP 2.1 Edition 2, the OCPP
  1.6 documentation of 2025-04 and the security whitepaper edition 4, as the OCA
  download page offers them. The whitepapers page listed uptime v1.3 when last
  read (repository: v1.1; not re-checked). CC BY-ND does not require tracking
  updates, but the repository may be pointing readers at outdated material.
- `ocpp/OCPP-1.6-configuration-keys.md` still cites the security whitepaper
  "edition 3", while the repository now vendors edition 4.
- Every eMI³ and NeMo file has a live or archived URL recorded in
  `emi3/README.md` and `nemo/README.md`, so linking instead of vendoring needs no
  licence. Whether to switch is a decision for the owner. This research does not
  conclude that redistribution is forbidden.
