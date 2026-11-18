# OSCP 2.0

Verbatim copy of the "OSCP 2.0 (all files)" download from the
[Open Charge Alliance](https://openchargealliance.org/my-oca/oscp/): the
specification (FINAL, 2020-10-12) and the JSON schemas from its `schemas.zip`,
extracted to `schemas/`.

| | |
| --- | --- |
| File | [`OSCP_2.0_Specification.zip`](https://openchargealliance.org/wp-content/uploads/downloads/OSCP_2.0_Specification.zip) |
| SHA-256 | `742eaa48e3cfcbd56f81c957a01c298c5048295e40be129a2dea2d6a52f2f853` |
| Retrieved | 2026-11-15 |

The specification PDF carries its own notice (PDF p. 4): "Copyright © 2010 –
2020 Open Charge Alliance. All rights reserved. This document is made
available under the Creative Commons Attribution-NoDerivatives 4.0
International Public License"
([legal code](https://creativecommons.org/licenses/by-nd/4.0/legalcode)).
The 26 JSON schemas carry no copyright or licence notice, and the PDF's notice
covers "this document" only, so their licence is not established. No right to
modify them is established either: they are kept exactly as published,
defects included, pending confirmation from the Open Charge Alliance. See
[the third-party assets inventory](../../docs/third-party-assets.md).

## Known defects in the published schemas

The specification PDF is normative. These schemas disagree with it:

| Schema | Defect | Specification |
| --- | --- | --- |
| `update-asset-measurements.json` | `measurements` puts `$ref: asset-measurement.json` beside `type: array` instead of under `items`, so draft-07 validates the whole array as one asset measurement and every valid message fails | §4.5.2: `AssetMeasurement`, cardinality `1..*` |
| `update-asset-measurements.json` | `$id` ends in `update-asset-measurement.json` (singular), not the file name | — |
| `version-url.json` | `$id` ends in `version_url.json`, while `register.json` refers to `version-url.json`; a validator that resolves by `$id` cannot find it | — |
| `group-capacity-compliance-error.json` | `forecasted_blocks` has `minItems: 1` | §4.4.3: cardinality `0..*` |

`tests/test_oscp_schemas.py` checks each of these defects, and that a local
patch of each one is enough, on in-memory copies of the schemas.

Patch them locally if you validate messages against these schemas.
