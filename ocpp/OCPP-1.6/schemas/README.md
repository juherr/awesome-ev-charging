# OCPP 1.6 schemas

Verbatim copy of `OCPP_1.6_documentation/schemas/` from the
"OCPP 1.6 (all files & errata)" download on the
[Open Charge Alliance](https://openchargealliance.org/my-oca/ocpp/) site:

| | |
| --- | --- |
| File | [`OCPP_1.6_documentation.zip`](https://openchargealliance.org/wp-content/uploads/2025/04/OCPP_1.6_documentation.zip) |
| SHA-256 | `2a1d80284ca60449e85951fc55bc0538b5d45bd6f97c6d9228745acacb52c11b` |
| Retrieved | 2026-11-15 |
| Specification | OCPP 1.6 edition 2; OCPP 1.6 and OCPP-J errata sheets of 2025-04, OCPP-S errata sheet of 2019-12 |

- `json/`: the 56 OCPP-J message schemas, JSON Schema draft-04, with an `id`
  of the form `urn:OCPP:1.6:2019:12:<Message>Request|Response`.
- `soap/`: the two OCPP-S WSDL files, `OCPP_CentralSystemService_1.6.wsdl`
  and `OCPP_ChargePointService_1.6.wsdl`.

`StopTransaction.json` is the only schema changed since the 2019-12 release:
its `id` reads `urn:OCPP:1.6:2025:04:StopTransactionRequest` and its
`unit` enumeration adds `Celsius`. The files keep the line endings OCA ships
them with: CRLF, except `StopTransaction.json`, which is LF.

The schemas for the messages added by the
[OCPP 1.6 security whitepaper](../../Whitepapers/OCPP-1.6-security-whitepaper-edition-4/schema/)
are a separate download.

The two WSDL files in `soap/` carry their own notice: "Copyright © 2010 –
2015 Open Charge Alliance. All rights reserved. This document is made
available under the Creative Commons Attribution-NoDerivatives 4.0
International Public License"
([legal code](https://creativecommons.org/licenses/by-nd/4.0/legalcode)).

The 56 JSON schemas in `json/` carry no copyright or licence notice, and
neither the download bundle nor the OCA download pages state one. Their
licence is not established. They are kept verbatim, as OCA ships them. See
[the third-party assets inventory](../../../docs/third-party-assets.md).
