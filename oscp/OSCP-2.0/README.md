# OSCP 2.0

Verbatim copy of the "OSCP 2.0 (all files)" download from the
[Open Charge Alliance](https://openchargealliance.org/my-oca/oscp/): the
specification (FINAL, 2020-10-12) and the JSON schemas from its `schemas.zip`,
extracted to `schemas/`.

The material is © Open Charge Alliance and published under the
[Creative Commons Attribution-NoDerivatives 4.0 International License](https://creativecommons.org/licenses/by-nd/4.0/legalcode).
The NoDerivatives term rules out redistributing a modified copy, so the files
below are kept exactly as published, defects included.

## Known defects in the published schemas

The specification PDF is normative. These schemas disagree with it:

| Schema | Defect | Specification |
| --- | --- | --- |
| `update-asset-measurements.json` | `measurements` puts `$ref: asset-measurement.json` beside `type: array` instead of under `items`, so draft-07 validates the whole array as one asset measurement and every valid message fails | §4.5.2: `AssetMeasurement`, cardinality `1..*` |
| `update-asset-measurements.json` | `$id` ends in `update-asset-measurement.json` (singular), not the file name | — |
| `version-url.json` | `$id` ends in `version_url.json`, while `register.json` refers to `version-url.json`; a validator that resolves by `$id` cannot find it | — |
| `group-capacity-compliance-error.json` | `forecasted_blocks` has `minItems: 1` | §4.4.3: cardinality `0..*` |

Patch them locally if you validate messages against these schemas.
