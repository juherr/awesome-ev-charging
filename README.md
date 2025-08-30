# Awesome Electric Vehicle [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

**A carefully curated list of EV-related tools and resources**

This repository contains a collection of specifications, tools, and resources related to electric vehicle (EV) charging protocols. It aims to be a central point of information for developers and enthusiasts working in the e-mobility space.

## Contents

- [Specifications](#specifications)
  - [OCPP (Open Charge Point Protocol)](#ocpp-open-charge-point-protocol)
  - [ISO 15118](#iso-15118)
  - [OCPI (Open Charge Point Interface)](#ocpi-open-charge-point-interface)
  - [OICP (Open InterCharge Protocol)](#oicp-open-intercharge-protocol)
  - [eMI³ (eMobility ICT Interoperability)](#emi-emobility-ict-interoperability)
  - [Eichrecht](#eichrecht)
  - [OIOI (discontinued)](#oioi-discontinued)
- [Tools and Resources](#tools-and-resources)
  - [OCPP](#ocpp-1)
    - [Servers](#servers)
    - [Simulators](#simulators)
    - [Libraries](#libraries)
    - [Misc](#misc)
  - [ISO 15118](#iso-15118-1)
    - [Plug & Charge](#plug--charge)
    - [Misc](#misc-1)
  - [OCPI](#ocpi-1)
    - [Libraries](#libraries-1)
  - [OICP](#oicp-1)
    - [Libraries](#libraries-2)
  - [Eichrecht](#eichrecht-1)
  - [Charging Station Management Systems (CSMS)](#charging-station-management-systems-csms)
  - [Charging Station Projects](#charging-station-projects)
- [Contributing](#contributing)
- [Other Resources](#other-resources)

[![ev roaming protocols](img/ev-roaming-protocols.jpg)](https://www.emobilitysimplified.com/2020/08/ev-roaming-protocol-differences-OCPI-OICP-OCHP-eMIP.html)

## Specifications

### OCPP (Open Charge Point Protocol)

The **Open Charge Point Protocol (OCPP)** is a communication protocol between electric vehicle charging stations and a central management system.

* [Wikipedia](https://en.wikipedia.org/wiki/Open_Charge_Point_Protocol)
* [Open Charge Aliance](https://www.openchargealliance.org/)
* Specifications
  * [2.1](ocpp/OCPP-2.1) (2025-01)
  * [2.0.1](ocpp/OCPP-2.0.1) (2020-04)
  * [2.0 (deprecated)](ocpp/OCPP-2.0) (2018)
  * [1.6](ocpp/OCPP-1.6-Documentation_2019_12) (2015)
  * [1.6 - Security Whitepaper Ed3](ocpp/Whitepapers/OCPP-1.6-security-whitepaper-edition-3-2)
  * [1.5 (deprecated)](ocpp/OCPP-1.5) (2012)
  * [1.2 (deprecated)](ocpp/OCPP-1.2) (2010)

### ISO 15118

**ISO 15118** is an international standard for communication between electric vehicles and the charging station.

* [Wikipedia](https://en.wikipedia.org/wiki/ISO_15118)
* [iso.org](https://www.iso.org/search.html?PROD_isoorg_en%5Bquery%5D=15118&PROD_isoorg_en%5Bmenu%5D%5Bfacet%5D=standard)

### OCPI (Open Charge Point Interface)

The **Open Charge Point Interface (OCPI)** is a protocol for roaming between charging station networks.

* [EVRoaming Fundation](https://evroaming.org/)
* [Specifications on GitHub](https://github.com/ocpi/ocpi)
  * [2.3.0](https://evroaming.org/wp-content/uploads/2025/02/OCPI-2.3.0.pdf) (2025-02)
  * [2.2.1](https://github.com/ocpi/ocpi/releases/download/2.2.1/OCPI-2.2.1.pdf) (2021-10)
  * [2.2.0-d2](https://github.com/ocpi/ocpi/releases/download/2.2-d2/OCPI-2.2-d2.pdf) (2020-06)
  * [2.2.0](https://github.com/ocpi/ocpi/releases/download/2.2/OCPI-2.2.pdf) (2019-09)
  * [2.1.1-d2](https://github.com/ocpi/ocpi/releases/download/2.1.1-d2/OCPI_2.1.1-d2.pdf) (2019-06)
  * [2.1.1](https://github.com/ocpi/ocpi/releases/download/2.1.1/OCPI_2.1.1.pdf) (2017-06)
  * 2.1.0 - Deprecated, contains some bugs, use 2.1.1 instead (2016-04)
  * [2.0](https://github.com/ocpi/ocpi/files/135934/OCPI_2.0-d2.pdf) (2016-02)

### OICP (Open InterCharge Protocol)

The **Open InterCharge Protocol (OICP)** is another protocol for roaming, developed by Hubject.

* [Specifications on GitHub](https://github.com/hubject/oicp)
  * [2.3](https://github.com/hubject/oicp/tree/master/OICP-2.3) (2020-10)
  * [2.2 CPO](https://github.com/hubject/oicp/releases/download/v2.2/OICP-CPO-2.2.pdf), [2.2 EMP](https://github.com/hubject/oicp/releases/download/v2.2/OICP-EMP-2.2.pdf) (2017-10)
  * [2.1 CPO](https://github.com/hubject/oicp/releases/download/v2.1/OICP-CPO-2.1.pdf), [2.1 EMP](https://github.com/hubject/oicp/releases/download/v2.1/OICP-EMP-2.1.pdf) (2016-10, retired 2023-04-13)

### eMI³ (eMobility ICT Interoperability)

**eMI³ (eMobility ICT Interoperability)** was a European initiative for e-mobility interoperability.

* [Website (archived)](https://web.archive.org/web/20230925033629/http://emi3group.com/)
* Specifications
  * eMi³ standard version V1.1 electric vehicle ICT interface specifications (2019-10)
    * [Part 1 v1.1](emi3/emi3-1.1/eMI3-standard-v1.1-Part-1.pdf)
    * [Terms and definitions v1.4](emi3/emi3-1.1/eMI3-standard-TermsAndDefinitions-v1.4.pdf)
  * eMi³ standard version V1.0 electric vehicle ICT interface specifications (2019-10)
    * [Part 1 v1.0](emi3/emi3-1.0/eMI3-standard-v1.0-Part-1.pdf)
    * [Part 2 v1.0](emi3/emi3-1.0/eMI3-standard-v1.0-Part-2.pdf)
    * [Terms and definitions v1.0](emi3/emi3-1.0/eMI3-standard-TermsAndDefinitions-v1.0.pdf)

### Eichrecht

**Eichrecht** is a German law for calibration and verification of measuring instruments, which applies to EV charging.

* [Whitepaper](https://openchargealliance.org/wp-content/uploads/2024/03/Presentation_Eichrecht_Plugfest.pdf)
* [Signed Meter Values in OCPP](https://openchargealliance.org/wp-content/uploads/2025/02/signed_meter_values-v10.pdf)

### OIOI (discontinued)

* [Latest specifications](https://juherr.dev/oioi-documentation/)

## Tools and Resources

### OCPP

#### Servers
* [steve-community/steve](https://github.com/steve-community/steve) (Java, 1.2S, 1.2J, 1.5S, 1.5J, 1.6S, 1.6J)
* [lbbrhzn/ocpp](https://github.com/lbbrhzn/ocpp) (Python/Home Assistant, 1.6J, 2.0.1, 2.1 experimental)
* [dallmann-consulting/ocpp.core](https://github.com/dallmann-consulting/ocpp.core) (.NET Core, 1.6J, 2.0)
* [openchargingcloud/wwcp_ocpp](https://github.com/openchargingcloud/wwcp_ocpp) (C#, 1.5, 1.6, 2.0.1, 2.1)
* [argonne-national-laboratory/node-red-contrib-ocpp](https://github.com/argonne-national-laboratory/node-red-contrib-ocpp) (Node-RED/Node.js, 1.5S, 1.6S, 1.6J)
* [ShellRechargeSolutionsEU/ocpp](https://github.com/ShellRechargeSolutionsEU/ocpp) (Scala, 1.5, 1.6, 2.0 partial)
* [c-jimenez/open-ocpp](https://github.com/c-jimenez/open-ocpp) (C++, 1.6, 2.0.1)
* [codelabsab/rust-ocpp](https://github.com/codelabsab/rust-ocpp) (Rust, 1.6, 2.0.1, 2.1)

#### Simulators
* [kubarskii/OCPP-J-CP-Simulator](https://github.com/kubarskii/OCPP-J-CP-Simulator) (JavaScript, 1.6)
* [javaisjavascript/ocpp-1.6-cp-simulator](https://github.com/javaisjavascript/ocpp-1.6-cp-simulator) (Node.js, 1.6)
* [JavaIsJavaScript/OCPP-2.0-CP-Simulator](https://github.com/JavaIsJavaScript/OCPP-2.0-CP-Simulator) (JavaScript, 2.0)
* [shellrechargesolutionseu/ocpp-charger](https://github.com/shellrechargesolutionseu/ocpp-charger) (Scala, 1.5/1.6 SOAP & JSON)
* [shellrechargesolutionseu/docile-charge-point](https://github.com/shellrechargesolutionseu/docile-charge-point) (Scala, 1.5, 1.6, 2.0)
* [vasyas/charger-simulator](https://github.com/vasyas/charger-simulator) (TypeScript, 1.5 SOAP, 1.6 JSON)
* [sap/e-mobility-charging-stations-simulator](https://github.com/sap/e-mobility-charging-stations-simulator) (TypeScript/Node.js, 1.6, 2.x)

#### Libraries
**C++**
* [c-jimenez/open-ocpp](https://github.com/c-jimenez/open-ocpp) (1.6, 2.0.1)
* [matth-x/ArduinoOcpp](https://github.com/matth-x/ArduinoOcpp) (1.6, 2.0.1)

**Go**
* [lorenzodonini/ocpp-go](https://github.com/lorenzodonini/ocpp-go) (1.6, 2.0.1)
* [voltbras/go-ocpp](https://github.com/voltbras/go-ocpp) (1.5 SOAP, 1.6 JSON)
* [ChargePi/ocpp-manager](https://github.com/ChargePi/ocpp-manager) (1.6, 2.0.1 planned)

**Java**
* [chargetimeeu/java-oca-ocpp](https://github.com/chargetimeeu/java-oca-ocpp) (1.6 SOAP & JSON, 2.0.1)
* [steve-community/ocpp-jaxb](https://github.com/steve-community/ocpp-jaxb) (1.2, 1.5, 1.6 SOAP & JSON, 2.0.1 JSON)

**Kotlin**
* [izivia/ocpp-toolkit](https://github.com/izivia/ocpp-toolkit) (1.5, 1.6, 2.0.1)

**Node.js**
* [mikuso/ocpp-rpc](https://github.com/mikuso/ocpp-rpc) (1.6, 2.0.1, 2.1)

**Python**
* [mobilityhouse/ocpp](https://github.com/mobilityhouse/ocpp) (1.6, 2.0.1)

**Rust**
* [codelabsab/rust-ocpp](https://github.com/codelabsab/rust-ocpp) (1.6, 2.0.1, 2.1)

**Scala**
* [ihomer/scala-ocpp](https://github.com/ihomer/scala-ocpp) (1.5, 1.6, 2.0 partial)

**TypeScript**
* [voltbras/ts-ocpp](https://github.com/voltbras/ts-ocpp) (1.5 SOAP, 1.6 JSON)

#### Misc
* [OCPP Spec](https://ocpp-spec.org/)
* [OCPP AI](https://openchargealliance.org/oca-i-chatbot/)
* [ChargeFlow CLI for debugging and validating OCPP messages](https://github.com/ChargePi/chargeflow)

### ISO 15118

#### Plug & Charge
* [OPNC](https://github.com/charinev/opnc)
* [OPCP](https://github.com/hubject/opcp)

#### Misc
* [sniffer-iso15118vse](https://github.com/endland/sniffer-iso15118vse)

### OCPI

#### Libraries
**Go**
* [ChargePi/ocpi-sdk-go](https://github.com/ChargePi/ocpi-sdk-go) (2.2.1)

**Kotlin**
* [izivia/ocpi-toolkit](https://github.com/IZIVIA/ocpi-toolkit) (2.2.1)

**PHP**
* [ChargeMap/ocpi-protocol](https://github.com/ChargeMap/ocpi-protocol) (2.1.1, archived)

**Python**
* [TECHS-Technological-Solutions/ocpi](https://github.com/TECHS-Technological-Solutions/ocpi) (2.2.1)
* [NOWUM/pyOCPI](https://github.com/NOWUM/pyOCPI) (2.2)

**Scala**
* [ShellRechargeSolutionsEU/ocpi-endpoints](https://github.com/ShellRechargeSolutionsEU/ocpi-endpoints) (2.1.1, archived)

**TypeScript**
* [gaia-green-tech/ocpi-types](https://github.com/gaia-green-tech/ocpi-types) (2.1.1, 2.2)
* [solidstudiosh/ocpi-schema](https://github.com/solidstudiosh/ocpi-schema) (2.1.1, 2.2, 2.2.1)

### OICP

#### Libraries
* [ChargePi/oicp-sdk-go](https://github.com/ChargePi/oicp-sdk-go) (Go, 2.2, 2.3)

### Eichrecht

* [OCMF](https://github.com/SAFE-eV/OCMF-Open-Charge-Metering-Format/)
* [transparenzsoftware](https://github.com/SAFE-eV/transparenzsoftware)
* [OCMF Go SDK](https://github.com/ChargePi/ocmf-go)

### Charging Station Management Systems (CSMS)

* [thoughtworks/maeve-csms](https://github.com/thoughtworks/maeve-csms) (Go, OCPP 1.6j, 2.0.1, ISO 15118)
* [citrineos/citrineos-core](https://github.com/citrineos/citrineos-core) ([doc](https://github.com/citrineos/citrineos)) (TypeScript/Node.js, OCPP 2.0.1)
* [EVerest/everest-core](https://github.com/EVerest/everest-core) (C++/Python/Rust, OCPP 1.6, 2.0.1, ISO 15118)

### Charging Station Projects

* [OpenEVSE/open_evse](https://github.com/OpenEVSE/open_evse) (C++, 1.6)
* [ChargePi/ChargePi-go](https://github.com/ChargePi/ChargePi-go) (Go, 1.6, 2.0.1 planned)

---

## Contributing

Contributions are welcome! If you know of a tool or resource that is not on the list, please feel free to add it.

The easiest way to contribute is to [open an issue](https://github.com/juherr/awesome-ev/issues/new/choose) using the "Add a link" template.

You can also submit a pull request. Please try to follow the existing format.

---

## Other Resources

Here are some other lists of EV-related projects:

- [GitHub list juherr](https://github.com/stars/juherr/lists/ev)
- [GitHub list mateogreil](https://github.com/stars/mateogreil/lists/ev-mobility)
