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
#### Libraries
**C**
* [parikshittyagi/ocppClientJ1.6](https://github.com/parikshittyagi/ocppClientJ1.6) (C; OCPP 1.6; This repo helps in connecting ocppJ1.6 complaint CMS server using websockets)
* [pazzk-labs/ocpp](https://github.com/pazzk-labs/ocpp) (C; OCPP client implementation in C)
* [tux-evse/afb-ocpp-ext](https://github.com/tux-evse/afb-ocpp-ext) (C; OCPP 1.6; AFB micro-service framework extention for OCPP 1.6 + 2.0.1)

**C++**
* [ChargeLab/OpenOCPP](https://github.com/ChargeLab/OpenOCPP) (C++; OCPP 1.6; Multi-platform OCPP 1.6/2.0.1 embedded software for charging stations)
* [EVerest/libocpp](https://github.com/EVerest/libocpp) (C++; OCPP 1.6, OCPP 2.0.1, OCPP 2.1; C++ implementation of the Open Charge Point Protocol)
* [markrpo/ocppws](https://github.com/markrpo/ocppws) (C++; ocpp over websockets for C++)
* [matth-x/MicroOcpp](https://github.com/matth-x/MicroOcpp) (C++; OCPP 1.6, OCPP 2.0.1; OCPP 1.6 / 2.0.1 client for microcontrollers)
* [matth-x/ArduinoOcpp](https://github.com/matth-x/ArduinoOcpp) (C++; 1.6, 2.0.1)


**CSS**
* [agruenb/micro-ocpp-dashboard](https://github.com/agruenb/micro-ocpp-dashboard) (CSS; A web-based dashboard for the MicroOcpp library)

**Erlang**
* [wfvining/ocpp](https://github.com/wfvining/ocpp) (Erlang; Open Charge Point Protocol)
* [vampirebyte/rabbitmq-web-ocpp](https://github.com/vampirebyte/rabbitmq-web-ocpp) (Erlang; Open source native RabbitMQ OCPP plugin / gateway)

**Go**
* [CoderSergiy/ocpp16-go](https://github.com/CoderSergiy/ocpp16-go) (Go; OCPP 1.6; Open Charge Point Protocol version 1.6 implementation in Go)
* [aliml92/ocpp](https://github.com/aliml92/ocpp) (Go; OCPP 1.6, OCPP 2.0.1; Golang implementation of the Open Charge Point Protocol (OCPP).)
* [gregszalay/ocpp-messages-go](https://github.com/gregszalay/ocpp-messages-go) (Go; OCPP 2.0.1; Go data types for OCPP 2.0.1 Messages)
* [lorenzodonini/ocpp-go](https://github.com/lorenzodonini/ocpp-go) (Go; 1.6, 2.0.1)
* [voltbras/go-ocpp](https://github.com/voltbras/go-ocpp) (Go; 1.5 SOAP, 1.6 JSON)
* [ChargePi/ocpp-manager](https://github.com/ChargePi/ocpp-manager) (1.6, 2.0.1 planned)

**Python**
* [mobilityhouse/ocpp](https://github.com/mobilityhouse/ocpp) (1.6, 2.0.1)


**Java**
* [ChargeTimeEU/Java-OCA-OCPP](https://github.com/ChargeTimeEU/Java-OCA-OCPP) (Java; Open source client and server library of Open Charge-Point Protocol (OCPP) defined by openchargealliance.org (OCA))
* [Llocer/llocer_ocpp](https://github.com/Llocer/llocer_ocpp) (Java; OCPP 2.0.1; openEV OCPP 2.0.1 implementation)
* [steve-community/ocpp-jaxb](https://github.com/steve-community/ocpp-jaxb) (Java; 1.2, 1.5, 1.6 SOAP & JSON, 2.0.1 JSON)


**JavaScript**
* [ZeMorfe/nodejs_ocpp16_client](https://github.com/ZeMorfe/nodejs_ocpp16_client) (JavaScript; OCPP 1.1.1, OCPP 1.6; NodeJS client for OCPP 1.6 JSON)
* [aymen-mouelhi/ocpp-js](https://github.com/aymen-mouelhi/ocpp-js) (JavaScript; Open Charge Point Protocol Implementation in JS)
* [mikuso/ocpp-rpc](https://github.com/mikuso/ocpp-rpc) (1.6, 2.0.1, 2.1)


**Kotlin**
* [IZIVIA/ocpp-toolkit](https://github.com/IZIVIA/ocpp-toolkit) (Kotlin; OCPP 1.5, OCPP 1.6, OCPP 2.0; a Kotlin library to perform OCPP operations)
* [monta-app/library-ocpp](https://github.com/monta-app/library-ocpp) (Kotlin; Monta's OCPP Library built using Kotlin)

**PHP**
* [DeltaVetal26/SteVe-OCPP-HTTP-Client](https://github.com/DeltaVetal26/SteVe-OCPP-HTTP-Client) (PHP; Basic HTTP client for sending commands remotely to the Steve OCPP control panel)

**Rust**
* [hlsxx/ocpp-charge-point-simulator](https://github.com/hlsxx/ocpp-charge-point-simulator) (Rust; OCPP 1.6, OCPP 2.0, OCPP 2.1; Rust OCPP Charge Point Simulator)
* [choudhary463/rocpp](https://github.com/choudhary463/rocpp) (Rust; OCPP 1.6, OCPP 2.0; Rust OCPP Implementation)
* [flowionab/ocpp-client](https://github.com/flowionab/ocpp-client) (Rust; OCPP 1.6; ocpp-client is a Rust library that provides an OCPP (Open Charge Point Protocol) client implementation.)
* [tommymalmqvist/rust-ocpp](https://github.com/tommymalmqvist/rust-ocpp) (Rust; OCPP 1.6, OCPP 2.0.1, OCPP 2.1; Libraries for ocpp 1.6, 2.0.1 and 2.1)
* [tux-evse/ocpp-binding-rs](https://github.com/tux-evse/ocpp-binding-rs) (Rust; OCPP Rust afb binding)
* [codelabsab/rust-ocpp](https://github.com/codelabsab/rust-ocpp) (1.6, 2.0.1, 2.1)


**Scala**
* [IHomer/scala-ocpp](https://github.com/IHomer/scala-ocpp) (Scala; OCPP 1.5, OCPP 1.6, OCPP 2.0; The open-source Scala OCPP implementation originally developed by NewMotion)
* [ShellRechargeSolutionsEU/ocpp](https://github.com/ShellRechargeSolutionsEU/ocpp) (Scala, 1.5, 1.6, 2.0 partial)
  
**TypeScript**
* [voltbras/ts-ocpp](https://github.com/voltbras/ts-ocpp) (1.5 SOAP, 1.6 JSON)
* [ChilG/zod-ocpp](https://github.com/ChilG/zod-ocpp) (TypeScript; OCPP 1.6)
* [connected-hil/ocpp-tools](https://github.com/connected-hil/ocpp-tools) (TypeScript; OCPP 1.6, OCPP 2.0.1; Open charge point protocol tools. Schema validation, Typescript types, and other helpful utilities.)
* [extrawest/ocpp-node-ts](https://github.com/extrawest/ocpp-node-ts) (TypeScript; OCPP 1.6, OCPP 2.0.1; Typescript package implementing the JSON version of the Open Charge Point Protocol (OCPP). Currently OCPP 2.0.1 is supported.)
* [gaia-charge/browser-ocpp-client](https://github.com/gaia-charge/browser-ocpp-client) (TypeScript; OCPP 1.6; 🔌 OCPP 1.6 client for browsers)
* [jacoscaz/typed-ocpp](https://github.com/jacoscaz/typed-ocpp) (TypeScript; OCPP 1.6, OCPP 2.0, OCPP 2.0.1, OCPP 2.1; A library for type-aware validation of OCPP 1.6, OCPP 2.0.1 and OCPP 2.1 messages, built against the official JSON Schema documents published by the Open Charge Alliance.)
* [node-ocpp/core](https://github.com/node-ocpp/core) (TypeScript; OCPP 1.2, OCPP 2.0.1)
* [rohittiwari-dev/ocpp-ts-rpc](https://github.com/rohittiwari-dev/ocpp-ts-rpc) (TypeScript; Revolutionize OCPP-J RPC-over-websocket in Node.js with TypeScript! Inspired by @mikuso/ocpp-rpc, this project offers a seamless, efficient solution for implementing compliant systems, ensuring rob…)
* [sepych/ocpp-ts](https://github.com/sepych/ocpp-ts) (TypeScript; OCPP 1.6; Typescript package implementing the JSON version of the Open Charge Point Protocol (OCPP).)
  
#### Misc
* [OCPP Spec](https://ocpp-spec.org/)
* [OCPP AI](https://openchargealliance.org/oca-i-chatbot/)
* [ChargeFlow CLI for debugging and validating OCPP messages](https://github.com/ChargePi/chargeflow)
* [AviranAbady/tzi-OCTT](https://github.com/AviranAbady/tzi-OCTT) (Python; Open OCTT implementation)
* [OpenChargingCloud/WWCP_OCPP](https://github.com/OpenChargingCloud/WWCP_OCPP) (C#; OCPP 1.5, OCPP 1.6, OCPP 2.0.1, OCPP 2.1; Connectivity between the World Wide Charging Protocol (WWCP) and the Open Charge Point Protocol (OCPP v1.6/v2.0.1/v2.1).)
* [OrangeTux/rauts](https://github.com/OrangeTux/rauts) (Rust; A Rust project exploring a routing mechanis for OCPP (Open Charge Point Protocol).)
* [OrangeTux/zeegat](https://github.com/OrangeTux/zeegat) (Python; Project to explore new routing system for handling OCPP messages)
* [abhishandilya/ocpp.ai](https://github.com/abhishandilya/ocpp.ai) (TypeScript; Chat with OCPP expert)
* [ampeco/cpd-ocpp](https://github.com/ampeco/cpd-ocpp) (JavaScript; OCPP 2.0; Open Charge Point Protocol)
* [argonne-vci/node-red-contrib-ocpp](https://github.com/argonne-vci/node-red-contrib-ocpp) (JavaScript; OCPP 1.5, OCPP 1.6; Open Charge Point Protocol Node-Red Nodes)
* [aws-solutions-library-samples/guidance-for-modernizing-electric-vehicle-charging-on-aws](https://github.com/aws-solutions-library-samples/guidance-for-modernizing-electric-vehicle-charging-on-aws) (TypeScript; OCPP 2.0.1; This guidance demonstrates how the OCPP Gateway acts as a proxy between OCPP and MQTT, enabling integration with AWS IoT Core and downstream CPO services built on AWS.)
* [brandonprry/VolatileOCPP](https://github.com/brandonprry/VolatileOCPP) (C#; OCPP 1.6; Security-Focused Implementation of Open Charge Alliance OCPP Test Document Scenarios)
* [elifTech/cpd-ocpp](https://github.com/elifTech/cpd-ocpp) (JavaScript; OCPP 2.0; Open Charge Point Protocol)
* [elifTech/ocpp-tester](https://github.com/elifTech/ocpp-tester) (JavaScript)
* [foxriver76/ioBroker.ocpp](https://github.com/foxriver76/ioBroker.ocpp) (TypeScript; OCPP 1.6; Adapter to connect OCPP 1.6 supported Wallbox to ioBroker.)
* [gennadiygnezdilov/ocpp-1.6J-example-request-response](https://github.com/gennadiygnezdilov/ocpp-1.6J-example-request-response) (OCPP 1.6; Example requests and responses OCPP 1.6J)
* [iclay/ocpp](https://github.com/iclay/ocpp) (Go; OCPP 1.6, OCPP 2.0)
* [psnehanshu/ocpp-task-manager](https://github.com/psnehanshu/ocpp-task-manager) (JavaScript; OCPP 1.6; A general-purpose, transport-layer agnostic framework to implement anything related to OCPP (Open Charge Point Protocol).)
* [vampirebyte/rabbitmq-web-ocpp](https://github.com/vampirebyte/rabbitmq-web-ocpp) (Erlang; RabbitMQ OCPP-J-to-AMQP adapter)
* [vorchunpaul/ocpp-gateway](https://github.com/vorchunpaul/ocpp-gateway) (Python; OCPP 2.0.1; OCPP 2.0.1 to 1.6 gateway)

#### Servers
**C#**
* [dallmann-consulting/OCPP.Core](https://github.com/dallmann-consulting/OCPP.Core) (C#; OCPP 1.6, OCPP 2.0; OCPP server and management UI written in .NET-Core)
* [digitaltwinconsortium/iot-edge-ocpp-central-system](https://github.com/digitaltwinconsortium/iot-edge-ocpp-central-system) (C#; Azure IoT Edge Module implementing the Open Charge Point Protocol (OCPP) V1.5 and V1.6 Central System)

**C++**
* [apostoldevel/ocpp-cs](https://github.com/apostoldevel/ocpp-cs) (C++; OCPP 1.6; OCPP Central System and Charge Point emulator.)

**Go**
* [Beep-Technologies/esteban-ocpp](https://github.com/Beep-Technologies/esteban-ocpp) (Go; Esteban-OCPP 🕴️⚡ - OCPP server implementation in Golang)
* [gregszalay/ocpp-csms-common-types](https://github.com/gregszalay/ocpp-csms-common-types) (Go; Common types for my custom Charging Station Management System)
* [gregszalay/ocpp-csms](https://github.com/gregszalay/ocpp-csms) (Go; OCPP 2.0.1; A modern, extendable OCPP 2.0.1. charging station management system)

**Java**
* [Llocer/llocer_cso](https://github.com/Llocer/llocer_cso) (Java; CSMS and CPO/CSO implementation using OCPI and OCPP)
* [m-villalilla/VirtualChargePoint](https://github.com/m-villalilla/VirtualChargePoint) (Java; A application to test ocpp servers, either with the GUI or with our API in your project)
* [parklapp/steve-pluggable](https://github.com/parklapp/steve-pluggable) (Java; OCPP 1.2, OCPP 1.5, OCPP 1.6; SteVe - OCPP server implementation in Java)
* [v-bodnar/ocpp-server](https://github.com/v-bodnar/ocpp-server) (Java; OCPP Server with GUI, CLI, Groovy)

**JavaScript**
* [gio-del/eMall](https://github.com/gio-del/eMall) (JavaScript; JavaScript-based project for an eMSP and CPMSs (OCPP Server))
* [zzerk/OCPP-J-Server](https://github.com/zzerk/OCPP-J-Server) (JavaScript; OCPP 1.6; A basic OCPP server written in NodeJS (based on OCPP 1.6J protocol))

**Python**
* [jagwarthegreat/EVerythingcharge](https://github.com/jagwarthegreat/EVerythingcharge) (Python; OCPP management system for the charge points operators (CPO's). Supports 1.6 and 2.0.1 OCPP versions.)
* [slachiewicz/ocpp-csms-backend](https://github.com/slachiewicz/ocpp-csms-backend) (Python; The Python app for monitoring and controlling electric vehicle chargers.)

**Rust**
* [FlipSoftware/moovolt-csms](https://github.com/FlipSoftware/moovolt-csms) (Rust; A Universal CSMS for OCPP Protocol: An Integrated Cross-Platform and Cross-Vendor Solution for Electric Vehicle Chargers)
* [alexs-sh/dummy-central-system](https://github.com/alexs-sh/dummy-central-system) (Rust; Dummy OCPP Central System)
* [codelabsab/ocpp-csms-server](https://github.com/codelabsab/ocpp-csms-server) (Rust; OCPP 2.0.1; OCPP v2.0.1 Websockets Server)

**Shell**
* [tux-evse/ocpp-csms](https://github.com/tux-evse/ocpp-csms) (Shell; Podman config for an ocpp-csms based on maeve-csms)

**TypeScript**
* [gregszalay/ocpp-csms-frontend](https://github.com/gregszalay/ocpp-csms-frontend) (TypeScript)
* [siddharth1729/ocpp](https://github.com/siddharth1729/ocpp) (TypeScript; OCPP 2.6; OCPP server in Typescript)

#### Simulators
**C++**
* [c-jimenez/open-ocpp-simu](https://github.com/c-jimenez/open-ocpp-simu) (C++; Charge Point simulator based on Open OCPP library)
* [matth-x/MicroOcppSimulator](https://github.com/matth-x/MicroOcppSimulator) (C++)

**Clojure**
* [chargegrid/abusive-charge-point](https://github.com/chargegrid/abusive-charge-point) (Clojure; OCPP 1.5; A naughty OCPP 1.5j charge point (pool) simulator to test or loadtest your OCPP backoffice)

**HTML**
* [JavaIsJavaScript/OCPP-J-CP-Simulator](https://github.com/JavaIsJavaScript/OCPP-J-CP-Simulator) (HTML; OCPP 1.6; A really simple cp simulator, that works with OCPP 1.6)
* [victormunoz/OCPP-1.6-Chargebox-Simulator](https://github.com/victormunoz/OCPP-1.6-Chargebox-Simulator) (HTML; OCPP 1.6; A simple chargepoint simulator, working with OCPP 1.6)

**Java**
* [evbox/station-simulator](https://github.com/evbox/station-simulator) (Java)
* [extrawest/Charge-Point-Simulator-via-OCPP-2.0.1](https://github.com/extrawest/Charge-Point-Simulator-via-OCPP-2.0.1) (Java; OCPP 2.0, OCPP 2.0.1; This is a emulator for huge numbers of charge points, that connect to central system through web socket and implement OCPP 2.0.1)
* [yohannlog/OCPP_ChargingStation_2_0_1](https://github.com/yohannlog/OCPP_ChargingStation_2_0_1) (Java; OCPP 2.0.1; Charging Station Simulator OCPP 2.0.1 JSON)

**JavaScript**
* [JavaIsJavaScript/OCPP-1.6-CP-Simulator](https://github.com/JavaIsJavaScript/OCPP-1.6-CP-Simulator) (JavaScript; OCPP 1.6; Hacky but it works for testing purposes)
* [JavaIsJavaScript/OCPP-2.0-CP-Simulator](https://github.com/JavaIsJavaScript/OCPP-2.0-CP-Simulator) (JavaScript, 2.0)
* [Lamerat/OCPP-Charge-Point-Simulator](https://github.com/Lamerat/OCPP-Charge-Point-Simulator) (JavaScript; Charge Point Simulator OCPP JSON-1.6)
* [wirelane/ocpp-client-simulator](https://github.com/wirelane/ocpp-client-simulator) (JavaScript; OCPP 1.6; A simple Node.JS script simulating a OCPP 1.6 compatible Charging Station)
* [kubarskii/OCPP-J-CP-Simulator](https://github.com/kubarskii/OCPP-J-CP-Simulator) (JavaScript, 1.6)

**Kotlin**
* [monta-app/ocpp-emulator](https://github.com/monta-app/ocpp-emulator) (Kotlin; OCPP 1.6, OCPP 2.0.1; An open source OCPP Charge Point Emulator built using Kotlin Multiplatform and Jetbrains Compose)

**Less**
* [road-labs/chargestation-one](https://github.com/road-labs/chargestation-one) (Less; OCPP 1.6, OCPP 2.0.1, OCPP 2.1; Charging station OCPP based simulator with support for OCPP 1.6 and OCPP 2.0.1)

**Python**
* [TECHS-Technological-Solutions/ocpp-simulator](https://github.com/TECHS-Technological-Solutions/ocpp-simulator) (Python)
* [virta-ltd/charge-device-simulator](https://github.com/virta-ltd/charge-device-simulator) (Python; Easy to use device simulators for different protocols like OCPP and Ensto)

**Ruby**
* [glurp/ocpp_simulator](https://github.com/glurp/ocpp_simulator) (Ruby; Simulation of a electrical Charge Point via OCPP protocol)

**Rust**
* [hlsxx/ocpp-charge-point-simulator](https://github.com/hlsxx/ocpp-charge-point-simulator) (Rust; Simple CLI OCPP charge point simulator)
* [romfrolov/station-emulator](https://github.com/romfrolov/station-emulator) (Rust; OCPP 2.0; EV charging station emulator (OCPP 2.0))

**Scala**
* [ShellRechargeSolutionsEU/docile-charge-point](https://github.com/ShellRechargeSolutionsEU/docile-charge-point) (Scala; OCPP 1.5, OCPP 1.6, OCPP 2.0; Scriptable OCPP charge point simulator and test tool)
* [ShellRechargeSolutionsEU/ocpp-charger](https://github.com/ShellRechargeSolutionsEU/ocpp-charger) (Scala; Simple ocpp charger simulator)

**TypeScript**
* [OpenChargingCloud/ChargingStationApp](https://github.com/OpenChargingCloud/ChargingStationApp) (TypeScript; OCPP 1.6, OCPP 2.0.1, OCPP 2.1; A virtual charging station for testing implementing e.g. the Open Charge Point Protocol (OCPP v1.6/v2.0.1/v2.1).)
* [SAP/e-mobility-charging-stations-simulator](https://github.com/SAP/e-mobility-charging-stations-simulator) (TypeScript; OCPP 1.6; OCPP-J charging stations simulator)
* [oglimmer/scriptable-ocpp-chargepoint-simulator](https://github.com/oglimmer/scriptable-ocpp-chargepoint-simulator) (TypeScript; OCPP 1.6; A Scriptable OCPP Chargepoint Simulator for OCPP 1.6J. Client and Server.)
* [shiv3/ocpp-cp-simulator](https://github.com/shiv3/ocpp-cp-simulator) (TypeScript; OCPP 1.6; simple standalone ocpp charging port simulator written in reactjs, its based on OCPP 1.6J protocol)
* [solidstudiosh/ocpp-virtual-charge-point](https://github.com/solidstudiosh/ocpp-virtual-charge-point) (TypeScript; OCPP 1.6, OCPP 2.0.1; Simple, configurable, terminal-based OCPP Charging Station simulator written in Node.js with Schema validation)
* [vasyas/charger-simulator](https://github.com/vasyas/charger-simulator) (TypeScript, 1.5 SOAP, 1.6 JSON)

### ISO 15118
#### Plug & Charge
* [OPNC](https://github.com/charinev/opnc)
* [OPCP](https://github.com/hubject/opcp)
  
#### Misc
* [sniffer-iso15118vse](https://github.com/endland/sniffer-iso15118vse)
* [EVerest/libiso15118](https://github.com/EVerest/libiso15118) (C++; ISO 15118 library suite)
* [EcoG-io/iso15118](https://github.com/EcoG-io/iso15118) (Python; Implementation of the ISO 15118 Communication Protocol (-2, -20, -8))
* [FlUxIuS/V2GInjector](https://github.com/FlUxIuS/V2GInjector) (Python; V2GInjector - Tool to intrude a V2G PowerLine network, but also to capture and inject V2G packets)
* [SwitchEV/RISE-V2G](https://github.com/SwitchEV/RISE-V2G) (Java; The only fully-featured reference implementation of the Vehicle-2-Grid communication interface ISO 15118)
* [uhi22/pyPLC](https://github.com/uhi22/pyPLC) (Python; Electric vehicle CCS charging investigations with Python)

### OCPI
#### Libraries
**C#**
* [BitzArt/OCPI.Net](https://github.com/BitzArt/OCPI.Net) (C#; OCPI implementation for .Net)
* [kraftvaerk/OCPI](https://github.com/kraftvaerk/OCPI) (C#; Framework for the Open Charge Point Interface (OCPI))

**HTML**
* [gaia-charge/ocpi-types](https://github.com/gaia-charge/ocpi-types) (HTML; 🔣 Auto-generated OCPI type definitions for multiple languages)

**Java**
* [Llocer/llocer_ocpi](https://github.com/Llocer/llocer_ocpi) (Java; OCPI 2.2.1; openEV OCPI 2.2.1 implementation)
* [extrawest/Extrawest-OCPI-2.2.1-CPO-Client](https://github.com/extrawest/Extrawest-OCPI-2.2.1-CPO-Client) (Java; Client library for Open Charge-Point Protocol CPO Server from extrawest.com)
* [extrawest/Extrawest-OCPI-2.2.1-CPO-Server](https://github.com/extrawest/Extrawest-OCPI-2.2.1-CPO-Server) (Java; OCPI 2.1.1, OCPI 2.2, OCPI 2.2.1; Library allows to implement CPO's application following OCPI-2.2.1 Specification by reusing pre-created models, controllers etc.)
* [extrawest/Extrawest-OCPI-2.2.1-EMSP-Server](https://github.com/extrawest/Extrawest-OCPI-2.2.1-EMSP-Server) (Java; OCPI 2.1.1, OCPI 2.2, OCPI 2.2.1; Library allows to implement eMSP's application following OCPI-2.2.1 Specification by reusing pre-created models, controllers etc.)

**Python**
* [extrawest/extrawest_ocpi](https://github.com/extrawest/extrawest_ocpi) (Python; Python implementation of Open Charge Point Interface (OCPI) protocol based on fastapi.)
* [TECHS-Technological-Solutions/ocpi](https://github.com/TECHS-Technological-Solutions/ocpi) (2.2.1)
* [NOWUM/pyOCPI](https://github.com/NOWUM/pyOCPI) (2.2)
  
**Go**
* [ChargePi/ocpi-sdk-go](https://github.com/ChargePi/ocpi-sdk-go) (2.2.1)

**Kotlin**
* [izivia/ocpi-toolkit](https://github.com/IZIVIA/ocpi-toolkit) (2.2.1)

**Scala**
* [ShellRechargeSolutionsEU/ocpi-endpoints](https://github.com/ShellRechargeSolutionsEU/ocpi-endpoints) (2.1.1, archived)

**PHP**
* [ChargeMap/ocpi-protocol](https://github.com/ChargeMap/ocpi-protocol) (2.1.1, archived)

**TypeScript**
* [gaia-green-tech/ocpi-types](https://github.com/gaia-green-tech/ocpi-types) (2.1.1, 2.2)
* [solidstudiosh/ocpi-schema](https://github.com/solidstudiosh/ocpi-schema) (2.1.1, 2.2, 2.2.1)
* [andreibesleaga/ocpi-sdk](https://github.com/andreibesleaga/ocpi-sdk) (OCPI SDK & MCP Server)

#### Misc
* [CNX-GIREVE/GIREVE_Tech_OCPI_V2.1.1](https://github.com/CNX-GIREVE/GIREVE_Tech_OCPI_V2.1.1) (OCPI 2.1.1; IOP – OCPI 2.1.1 Interface - GIREVE Implementation Guide)
* [CNX-GIREVE/GIREVE_Tech_OCPI_V2.2.1](https://github.com/CNX-GIREVE/GIREVE_Tech_OCPI_V2.2.1) (OCPI 2.2.1; IOP – OCPI 2.2.1 Interface - GIREVE Implementation Guide)
* [MTES-MCT/ocpi-playground](https://github.com/MTES-MCT/ocpi-playground) (Python; A playground to test OCPI-based infrastructures)
* [OpenChargingCloud/OCPIExplorerDesktopApp](https://github.com/OpenChargingCloud/OCPIExplorerDesktopApp) (TypeScript; OCPI 2.1, OCPI 2.1.1, OCPI 2.2, OCPI 2.2.1, OCPI 2.3.0, OCPI 3.0; An OCPI Explorer as an Electron Desktop App)
* [OpenChargingCloud/OCPIExplorerWebApp](https://github.com/OpenChargingCloud/OCPIExplorerWebApp) (TypeScript; OCPI 2.1, OCPI 2.1.1, OCPI 2.2.1, OCPI 2.3.0, OCPI 3.0; An OCPI Explorer as a Web App)
* [OpenChargingCloud/WWCP_OCPI](https://github.com/OpenChargingCloud/WWCP_OCPI) (C#; OCPI 2.0, OCPI 2.1, OCPI 2.1.1, OCPI 2.2, OCPI 2.2.1, OCPI 2.3, OCPI 3.0; Communication between the World Wide Charging Protocol (WWCP) and the Open Charge Point Interface (OCPI v2.1.1, v2.2.1, v2.3.0, v3.0).)
* [chargeprice/chargeprice-api-docs](https://github.com/chargeprice/chargeprice-api-docs) (Documentation for 3rd party applications to communicate with the Chargeprice API.)
* [citrineos/citrineos-ocpi](https://github.com/citrineos/citrineos-ocpi) (TypeScript; OCPI 2.2.1, OCPP 2.0.1; Support for OCPI built on top of core CitrineOS)
* [hyndex/OCPIPyBridge](https://github.com/hyndex/OCPIPyBridge) (Python)
* [kelseymok/ocpi-implementation](https://github.com/kelseymok/ocpi-implementation) (Python)
* [ocpi/ocpi-tool](https://github.com/ocpi/ocpi-tool) (TypeScript; OCPI 2.2.1; A tool for exporting data from OCPI platforms)
* [plugoinc/ocpi-openapi](https://github.com/plugoinc/ocpi-openapi) (OCPI definision using OpenAPI)
* [tandemdrive/ocpi-tariffs](https://github.com/tandemdrive/ocpi-tariffs) (OCPI tariff calculations)

### OICP
#### Libraries

**Go**
* [ChargePi/oicp-sdk-go](https://github.com/ChargePi/oicp-sdk-go) (Go, 2.2, 2.3)

### Eichrecht
* [transparenzsoftware](https://github.com/SAFE-eV/transparenzsoftware)

### Misc Roaming Protocols Libraries
* [andreibesleaga/oscp-sdk](https://github.com/andreibesleaga/oscp-sdk) (TypeScript; OSCP SDK & MCP Server)
* [andreibesleaga/ohcp-mcp](https://github.com/andreibesleaga/ohcp-mcp) (TypeScript; OHCP MCP Server)

### Charging Station Management Systems (CSMS)
* [steve-community/steve](https://github.com/steve-community/steve) (Java, 1.2S, 1.2J, 1.5S, 1.5J, 1.6S, 1.6J)
* [juherr/evolve](https://github.com/juherr/evolve) (Java, 1.2S, 1.2J, 1.5S, 1.5J, 1.6S, 1.6J)
* [thoughtworks/maeve-csms](https://github.com/thoughtworks/maeve-csms) (Go, OCPP 1.6j, 2.0.1, ISO 15118)
* [citrineos/citrineos-core](https://github.com/citrineos/citrineos-core) ([doc](https://github.com/citrineos/citrineos)) (TypeScript/Node.js, OCPP 2.0.1)
* [EVerest/everest-core](https://github.com/EVerest/everest-core) (C++/Python/Rust, OCPP 1.6, 2.0.1, ISO 15118)
* [lbbrhzn/ocpp](https://github.com/lbbrhzn/ocpp) (Python/Home Assistant, 1.6J, 2.0.1, 2.1 experimental)
* [argonne-national-laboratory/node-red-contrib-ocpp](https://github.com/argonne-national-laboratory/node-red-contrib-ocpp) (Node-RED/Node.js, 1.5S, 1.6S, 1.6J)
* [Anmirazik/Open-Source-Ev-charger-End-to-End-Solution](https://github.com/Anmirazik/Open-Source-Ev-charger-End-to-End-Solution) (Step by step on how to integrate Everest based EV Charger with CSMS such as Steve , Open E-Mobility , CitrineOS and many more Open Source CSMS. Please change to different branches for different CSMS)

### Charging Station Projects
* [EVerest/EVerest](https://github.com/EVerest/EVerest) (Dockerfile; Main Repository of EVerest - an EV charging software stack. All main documentations and issues are stored here.)
* [OpenEVSE/openevse_esp32_firmware](https://github.com/OpenEVSE/openevse_esp32_firmware) (C; OpenEVSE V4 WiFi gateway using ESP32)
* [SmartEVSE/SmartEVSE-3](https://github.com/SmartEVSE/SmartEVSE-3) (C; Smart Electric Vehicle Charging Station (EVSE))
* [SolarNetwork/solarnetwork-central](https://github.com/SolarNetwork/solarnetwork-central) (Java; Centralized SolarNet service for SolarNetwork)
* [digitaltwinconsortium/OCPP-Charging-Dashboard](https://github.com/digitaltwinconsortium/OCPP-Charging-Dashboard) (JavaScript; A dockerized web app for displaying Electric Vehicle charging station status, following the OCPP standard data model.)
* [dzurikmiroslav/esp32-evse](https://github.com/dzurikmiroslav/esp32-evse) (C; ESP32 EVSE firmware)
* [ev-map/EVMap](https://github.com/ev-map/EVMap) (Kotlin; Android app to find electric vehicle charging stations - compatible with community databases such as GoingElectric.de and OpenChargeMap.org.)
* [evcc-io/evcc](https://github.com/evcc-io/evcc) (Go; solar charging ☀️🚘)
* [gregszalay/ocpp-charging-station](https://github.com/gregszalay/ocpp-charging-station) (C++; OCPP 2.0.1; Charging Station firmware for electric vehicles - OCPP 2.0.1. compliant)
* [leeyuentuen/alfen_wallbox](https://github.com/leeyuentuen/alfen_wallbox) (Python; Alfen wallbox - Home Assistant Component)
* [morosanag/OCPP-Project](https://github.com/morosanag/OCPP-Project) (Java; Management system for electrical charging stations)
* [motown-io/motown](https://github.com/motown-io/motown) (Java; The heart and soul of electric mobility)
* [sap-labs-france/ev-dashboard](https://github.com/sap-labs-france/ev-dashboard) (TypeScript; The Open e-Mobility Charging Station management front-end Angular application (check also ev-server and ev-mobile))
* [sap-labs-france/ev-server](https://github.com/sap-labs-france/ev-server) (TypeScript; The Open e-Mobility Charging Station management backend server (check also ev-dashboard and ev-mobile))
* [thepaulcooper/victron-openEVSE](https://github.com/thepaulcooper/victron-openEVSE) (openEVSE controller for Victron PV / battery system)

### OCMF
* [SAFE-eV/OCMF-Open-Charge-Metering-Format](https://github.com/SAFE-eV/OCMF-Open-Charge-Metering-Format)
* [SAFE-eV/transparenzsoftware](https://github.com/SAFE-eV/transparenzsoftware)
* [ChargePi/ocmf-go](https://github.com/ChargePi/ocmf-go) (Go; OCMF Go SDK)
* [Namoshek/OpenChargeMeteringFormat](https://github.com/Namoshek/OpenChargeMeteringFormat) (C#; A .NET implementation of the Open Charge Metering Format (OCMF).)
* [road-labs/ocmf-js](https://github.com/road-labs/ocmf-js) (TypeScript; TypeScript/JavaScript implementation of the Open Charge Metering Format (OCMF) specification)

### OCM - Open Charge Map
* [openchargemap](https://github.com/openchargemap) (Official OCM GitHub)
* [openchargemap/ocm-data](https://github.com/openchargemap/ocm-data) (Shell; Snapshots of current Open Charge Map data [deprecated])
* [andreibesleaga/ocm-sdk](https://github.com/andreibesleaga/ocm-sdk) (TypeScript; OCM SDK & MCP Server)
* [andreibesleaga/ocm-php](https://github.com/andreibesleaga/ocm-php) (PHP; OCM SDK)

### OCN (Open Charging Network)
* [energywebfoundation/ocn-bridge](https://github.com/energywebfoundation/ocn-bridge) (TypeScript; Open Charging Network Bridge (mirror of https://bitbucket.org/shareandcharge/ocn-bridge).)
* [energywebfoundation/ocn-node](https://github.com/energywebfoundation/ocn-node) (Kotlin; OCPI 2.2)
* [energywebfoundation/ocn-registry](https://github.com/energywebfoundation/ocn-registry) (Java; OCPI 2.2)
* [energywebfoundation/ocn-tools](https://github.com/energywebfoundation/ocn-tools) (TypeScript; Contains common tools for aiding development of applications built on top of the OCN. It is possible to run a mock E-Mobility Service Provider (MSP) or Charge Point Operator (CPO) with these tools.)
* [olisystems/ocn-node-v2](https://github.com/olisystems/ocn-node-v2) (Kotlin; OCPI 2.2; Second version of Ocn Node orginally forked from https://github.com/energywebfoundation/ocn-node)
* [olisystems/ocn-registry-v2.0](https://github.com/olisystems/ocn-registry-v2.0) (TypeScript; The second version of OCN smart contracts and CLI based on https://github.com/energywebfoundation/ocn-registry)

### Battery
* [dalathegreat/Battery-Emulator](https://github.com/dalathegreat/Battery-Emulator) (C++; This revolutionary software enables EV battery packs to be easily reused for stationary storage in combination with solar inverters)
* [mnh-jansson/open-battery-information](https://github.com/mnh-jansson/open-battery-information) (C++)

## Contributing

Contributions are welcome! If you know of a tool or resource that is not on the list, please feel free to add it.

The easiest way to contribute is to [open an issue](https://github.com/juherr/awesome-ev/issues/new/choose) using the "Add a link" template.

You can also submit a pull request. Please try to follow the existing format.

---

## Other Resources

Here are some other lists of EV-related projects:

- [GitHub list juherr](https://github.com/stars/juherr/lists/ev)
- [GitHub list mateogreil](https://github.com/stars/mateogreil/lists/ev-mobility)
