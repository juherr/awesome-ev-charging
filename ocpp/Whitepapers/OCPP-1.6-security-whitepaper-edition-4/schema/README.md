# OCPP 1.6 security whitepaper schemas

Verbatim copy of `JSON_schemas.zip`, extracted, from the
"OCPP 1.6 Security Whitepaper Edition 4" download on the
[Open Charge Alliance](https://openchargealliance.org/my-oca/ocpp/) site:

| | |
| --- | --- |
| File | [`OCPP-1.6-security-whitepaper-edition-4.zip`](https://openchargealliance.org/wp-content/uploads/downloads/OCPP-1.6-security-whitepaper-edition-4.zip), entry `JSON_schemas.zip` |
| SHA-256 | `158b883e8ee712fd80fad3610b69fad355f7831d7a0ccdd996ce6b5452ce6859` |
| Retrieved | 2026-11-15 |
| Whitepaper | Edition 4, 2026-02-05 |

22 schemas for the request and response messages the whitepaper adds to
OCPP 1.6 (certificate management, signed firmware, security events, logs),
JSON Schema draft-06, with a `$id` of the form
`urn:OCPP:Cp:1.6:2020:3:<Message>.req|conf`.

Edition 4 ships the same 22 files as edition 3
(`OCPP-1.6-security-whitepaper-edition-3-2.zip`), byte for byte. The core
OCPP 1.6 schemas are in [`ocpp/OCPP-1.6/schemas`](../../../OCPP-1.6/schemas/).

The schemas carry no copyright or licence notice, and the download bundle
holds no licence file. The whitepaper PDF of the same bundle is published
under the
[Creative Commons Attribution-NoDerivatives 4.0 International License](https://creativecommons.org/licenses/by-nd/4.0/legalcode),
but its notice covers "this document" only. The licence of these files is
not established. They are kept verbatim, as OCA ships them, pending
confirmation from the Open Charge Alliance. See
[the third-party assets inventory](../../../../docs/third-party-assets.md).
