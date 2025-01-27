# Awesome Electric Vehicle [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

**A carefully curated list of EV-related tools and resources**

## Contents

- [OCPP](#ocpp)
  - [Server](#ocpp-servers)
  - [Simulator](#ocpp-simulators)
  - [Libraries](#ocpp-libraries)
  - [Misc](#ocpp-misc)
- [OCPI](#ocpi)
  - [Libraries](#ocpi-libraries)
- [eMI³](#emi)

[![ev roaming protocols](img/ev-roaming-protocols.jpg)](https://www.emobilitysimplified.com/2020/08/ev-roaming-protocol-differences-OCPI-OICP-OCHP-eMIP.html)

Here are some awesome tools for dealing with EV:

## OCPP

* [Wikipedia](https://en.wikipedia.org/wiki/Open_Charge_Point_Protocol)
* [Open Charge Aliance](https://www.openchargealliance.org/)
* Specifications
  * [1.2 (deprecated)](ocpp/OCPP-1.2)
  * [1.5 (deprecated)](ocpp/OCPP-1.5)
  * [1.6](ocpp/OCPP-1.6-Documentation_2019_12)
  * [1.6 - Security Whitepaper Ed3](ocpp/Whitepapers/OCPP-1.6-security-whitepaper-edition-3-2)
  * [2.0 (deprecated)](ocpp/OCPP-2.0)
  * [2.0.1](ocpp/OCPP-2.0.1)
  * [2.1](ocpp/OCPP-2.1)

### OCPP Servers

* [OCPP server implementation in Java](https://github.com/steve-community/steve)
* [Home Assistant integration for OCPP EV chargers](https://github.com/lbbrhzn/ocpp)
* [OCPP server and management UI written in .NET-Core](https://github.com/dallmann-consulting/ocpp.core)
* [Connectivity between WWCP and OCPP v1.6/v2.0](https://github.com/openchargingcloud/wwcp_ocpp)
* [Open Charge Point Protocol Node-Red Nodes](https://github.com/argonne-national-laboratory/node-red-contrib-ocpp)
* [Open e-Mobility Charging Station management backend server](https://github.com/charge-angels/ca-ev-server)

### OCPP Simulators

* [OCPP-J-CP-Simulator - A really simple OCPP 1.6 cp simulator](https://github.com/kubarskii/OCPP-J-CP-Simulator)
* [OCPP 1.6 Charge Point Simulator](https://github.com/javaisjavascript/ocpp-1.6-cp-simulator)
* [OCPP 2.0 Charge Point Simulator - A really simple OCPP 2.0 cp simulator](https://github.com/JavaIsJavaScript/OCPP-2.0-CP-Simulator)
* [Simple ocpp charger simulator](https://github.com/shellrechargesolutionseu/ocpp-charger)
* [Scriptable OCPP charge point simulator and test tool](https://github.com/shellrechargesolutionseu/docile-charge-point)
* [OCPP charger (charging station) simulator](https://github.com/vasyas/charger-simulator)
* [e-Mobility OCPP-J Charging Stations simulator](https://github.com/sap-labs-france/ev-simulator)

### OCPP Libraries

* [Python implementation of the Open Charge Point Protocol](https://github.com/mobilityhouse/ocpp)
* [Open Charge Point Protocol for Scala](github.com/ihomer/scala-ocpp)
* [Java-OCA-OCPP - A Java client and server library of Open Charge-Point Protocol](https://github.com/chargetimeeu/java-oca-ocpp)
* [OCPP 1.6 client for ESP32 / ESP8266](https://github.com/matth-x/ArduinoOcpp)
* [OCPP implementation in Go](https://github.com/lorenzodonini/ocpp-go)
* [v1.5 and v1.6 OCPP implementation in Golang](https://github.com/voltbras/go-ocpp)
* [OCPP implemented in Typescript](https://github.com/voltbras/ts-ocpp)
* [C++ implementation of the OCPP 1.6 protocol](https://github.com/c-jimenez/open-ocpp)
* [A Node.js client & server implementation of OCPP-J protcol](https://github.com/mikuso/ocpp-rpc)
* [Rust library for ocpp 1.6 and 2.0.1](https://github.com/codelabsab/rust-ocpp)
* [Java mappings for OCPP](https://github.com/steve-community/ocpp-jaxb)
* [Kotlin library to perform OCPP operations](https://github.com/izivia/ocpp-toolkit)

### OCPP Misc

* [OCPP Spec](https://ocpp-spec.org/)
* [OCPP AI](https://ocpp.vercel.app/)

## OCPI

* [EVRoaming Fundation](https://evroaming.org/)
* [Specifications](https://github.com/ocpi/ocpi)
  * [2.2.1](https://github.com/ocpi/ocpi/tree/release-2.2.1-bugfixes) - [pdf](https://github.com/ocpi/ocpi/releases/download/2.2.1/OCPI-2.2.1.pdf) 
  * [2.1.1](https://github.com/ocpi/ocpi/tree/release-2.1.1-bugfixes) - [pdf](https://github.com/ocpi/ocpi/releases/download/2.1.1-d2/OCPI_2.1.1-d2.pdf)

### OCPI Libraries

* [Endpoints in Scala](https://github.com/ShellRechargeSolutionsEU/ocpi-endpoints)
* [Client in PHP](https://github.com/ChargeMap/ocpi-protocol)
* [Server in Python](https://github.com/TECHS-Technological-Solutions/ocpi)
* [Endpoints and client in Kotlin](https://github.com/IZIVIA/ocpi-toolkit)
* [OCPI Types in TypeScript](https://github.com/gaia-green-tech/ocpi-types)
* [Endpoints in Python](https://github.com/NOWUM/pyOCPI)
* [OCPI Schema](https://github.com/solidstudiosh/ocpi-schema)

## eMI³

* [Website](http://emi3group.com/) ([Archive.org](https://web.archive.org/web/20230925033629/http://emi3group.com/))
* Specifications
  * eMi³ standard version V1.0 electric vehicle ICT interface specifications
    * [Part 1 v1.0](emi3/emi3-1.0/eMI3-standard-v1.0-Part-1.pdf)
    * [Part 2 v1.0](emi3/emi3-1.0/eMI3-standard-v1.0-Part-2.pdf)
    * [Terms and definitions v1.0](emi3/emi3-1.0/eMI3-standard-TermsAndDefinitions-v1.0.pdf)
  * eMi³ standard update, version V1.1 electric vehicle ICT interface specifications
    * [Part 1 v1.1](emi3/emi3-1.1/eMI3-standard-v1.1-Part-1.pdf)
    * [Terms and definitions v1.4](emi3/emi3-1.1/eMI3-standard-TermsAndDefinitions-v1.4.pdf)

---

**Not curated list**

[GitHub list](https://github.com/stars/juherr/lists/ev)
