# Legacy & pending EV charging projects

Projects kept out of the main [README](README.md) list — which only features actively maintained, curated tools — but preserved here for reference: dormant, archived, or deprecated projects, plus candidates still awaiting curation.

## Dormant (125)

### OCPP

#### Server

- [thoughtworks/maeve-csms](https://github.com/thoughtworks/maeve-csms) - MaEVe is an experimental Go-based EV charge station management system that accepts OCPP 1.6j/2.0.1 charge station connections and integrates with Hubject for ISO 15118 Plug and Charge (OCPP 1.6, 2.0.1 · Go · ⭐ 120 · 💤 2024-08-01).
- [sap-labs-france/ev-server](https://github.com/sap-labs-france/ev-server) - A Node.js backend server for managing EV charging stations, storing OCPP data in MongoDB, exposing REST APIs, and supporting operations such as remote control, smart charging, billing, roaming, and analytics (TypeScript · ⭐ 176 · 💤 2024-08-07).
- [aws-solutions-library-samples/guidance-for-modernizing-electric-vehicle-charging-on-aws](https://github.com/aws-solutions-library-samples/guidance-for-modernizing-electric-vehicle-charging-on-aws) - AWS guidance for deploying an OCPP Gateway that proxies charge point WebSocket traffic to MQTT via AWS IoT Core for a serverless CPO/CSMS architecture (OCPP 2.0, 2.0.1 · TypeScript · ⭐ 93 · 💤 2025-02-28).
- [sap-labs-france/ev-dashboard](https://github.com/sap-labs-france/ev-dashboard) - Angular dashboard frontend for Open e-Mobility that connects to ev-server to monitor, manage, remotely control, bill, and analyze EV charging stations and related assets (TypeScript · ⭐ 78 · 💤 2024-08-02).
- [gregszalay/ocpp-csms](https://github.com/gregszalay/ocpp-csms) - A microservice-based OCPP 2.0.1 charging station management system with WebSocket communication, selected OCPP message handling, REST management APIs, and GCP Pub/Sub/Firestore integration (OCPP 2.0.1 · Go · ⭐ 59 · 💤 2023-02-11).
- [digitaltwinconsortium/iot-edge-ocpp-central-system](https://github.com/digitaltwinconsortium/iot-edge-ocpp-central-system) - Azure IoT Edge Docker module implementing an OCPP 1.5/1.6 Central System server that communicates with charge points and publishes telemetry to MQTT/Azure IoT Hub (C# · ⭐ 27 · 💤 2025-05-09).
- [v-bodnar/ocpp-server](https://github.com/v-bodnar/ocpp-server) - Java 11 OCPP server application with GUI and CLI modes, SSL/TLS support, REST control API, and runtime behavior customization via Groovy scripts (Java · ⭐ 24 · 💤 2021-11-20).
- [codelabsab/ocpp-csms-server](https://github.com/codelabsab/ocpp-csms-server) - Archived OCPP 2.0.1 WebSocket server implementation for CSMS use (OCPP 2.0.1 · Rust · ⭐ 20 · 💤 2024-08-29).
- [foxriver76/ioBroker.ocpp](https://github.com/foxriver76/ioBroker.ocpp) - IoBroker.ocpp is an ioBroker adapter for connecting and controlling OCPP 1.6-compatible wallboxes (OCPP 1.6 · TypeScript · ⭐ 20 · 💤 2023-02-09).
- [ChagataiDuru/OCPP-Framework](https://github.com/ChagataiDuru/OCPP-Framework) - A NestJS-based OCPP charge station management system with microservices for charge point communication, event processing, MongoDB storage, and an AngularJS monitoring frontend (TypeScript · ⭐ 13 · 💤 2024-01-25).
- [gio-del/eMall](https://github.com/gio-del/eMall) - EMall is a JavaScript web application for EV drivers and charging point operators to find, book, monitor, and manage charging points, including OCPP communication with chargers (JavaScript · ⭐ 11 · 💤 2023-06-06).
- [morosanag/OCPP-Project](https://github.com/morosanag/OCPP-Project) - OCPP-Project is a management system for EV charging stations with WebSocket and SOAP interfaces, business logic, and database persistence for administrator control (Java · ⭐ 10 · 💤 2017-03-19).
- [elifTech/ocpp-tester](https://github.com/elifTech/ocpp-tester) - A hosted OCPP dashboard/server endpoint for connecting charging points by charge point ID (JavaScript · ⭐ 7 · 💤 2019-05-22).
- [jagwarthegreat/EVerythingcharge](https://github.com/jagwarthegreat/EVerythingcharge) - OCPP management system for CPOs that manages OCPP 1.6 and 2.0.1 charge point connections through scalable API, worker, RabbitMQ, and PostgreSQL services (⭐ 6 · 💤 2024-03-21).
- [Llocer/llocer_cso](https://github.com/Llocer/llocer_cso) - Llocer_cso is a Charging Station Management System and CPO/CSO implementation that manages EVSEs via OCPP and optionally connects to eMSPs via OCPI (Java · ⭐ 5 · 💤 2022-05-01).
- [siddharthsabron/ocpp](https://github.com/siddharthsabron/ocpp) - TypeScript Node.js WebSocket server for communicating with OCPP-compatible EV charging stations (TypeScript · ⭐ 5 · 💤 2024-04-18).
- [ocpp-balanz/balanz](https://github.com/ocpp-balanz/balanz) - Balanz is a CSMS or local controller OCPP server with smart charging capabilities (Python · ⭐ 5 · 💤 2025-07-01).
- [zzerk/OCPP-J-Server](https://github.com/zzerk/OCPP-J-Server) - A basic Node.js server implementation for the OCPP 1.6J protocol (OCPP 1.6 · JavaScript · ⭐ 5 · 💤 2022-02-12).
- [gregszalay/ocpp-csms-frontend](https://github.com/gregszalay/ocpp-csms-frontend) - A frontend for an OCPP charging station management system currently under development (TypeScript · ⭐ 4 · 💤 2022-10-10).
- [tux-evse/ocpp-csms](https://github.com/tux-evse/ocpp-csms) - Podman configuration and scripts for running and testing a Maeve-based OCPP CSMS with a simple OCPP 1.6 client (OCPP 1.6 · Shell · ⭐ 3 · 💤 2023-10-17).

#### Simulator

- [kubarskii/OCPP-J-CP-Simulator](https://github.com/kubarskii/OCPP-J-CP-Simulator) - A simple charge point simulator for OCPP 1.6 with basic core features and a prototype UI (OCPP 1.6 · HTML · ⭐ 99 · 💤 2020-04-08).
- [glurp/ocpp_simulator](https://github.com/glurp/ocpp_simulator) - Ocpp_simulator is a Ruby gem for simulating OCPP charge points, central-system commands, and fleets using SOAP XML templates (Ruby · ⭐ 21 · 💤 2018-06-26).
- [victormunoz/OCPP-1.6-Chargebox-Simulator](https://github.com/victormunoz/OCPP-1.6-Chargebox-Simulator) - A simple OCPP 1.6 charge point simulator that connects to a central station and sends common chargebox events (OCPP 1.6 · HTML · ⭐ 123 · 💤 2024-07-08).
- [ShellRechargeSolutionsEU/docile-charge-point](https://github.com/ShellRechargeSolutionsEU/docile-charge-point) - A Scala-based scriptable OCPP charge point simulator and test tool for running scripted charge point behavior and assertions against OCPP central systems (OCPP 1.5, 1.6, 2.0 · Scala · ⭐ 82 · 💤 2022-01-20).
- [oglimmer/scriptable-ocpp-chargepoint-simulator](https://github.com/oglimmer/scriptable-ocpp-chargepoint-simulator) - Scriptable Node.js simulator for OCPP 1.6J charge points with REST and web frontends, batch scripting, and WebSocket client/server support (OCPP 1.6 · TypeScript · ⭐ 72 · 💤 2023-05-16).
- [vasyas/charger-simulator](https://github.com/vasyas/charger-simulator) - TypeScript OCPP charging station simulator usable as a CLI or JS library, supporting OCPP-J 1.6 and OCPP-SOAP 1.5 (TypeScript · ⭐ 67 · 💤 2025-04-09).
- [JavaIsJavaScript/OCPP-2.0-CP-Simulator](https://github.com/JavaIsJavaScript/OCPP-2.0-CP-Simulator) - A simple OCPP 2.0 charge point simulator for connecting a registered charge point to a configured endpoint (OCPP 2.0 · HTML · ⭐ 65 · 💤 2024-01-02).
- [evbox/station-simulator](https://github.com/evbox/station-simulator) - OCPP Station Simulator is a Java tool and library for simulating OCPP charging stations that connect to a CSMS over WebSocket (Java · ⭐ 64 · 💤 2024-02-27).
- [JavaIsJavaScript/OCPP-1.6-CP-Simulator](https://github.com/JavaIsJavaScript/OCPP-1.6-CP-Simulator) - Node.js command-line simulator for testing OCPP 1.6 charge point and central system message flows (OCPP 1.6 · JavaScript · ⭐ 43 · 💤 2019-01-18).
- [ZeMorfe/nodejs_ocpp16_client](https://github.com/ZeMorfe/nodejs_ocpp16_client) - Node.js OCPP 1.6 JSON charge point client for testing server interactions, web UI control, and smart charging profile behavior (OCPP 1.6 · JavaScript · ⭐ 40 · 💤 2020-03-23).
- [ShellRechargeSolutionsEU/ocpp-charger](https://github.com/ShellRechargeSolutionsEU/ocpp-charger) - Actor-based OCPP charger simulator that can run standalone against a central system over SOAP or OCPP-J/WebSocket (Scala · ⭐ 38 · 💤 2021-08-17).
- [extrawest/Charge-Point-Simulator-via-OCPP-2.0.1](https://github.com/extrawest/Charge-Point-Simulator-via-OCPP-2.0.1) - A Java Dockerized simulator that emulates multiple OCPP 2.0.1 charge points over WebSocket for testing and load testing central systems (OCPP 2.0, 2.0.1 · Java · ⭐ 37 · 💤 2023-03-07).
- [romfrolov/station-emulator](https://github.com/romfrolov/station-emulator) - A Rust EV charging station emulator that connects to a CSMS over WebSocket and supports OCPP 2.0 messages such as BootNotification (OCPP 2.0 · Rust · ⭐ 18 · 💤 2023-06-21).
- [TECHS-Technological-Solutions/ocpp-simulator](https://github.com/TECHS-Technological-Solutions/ocpp-simulator) - An OCPP-based simulator for simulating an EV charge point (Python · ⭐ 17 · 💤 2022-08-29).
- [extrawest/BDD-Charge-Point-Tester-via-OCPP-J-](https://github.com/extrawest/BDD-Charge-Point-Tester-via-OCPP-J-) - Java/Spring Boot Cucumber-based OCPP 1.6J simulator and BDD test tool for exercising charge point and central system message flows (OCPP 1.6 · Java · ⭐ 15 · 💤 2023-03-17).
- [Lamerat/OCPP-Charge-Point-Simulator](https://github.com/Lamerat/OCPP-Charge-Point-Simulator) - OCPP JSON 1.6 charge point simulator implementing common charge point and central system operations (JavaScript · ⭐ 12 · 💤 2025-01-29).
- [m-villalilla/VirtualChargePoint](https://github.com/m-villalilla/VirtualChargePoint) - VirtualChargePoint is a GUI and API-based OCPP charge point simulator for testing OCPP server software (Java · ⭐ 11 · 💤 2018-07-14).
- [yohannlog/OCPP_ChargingStation_2_0_1](https://github.com/yohannlog/OCPP_ChargingStation_2_0_1) - A JavaFX charging station simulator for testing OCPP 2.0.1 JSON server implementations without a physical charger (Java · ⭐ 7 · 💤 2022-05-20).
- [ocpp-balanz/ocppsim](https://github.com/ocpp-balanz/ocppsim) - OCPP v1.6 charge point simulator for testing central systems via WebSocket control and scripted charger behavior (OCPP 1.6 · Python · ⭐ 6 · 💤 2025-06-16).
- [chargegrid/abusive-charge-point](https://github.com/chargegrid/abusive-charge-point) - Abusive Charge Point is an OCPP 1.5j charge point pool simulator that sends randomized charge point messages for testing or load testing an OCPP back office (OCPP 1.5 · Clojure · ⭐ 6 · 💤 2017-08-02).
- [alexs-sh/dummy-central-system](https://github.com/alexs-sh/dummy-central-system) - A Rust dummy OCPP central system that emulates a charging station operator backend handling basic OCPP messages and certificate signing flows (Rust · ⭐ 4 · 💤 2021-08-11).
- [elumobility/elu-twins](https://github.com/elumobility/elu-twins) - ELU Twins is an e-mobility simulation toolkit for creating virtual OCPP charge points, vehicles, and test CSMS interactions (OCPP 1.6, 2.0.1 · Python · ⭐ 4 · 💤 2024-09-12).
- [esiebert/v16-fcs](https://github.com/esiebert/v16-fcs) - Fake Charging Station is a Python OCPP 1.6 charging station simulator with an API for controlling charger behavior and testing CSMS edge cases (Python · ⭐ 3 · 💤 2025-06-23).
- [elton-saraci/ocpp-charge-point-simulator](https://github.com/elton-saraci/ocpp-charge-point-simulator) - A Java Spring Boot OCPP charge point simulator that connects to a configured central system and exposes local API documentation (OCPP 1.6 · Java · ⭐ 3 · 💤 2025-04-30).
- [JavaIsJavaScript/OCPP-J-CP-Simulator](https://github.com/JavaIsJavaScript/OCPP-J-CP-Simulator) - OCPP-J-CP-Simulator is a simple charge point simulator for registering and testing against an OCPP 1.6 endpoint (OCPP 1.6 · HTML · ⭐ 2 · 💤 2018-05-14).
- [ges0909/ocpp-charge-point-simulator-dashboard](https://github.com/ges0909/ocpp-charge-point-simulator-dashboard) - A Deno, Vue, and Vuetify dashboard project for simulating an OCPP charge point (TypeScript · ⭐ 1 · 💤 2024-11-03).

#### Libraries

##### C

- [parikshittyagi/ocppClientJ1.6](https://github.com/parikshittyagi/ocppClientJ1.6) - A C OCPP 1.6J WebSocket client that connects a charge point to a CMS server and supports basic BootNotification messaging plus OCPP frame parsing and creation (OCPP 1.6 · ⭐ 53 · 💤 2020-05-17).

##### C++

- [EVerest/libocpp](https://github.com/EVerest/libocpp) - Libocpp is an archived C++ library implementing OCPP 1.6, 2.0.1, and 2.1 for integration with charging station firmware (OCPP 1.6, 2.0.1, 2.1 · ⭐ 151 · 💤 2026-04-27).

##### Erlang

- [wfvining/ocpp](https://github.com/wfvining/ocpp) - Erlang OTP library implementing the OCPP 2.0.1 protocol layer for CSMS applications, handling station communication semantics and compliance support (⭐ 11 · 💤 2025-02-24).

##### Go

- [iclay/ocpp](https://github.com/iclay/ocpp) - Go network communication library implementing OCPP 1.6 for charger-to-central-system communication with plugin-based active and passive handlers (OCPP 1.6, 2.0 · ⭐ 79 · 💤 2022-06-23).
- [voltbras/go-ocpp](https://github.com/voltbras/go-ocpp) - A Go implementation of OCPP 1.5 SOAP and OCPP 1.6 JSON for building central system and charge point clients (OCPP 1.5, 1.6 · ⭐ 49 · 💤 2022-02-16).
- [gregszalay/ocpp-csms-common-types](https://github.com/gregszalay/ocpp-csms-common-types) - Common type definitions for a custom OCPP-based Charging Station Management System (⭐ 5 · 💤 2022-10-14).
- [CoderSergiy/ocpp16-go](https://github.com/CoderSergiy/ocpp16-go) - Go library implementing OCPP 1.6 JSON communication messages with a small central system example (OCPP 1.6 · ⭐ 4 · 💤 2022-08-04).
- [gregszalay/ocpp-messages-go](https://github.com/gregszalay/ocpp-messages-go) - Go data types for OCPP 2.0.1 message wrappers and payloads generated from JSON schemas (OCPP 2.0.1 · ⭐ 3 · 💤 2024-10-13).

##### Java

- [Llocer/llocer_ocpp](https://github.com/Llocer/llocer_ocpp) - OpenEV llocer_ocpp is a base library for implementing an OCPP 2.0.1 server (⭐ 6 · 💤 2022-04-18).

##### JavaScript

- [elifTech/cpd-ocpp](https://github.com/elifTech/cpd-ocpp) - JavaScript library providing an abstraction layer, client/server helpers, and request validation for OCPP 1.6 JSON (OCPP 2.0 · ⭐ 67 · 💤 2022-12-06).
- [aymen-mouelhi/ocpp-js](https://github.com/aymen-mouelhi/ocpp-js) - JavaScript implementation of OCPP for creating a central system, charge point clients, and a charge point server with configurable storage (⭐ 61 · 💤 2021-08-09).
- [psnehanshu/ocpp-task-manager](https://github.com/psnehanshu/ocpp-task-manager) - A transport-agnostic Node.js framework for handling OCPP messages to build charge point software, simulators, backends, or CSMS (OCPP 1.6 · ⭐ 12 · 💤 2023-12-23).
- [ampeco/cpd-ocpp](https://github.com/ampeco/cpd-ocpp) - JavaScript library providing OCPP 1.6 JSON client/server abstractions and request/response validation (OCPP 2.0 · ⭐ 3 · 💤 2024-01-29).

##### Python

- [villekr/ocpp-asgi](https://github.com/villekr/ocpp-asgi) - Ocpp-asgi is a Python library that extends mobilityhouse/ocpp with an ASGI interface for building event-driven OCPP Central System backends over WebSocket and HTTP (OCPP 2.0.1 · ⭐ 23 · 💤 2022-12-23).
- [OrangeTux/zeegat](https://github.com/OrangeTux/zeegat) - Zeegat is a Python prototype for routing and composing handlers for OCPP messages using a Service-style interface (⭐ 5 · 💤 2022-06-26).

##### Rust

- [choudhary463/rocpp](https://github.com/choudhary463/rocpp) - ROCPP is a modular Rust implementation of OCPP 1.6 with client libraries, core protocol types, a charger simulator, and conformance tests (OCPP 1.6, 2.0 · ⭐ 13 · 💤 2025-06-04).
- [flowionab/ocpp-charge-point](https://github.com/flowionab/ocpp-charge-point) - Rust library for building OCPP 1.6 and 2.0.1 compliant EV charge points and managing communication with central systems (OCPP 1.6, 2.0.1 · ⭐ 4 · 💤 2024-08-02).
- [OrangeTux/rauts](https://github.com/OrangeTux/rauts) - Rauts is an early-stage Rust library for building OCPP servers and clients with Axum-style request routing and handler extraction (⭐ 4 · 💤 2023-01-04).
- [tux-evse/ocpp-binding-rs](https://github.com/tux-evse/ocpp-binding-rs) - Rust OCPP charger stack implementation packaged as an afb-binding microservice for OCPP 1.6 and 2.0.1 WebSocket communication and testing (OCPP 1.6, 2.0.1 · ⭐ 2 · 💤 2024-11-18).

##### Scala

- [ShellRechargeSolutionsEU/ocpp](https://github.com/ShellRechargeSolutionsEU/ocpp) - Scala library implementing the OCPP network protocol with message types, JSON serialization, and RPC support for OCPP-J 1.5/1.6 and partial OCPP 2.0 (OCPP 1.2, 1.5, 1.6, 2.0 · ⭐ 211 · 💤 2021-10-08).
- [IHomer/scala-ocpp](https://github.com/IHomer/scala-ocpp) - Scala libraries implementing OCPP message models, JSON serialization, and OCPP-J RPC connections for charge point and central system communication (OCPP 1.2, 1.5, 1.6, 2.0 · ⭐ 20 · 💤 2024-05-27).

##### TypeScript

- [extrawest/ocpp-node-ts](https://github.com/extrawest/ocpp-node-ts) - TypeScript library implementing OCPP 2.0.1 JSON client and central system communication over WebSockets (OCPP 1.6, 2.0.1 · ⭐ 19 · 💤 2023-09-14).
- [sepych/ocpp-ts](https://github.com/sepych/ocpp-ts) - TypeScript library for implementing OCPP 1.6 JSON central system and charge point WebSocket communication (OCPP 1.6 · ⭐ 9 · 💤 2021-12-26).
- [evorada/browser-ocpp-client](https://github.com/evorada/browser-ocpp-client) - Browser-compatible TypeScript client library for implementing OCPP 1.6 charge point communication over WebSocket (OCPP 1.6 · ⭐ 6 · 💤 2022-04-15).
- [ChilG/zod-ocpp](https://github.com/ChilG/zod-ocpp) - TypeScript library providing Zod validation schemas for OCPP 1.6J messages, requests, and responses (OCPP 1.6 · ⭐ 1 · 💤 2024-08-02).
- [node-ocpp/core](https://github.com/node-ocpp/core) - A Node.js library for implementing an OCPP Central System over JSON/WebSocket with handlers, outbound messaging, and OCPP 1.6 Core type definitions (OCPP 1.2, 2.0.1 · ⭐ 1 · 💤 2023-09-25).

#### Misc

- [gennadiygnezdilov/ocpp-1.6J-example-request-response](https://github.com/gennadiygnezdilov/ocpp-1.6J-example-request-response) - Example OCPP 1.6J JSON request and response messages for implementing charging station to server communication (OCPP 1.6 · ⭐ 29 · 💤 2024-08-08).
- [Anmirazik/Open-Source-Ev-charger-End-to-End-Solution](https://github.com/Anmirazik/Open-Source-Ev-charger-End-to-End-Solution) - A step-by-step guide for integrating an EVerest-based EV charger with open-source CSMS backends using OCPP (⭐ 19 · 💤 2023-12-07).
- [digitaltwinconsortium/OCPP-Charging-Dashboard](https://github.com/digitaltwinconsortium/OCPP-Charging-Dashboard) - Dockerized Azure web dashboard for displaying EV charging station status using the OCPP data model (JavaScript · ⭐ 17 · 💤 2023-06-27).
- [DeltaVetal26/SteVe-OCPP-HTTP-Client](https://github.com/DeltaVetal26/SteVe-OCPP-HTTP-Client) - A PHP HTTP client that automates SteVe OCPP web interface commands for managing connected charging points (PHP · ⭐ 12 · 💤 2023-10-07).
- [vorchunpaul/ocpp-gateway](https://github.com/vorchunpaul/ocpp-gateway) - OCPP gateway that translates selected messages between OCPP 2.0.1 charge points and OCPP 1.6 servers (OCPP 2.0.1 · Python · ⭐ 4 · 💤 2022-02-28).
- [IdahoLabUnsupported/OCPP-2.0.1-Interim-KPI-Calculator](https://github.com/IdahoLabUnsupported/OCPP-2.0.1-Interim-KPI-Calculator) - An archived toolchain parses OCPP 2.0.1 logs, splits them by device, extracts message fields, and calculates aggregate Interim KPIs (OCPP 2.0.1 · Python · ⭐ 2 · 💤 2026-06-18).
- [abhishandilya/ocpp.ai](https://github.com/abhishandilya/ocpp.ai) - An open-source AI chatbot UI configured for chatting with an OCPP expert (TypeScript · ⭐ 1 · 💤 2023-11-07).

#### Dashboard

- [agruenb/micro-ocpp-dashboard](https://github.com/agruenb/micro-ocpp-dashboard) - A web-based dashboard for monitoring and interacting with the MicroOcpp OCPP library, optimized for deployment on microcontrollers (CSS · ⭐ 13 · 💤 2024-10-16).

#### Testing

- [brandonprry/VolatileOCPP](https://github.com/brandonprry/VolatileOCPP) - VolatileOCPP is a security-focused OCPP scenario test runner for validating CSMS/OCPP server implementations against Open Charge Alliance test document scenarios (OCPP 1.6 · C# · ⭐ 12 · 💤 2025-03-18).

### OCPI

#### Server

- [MTES-MCT/ocpi-playground](https://github.com/MTES-MCT/ocpi-playground) - OCPI Playground is a Docker-based demonstration stack for testing OCPI server topologies and OCPI-related services (Python · ⭐ 6 · 💤 2026-03-27).
- [energywebfoundation/ocn-bridge](https://github.com/energywebfoundation/ocn-bridge) - OCN Bridge is a TypeScript/JavaScript OCPI bridge that connects pluggable CPO or EMSP backoffice APIs to an Open Charging Network node and registry (TypeScript · ⭐ 5 · 💤 2022-04-07).
- [energywebfoundation/ocn-node](https://github.com/energywebfoundation/ocn-node) - Open Charging Network Node is a Kotlin/JVM server that brokers OCPI 2.2 eRoaming requests between EV charging platforms in the decentralized OCN network (OCPI 2.2 · Kotlin · ⭐ 5 · 💤 2024-12-23).
- [kelseymok/ocpi-implementation](https://github.com/kelseymok/ocpi-implementation) - A proof-of-concept OCPI CDR implementation that simulates OCPP events, processes them through Kafka consumers, stores OCPI-related data in DynamoDB, and exposes CDRs through an API (Python · ⭐ 4 · 💤 2023-03-23).

#### Simulator

- [energywebfoundation/ocn-tools](https://github.com/energywebfoundation/ocn-tools) - Open Charging Network Tools provides mock OCPI MSP and CPO servers for developing and registering OCN-based applications (TypeScript · ⭐ 11 · 💤 2022-04-26).

#### Libraries

##### C#

- [kraftvaerk/OCPI](https://github.com/kraftvaerk/OCPI) - C# reference framework for OCPI 2.1.1 DTOs and protocol interfaces (⭐ 16 · 💤 2022-12-08).

##### Java

- [extrawest/Extrawest-OCPI-2.2.1-CPO-Server](https://github.com/extrawest/Extrawest-OCPI-2.2.1-CPO-Server) - Java library for implementing an OCPI 2.2.1 Charging Point Operator server using reusable models, interfaces, controllers, and APIs (OCPI 2.1.1, 2.2, 2.2.1 · ⭐ 11 · 💤 2024-03-11).
- [Llocer/llocer_ocpi](https://github.com/Llocer/llocer_ocpi) - Llocer_ocpi is an open-source library for implementing OCPI 2.2.1 nodes with HTTP servlet handling, request building, and sender/receiver interfaces (OCPI 2.2.1 · ⭐ 10 · 💤 2024-09-29).
- [extrawest/Extrawest-OCPI-2.2.1-EMSP-Server](https://github.com/extrawest/Extrawest-OCPI-2.2.1-EMSP-Server) - Java library for implementing an eMSP OCPI 2.2.1 server using reusable models, controllers, and related components (OCPI 2.1.1, 2.2, 2.2.1 · ⭐ 7 · 💤 2024-02-29).
- [extrawest/Extrawest-OCPI-2.2.1-CPO-Client](https://github.com/extrawest/Extrawest-OCPI-2.2.1-CPO-Client) - Java client library generated from OpenAPI for calling an OCPI 2.2.1 CPO Server API (OCPI 2.2.1 · ⭐ 5 · 💤 2023-11-23).

##### JavaScript

- [hyndex/node-ocpi](https://github.com/hyndex/node-ocpi) - Node-ocpi is a Node.js library providing OCPI data models and validation utilities for EV charging applications (⭐ 7 · 💤 2023-12-26).

##### PHP

- [ChargeMap/ocpi-protocol](https://github.com/ChargeMap/ocpi-protocol) - A PHP PSR-compatible library and client SDK for handling OCPI eMSP request/response classes, models, validation, listing pagination, and CPO API calls (⭐ 21 · 💤 2021-11-12).
- [Codivores/Laravel-OCPI-eMSP](https://github.com/Codivores/Laravel-OCPI-eMSP) - Laravel package implementing OCPI 2.1.1 eMSP functionality, including CDRs, commands, credentials, locations, sessions, and versions modules (⭐ 2 · 💤 2025-06-27).

##### Python

- [NOWUM/pyOCPI](https://github.com/NOWUM/pyOCPI) - PyOCPI is a Python Flask-RESTX package that provides OCPI 2.2 REST endpoint definitions, schemas, OpenAPI support, and manager interfaces for integrating OCPI business logic (⭐ 10 · 💤 2025-03-19).
- [hyndex/OCPIPyBridge](https://github.com/hyndex/OCPIPyBridge) - OCPIPyBridge is a Python library providing Pydantic models and validation for OCPI entities used in EV charging applications (⭐ 4 · 💤 2023-12-26).

##### Scala

- [ShellRechargeSolutionsEU/ocpi-endpoints](https://github.com/ShellRechargeSolutionsEU/ocpi-endpoints) - Scala library providing reusable OCPI protocol endpoint routes, clients, message serialization, and example usage for applications implementing common OCPI modules (OCPI 2.1.1 · ⭐ 15 · 💤 2021-07-29).

##### TypeScript

- [solidstudiosh/ocpi-schema](https://github.com/solidstudiosh/ocpi-schema) - A Node.js tool that generates JSON Schemas for OCPI versions 2.1.1 and later (⭐ 20 · 💤 2025-06-09).
- [andreibesleaga/ocpi-sdk](https://github.com/andreibesleaga/ocpi-sdk) - Deprecated TypeScript/JavaScript SDK for accessing an OCPI REST API, with an included MCP server for AI-based OCPI communication (⭐ 3 · 🚫 deprecated).
- [niklam/ocpi-types](https://github.com/niklam/ocpi-types) - TypeScript DTOs and enums for implementing and validating OCPI 2.2.1 data models in EV charging applications (OCPI 2.2.1 · ⭐ 2 · 💤 2025-06-18).

##### Other

- [GLCharge/ocpi](https://github.com/GLCharge/ocpi) - Go client libraries generated from OpenAPI specifications for interacting with OCPI protocol APIs (OCPI 2.1.1, 2.2.1 · ⭐ 11 · 💤 2024-04-19).

#### Misc

- [energywebfoundation/ocn-registry](https://github.com/energywebfoundation/ocn-registry) - Ethereum smart contracts for registering Open Charging Network nodes, OCPI parties, and service permissions (OCPI 2.2 · Java · ⭐ 4 · 💤 2022-06-13).
- [suroorhussain/ev-protocols](https://github.com/suroorhussain/ev-protocols) - A Docusaurus documentation site that translates the official OCPI specification from AsciiDoc to Markdown for easier navigation (⭐ 2 · 💤 2023-08-16).

#### OpenAPI Specification

- [plugoinc/ocpi-openapi](https://github.com/plugoinc/ocpi-openapi) - An OpenAPI definition project for documenting and validating the OCPI API specification (⭐ 5 · 💤 2024-02-19).

### iso15118

#### Misc

- [FlUxIuS/V2GInjector](https://github.com/FlUxIuS/V2GInjector) - V2GInjector is a tool for capturing, decoding, and injecting V2G packets on HomePlug Green PHY powerline networks used between electric vehicles and charging stations (Python · ⭐ 142 · 💤 2024-12-19).
- [endland/sniffer-iso15118vse](https://github.com/endland/sniffer-iso15118vse) - A modified Wireshark dissector for inspecting ISO 15118-8 vendor-specific elements in Wi-Fi management frames used by EVCC and SECC during wireless EV charging association (⭐ 22 · 💤 2019-11-04).

#### Libraries

##### C++

- [EVerest/libiso15118](https://github.com/EVerest/libiso15118) - C++ library suite implementing ISO 15118-20 communication for EV charging, with ISO 15118-2 and DIN 70121 support planned through related EVerest modules (⭐ 34 · 💤 2026-02-17).

### OICP

#### Libraries

##### Other

- [GLCharge/oicp-client-go](https://github.com/GLCharge/oicp-client-go) - Go client libraries/SDK generated from OpenAPI specifications for the Open Intercharge Protocol (⭐ 6 · 💤 2024-04-19).

### Eichrecht

#### OCMF

- [Namoshek/OpenChargeMeteringFormat](https://github.com/Namoshek/OpenChargeMeteringFormat) - A .NET library for parsing OCMF messages and verifying their signatures (C# · ⭐ 5 · 💤 2025-01-20).

### Other

- [EVerest/EVerest-archived](https://github.com/EVerest/EVerest-archived) - Archived repository whose content has moved to the main EVerest repository (⭐ 346 · 💤 2026-03-16).
- [motown-io/motown](https://github.com/motown-io/motown) - Motown is an Apache-licensed platform for supporting and managing electric vehicle charging infrastructure (Java · ⭐ 44 · 💤 2019-02-01).
- [openchargemap/ocm-data](https://github.com/openchargemap/ocm-data) - Deprecated repository containing gzipped JSON snapshots of Open Charge Map POI and reference data exported from a MongoDB cache (Shell · ⭐ 29 · 🚫 deprecated · 💤 2021-11-05).
- [EVerest/everest-framework](https://github.com/EVerest/everest-framework) - EVerest Framework manages module dependencies, validates module configuration against manifests, and launches EV charging system modules that communicate over a wrapped MQTT protocol (C++ · ⭐ 29 · 💤 2025-12-04).

#### Clearing House Protocol

- [e-clearing-net/OCHP](https://github.com/e-clearing-net/OCHP) - Open Clearing House Protocol is a protocol specification for connecting electric mobility charging infrastructure market actors (XSLT · ⭐ 49 · 💤 2024-05-02).

#### Energy management

- [thepaulcooper/victron-openEVSE](https://github.com/thepaulcooper/victron-openEVSE) - Node-RED controller that adjusts an openEVSE charger via MQTT to use available Victron PV and battery power for EV charging (⭐ 6 · 💤 2021-10-23).

#### Home Assistant integration

- [CreasolTech/DomBusEVSE_ha](https://github.com/CreasolTech/DomBusEVSE_ha) - Home Assistant configuration files for using the DomBusEVSE module to build and control a DIY smart EV wallbox charging station (⭐ 10 · 💤 2023-09-04).
- [SCiunczyk/wallbox-diy](https://github.com/SCiunczyk/wallbox-diy) - ESPHome configuration and hardware files for an ESP32 Wi-Fi to Modbus proxy that connects a DIY DomBusEVSE wallbox to Home Assistant and measures EV charging energy (⭐ 5 · 💤 2025-01-20).

#### Home Energy Management

- [pieterh/energy-management-system](https://github.com/pieterh/energy-management-system) - HEMS is a Docker-deployable home energy management system for monitoring, configuring, and automating devices including Alfen EV charge points, P1 smart meters, and Enphase solar gateways (C# · ⭐ 25 · 💤 2024-04-24).

#### Maps & route planning

- [andreibesleaga/ocm-sdk](https://github.com/andreibesleaga/ocm-sdk) - A deprecated TypeScript/JavaScript SDK and MCP server for accessing the Open Charge Map REST API for EV charging location data (TypeScript · ⭐ 4 · 🚫 deprecated).
- [andreibesleaga/ocm-php](https://github.com/andreibesleaga/ocm-php) - A deprecated unofficial PHP SDK for accessing the Open Charge Map REST API from PHP applications (PHP · ⭐ 0 · 🚫 deprecated).
- [formidablae/EV_Route_Planner](https://github.com/formidablae/EV_Route_Planner) - A Vue.js web app that plans electric vehicle routes with charging-station stops based on vehicle range, departure, and destination using OpenChargeMap and OpenStreetMap data (Vue · ⭐ 27 · 💤 2024-04-08).

#### OCHP Server

- [andreibesleaga/ochp-mcp](https://github.com/andreibesleaga/ochp-mcp) - A deprecated TypeScript MCP server that exposes OCHP 1.4 and OCHP-Direct operations for EV charging authorization, charge point data, status, CDRs, and EVSE control (TypeScript · ⭐ 0 · 🚫 deprecated).

#### OSCP Libraries

- [andreibesleaga/oscp-sdk](https://github.com/andreibesleaga/oscp-sdk) - Deprecated TypeScript/JavaScript SDK for the OSCP REST API with an MCP server for AI-assisted API exploration and integration (TypeScript · ⭐ 2 · 🚫 deprecated).

### Uncategorized

- [gregszalay/ocpp-charging-station](https://github.com/gregszalay/ocpp-charging-station) - Charging Station firmware for electric vehicles - OCPP 2.0.1. compliant (C++ · ⭐ 22 · 💤 2022-10-14).
- [ChargeMap/autocharge-vehicles-database](https://github.com/ChargeMap/autocharge-vehicles-database)

## To refine (173 projects)

### OCPP

#### Server

- [yuncitys/YunCharging](https://github.com/yuncitys/YunCharging) - YunCharge is an open-source EV and e-bike charging operation and billing platform with user apps, payments, charger management, and support for YunKuaiChong and OCPP protocols (OCPP 1.5, 2.0 · Java · ⭐ 71 · 💤 2024-10-17).
- [gennadiygnezdilov/php-ocpp-1.6J](https://github.com/gennadiygnezdilov/php-ocpp-1.6J) - A PHP WebSocket server script for handling OCPP 1.6J communication with EV charging stations using Ratchet and MySQL (OCPP 1.6 · PHP · ⭐ 15 · 💤 2024-08-09).
- [stromenergy/strom](https://github.com/stromenergy/strom) - Strom is an open-source OCPP 1.6 bridge that lets charge point owners start, stop, monitor, and bill EV charging sessions using Lightning and Nostr payment flows (OCPP 1.6, 2.0.1 · Go · ⭐ 9 · 💤 2023-05-20).
- [ChargeTimeEU/ChargeTime-HQ](https://github.com/ChargeTimeEU/ChargeTime-HQ) - ChargeTime-HQ is a JavaFX application for operating EV charging equipment using OCPP (Java · ⭐ 8 · 💤 2020-10-13).
- [davbauer/ocpp-manager](https://github.com/davbauer/ocpp-manager) - OCPP Manager is a web-based OCPP 1.6J charging station management platform for monitoring chargers, managing RFID authorizations, and tracking charging transactions (TypeScript · ⭐ 6).
- [psnehanshu/ocpp-central-system-boilerplate-code](https://github.com/psnehanshu/ocpp-central-system-boilerplate-code) - Boilerplate Node.js code for starting an OCPP central system server (JavaScript · ⭐ 6 · 💤 2022-12-13).
- [Llocer/llocer_ev_examples](https://github.com/Llocer/llocer_ev_examples) - OpenEV examples provides sample OCPP server and client simulator code plus OCPI node implementations for credentials and locations modules (Java · ⭐ 5 · 💤 2022-07-16).
- [u2ware/ocpp-boot-server](https://github.com/u2ware/ocpp-boot-server) - Spring Boot-based customizable OCPP server emulator/sample implementation supporting OCPP 1.6, 2.0.1, and 2.1 with pluggable Java handlers and mock testing (Java · ⭐ 5).
- [opencpo/opencpo](https://github.com/opencpo/opencpo) - OpenCPO is an open-source EV charging platform for running a CPO network with an OCPP 1.6/2.0.1 CSMS, admin dashboard, driver PWA, and virtual charger simulator (OCPP 1.6, 2.0.1 · Shell · ⭐ 4).
- [apostoldevel/ocpp-css](https://github.com/apostoldevel/ocpp-css) - OCPP Central System as a Service provides a central system for connecting, managing, and processing data from EV charging stations via OCPP 1.6 (⭐ 4 · 💤 2023-04-19).
- [mschmitt/shocpp](https://github.com/mschmitt/shocpp) - Shocpp is a Bash-based rudimentary OCPP 1.6 service for a personal wallbox that handles RFID and remote-start charging sessions and records per-account energy consumption (Shell · ⭐ 3).
- [ruslan-hut/evsys](https://github.com/ruslan-hut/evsys) - EVSYS is an OCPP 1.6J central system server for managing charging points, users, sessions, and related notifications (OCPP 1.6 · Go · ⭐ 3).
- [eva-sean/oye-proxy](https://github.com/eva-sean/oye-proxy) - OYE OCPP Proxy is a Node.js OCPP proxy that sits between EVSE chargers and a CSMS to monitor, log, inject commands, and optionally provide basic standalone charging control (OCPP 1.6 · JavaScript · ⭐ 3).
- [BashTheDog/elecq-ocpp-ha](https://github.com/BashTheDog/elecq-ocpp-ha) - Home Assistant custom integration that runs a local OCPP 2.0.1 WebSocket server to monitor and control Elecq AU101/AE106 EV chargers (OCPP 2.0.1 · Python · ⭐ 3).
- [OpenChargingCloud/CSMSApp](https://github.com/OpenChargingCloud/CSMSApp) - Electron-based OCPP Charging Station Management System application for testing and certification of e-mobility protocols, vendor extensions, and third-party charging stations (OCPP 2.1 · TypeScript · ⭐ 2).
- [EVtivity/evtivity-csms-helm](https://github.com/EVtivity/evtivity-csms-helm) - Helm chart for deploying the EVtivity CSMS, including OCPP and OCPI services, on Kubernetes (OCPP 1.6 · Shell · ⭐ 2).
- [FlipSoftware/moovolt-mvp](https://github.com/FlipSoftware/moovolt-mvp) - MOOV.OLT is an OCPP-based CSMS with a charge point service for WebSocket communication with physical chargers and a management system for permissions, charging control, and payments over AMQP (TypeScript · ⭐ 2 · 💤 2024-09-19).
- [adriandotdev/ocpp-central-system](https://github.com/adriandotdev/ocpp-central-system) - Node.js implementation of core OCPP central system commands exposed via REST APIs and WebSocket communication (JavaScript · ⭐ 1 · 💤 2024-12-12).
- [loafoe/go-occp-server](https://github.com/loafoe/go-occp-server) - Go OCPP 1.6-J central system server for connecting to EV chargers, authenticating charge points, monitoring status and meter values, and issuing remote control commands through an HTTP API (OCPP 1.6 · Go · ⭐ 1).
- [DJBenson/GivEVC-OCPPv2](https://github.com/DJBenson/GivEVC-OCPPv2) - Self-hosted OCPP 1.6J portal that replaces the GivEnergy cloud for managing GivEnergy EV chargers, including live monitoring, charging control, scheduling, RFID management, firmware updates, and API access (OCPP 1.6 · Python · ⭐ 1).
- [Anmirazik/OCPP1.6J-Server-Nodered](https://github.com/Anmirazik/OCPP1.6J-Server-Nodered) - A Node-RED prototype OCPP 1.6J server that exchanges basic charger commands and forwards OCPP data to ThingsBoard over MQTT for visualization and control (OCPP 1.6 · ⭐ 1 · 💤 2023-11-25).
- [hpxix/Aviator-Beta](https://github.com/hpxix/Aviator-Beta) - Aviator is a TypeScript/Node.js server runtime for managing EV charging infrastructure with OCPP 2.0.1 message routing, validation, and modular endpoints (OCPP 2.0.1 · TypeScript · ⭐ 1 · 💤 2024-11-28).
- [opencpo/opencpo-admin](https://github.com/opencpo/opencpo-admin) - OCPP Admin is a FastAPI-based CPO dashboard for managing OCPP charger networks, sessions, tariffs, tokens, PKI, and real-time OCPP messages through an OCPP Core API (HTML · ⭐ 1).
- [opencpo/opencpo-core](https://github.com/opencpo/opencpo-core) - OCPP Core is an OCPP 1.6j and 2.0.1 CSMS server with charger profiles, built-in PKI, ISO 15118 Plug & Charge support, OCPI roaming, REST APIs, and Redis/PostgreSQL-backed state and events (OCPP 1.6, 2.0.1 · Python · ⭐ 1).
- [SolarNetwork/solarnetwork-node-ocpp](https://github.com/SolarNetwork/solarnetwork-node-ocpp) - SolarNode plugins enabling OCPP protocol support for the SolarNode energy management platform (Java · ⭐ 0).
- [steve-white/ocpp-server](https://github.com/steve-white/ocpp-server) - A Go proof-of-concept OCPP 1.6 CSMS server for connecting chargers, handling basic messages and sessions, and sending charger commands via REST and message queues (OCPP 1.6 · Go · ⭐ 0).
- [chethanbhatbs/CMS](https://github.com/chethanbhatbs/CMS) - EV Charging CMS is a React and Python charge point operator management system with an OCPP 1.6 WebSocket server, live session monitoring, remote charging operations, CRM, RBAC administration, and a virtual charger for testing (OCPP 1.6 · JavaScript · ⭐ 0 · 💤 2026-06-15).
- [LastProject-ESIEE/OCPPConfigurationServer](https://github.com/LastProject-ESIEE/OCPPConfigurationServer) - A Java web application for configuring and updating EV charge points using OCPP 1.6J (Java · ⭐ 0).
- [dreak/ocpp-central-system](https://github.com/dreak/ocpp-central-system) - OCPP 1.6 central system with a NestJS WebSocket backend and React dashboard for managing EV charge points, transactions, and tags (OCPP 1.6 · TypeScript · ⭐ 0).

#### Simulator

- [sap-labs-france/ev-simulator](https://github.com/sap-labs-france/ev-simulator) - An OCPP-J charging station simulator for e-mobility testing (⭐ 38 · 💤 2024-01-04).
- [ChargePi/ChargePi](https://github.com/ChargePi/ChargePi) - ChargePi is a deprecated Raspberry Pi-based EV charge point client implementing OCPP 1.6 JSON/WebSocket for controlling multiple EVSE connectors with LEDs, relays, and power meters (OCPP 1.6, 2.0.1 · Python · ⭐ 27 · 🚫 deprecated · 💤 2024-07-25).
- [TumbleOwlee/ferrowl](https://github.com/TumbleOwlee/ferrowl) - A Rust terminal user interface application for simulating Modbus and OCPP charging devices (stations and central systems) for testing and development (OCPP 1.6, 2.0.1, 2.1 · Rust · ⭐ 5).
- [u2ware/ocpp-boot-client](https://github.com/u2ware/ocpp-boot-client) - Ocpp-boot-client is a Spring Boot OCPP client emulator/sample implementation for OCPP 1.6, 2.0.1, and 2.1 with customizable client handlers and a console UI (Java · ⭐ 5).
- [rohittiwari-dev/ocpp-ws-simulator](https://github.com/rohittiwari-dev/ocpp-ws-simulator) - A browser-based simulator for running one or more OCPP charge points against a CSMS for testing and debugging (OCPP 1.6, 2.0.1, 2.1 · TypeScript · ⭐ 3).
- [ZhongRuoyu/ocppsim](https://github.com/ZhongRuoyu/ocppsim) - A terminal OCPP-J charge point simulator written in Rust that connects to a CSMS over WebSocket and enables interactive testing of OCPP protocol workflows and charge point behavior (OCPP 1.6, 2.0.1, 2.1 · Rust · ⭐ 2).
- [autimit/ocpp-zig-poc](https://github.com/autimit/ocpp-zig-poc) - A Zig-based CSMS simulator that models EV charging sessions from mocked OCPP-inspired JSON data and calculates power, energy, cost, and host revenue sharing (Zig · ⭐ 2 · 💤 2025-07-02).
- [psnehanshu/charge-point-simulator](https://github.com/psnehanshu/charge-point-simulator) - A charge point simulator that runs multiple simultaneous charging sessions using OCPP 1.5 JSON (JavaScript · ⭐ 2 · 💤 2020-10-09).
- [brunoluiz/ocpp-server-tool](https://github.com/brunoluiz/ocpp-server-tool) - Java command-line tool that simulates an OCPP 1.5 SOAP Central System server for sending supported commands to a charge point (OCPP 1.5 · Java · ⭐ 2 · 💤 2017-03-03).
- [kiranj26/evse-fault-injector](https://github.com/kiranj26/evse-fault-injector) - EVSE Fault Injector is a C++ tool for simulating faults and testing EV charger behavior and protocol robustness with OCPP, ISO 15118, and real or simulated EVSE setups (Makefile · ⭐ 1 · 💤 2024-12-16).
- [ruslan-hut/ocpp-emu](https://github.com/ruslan-hut/ocpp-emu) - Web-based EV charging station emulator for creating and managing simulated OCPP 1.6, 2.0.1, and 2.1 charging stations with message inspection and custom message testing (OCPP 1.6, 2.0.1, 2.1 · Go · ⭐ 1).
- [MuhammedAlmaz/ma-ocpp-simulator](https://github.com/MuhammedAlmaz/ma-ocpp-simulator) - A web-based OCPP 1.6 charge point simulator for testing EV charging back-end applications (OCPP 1.6, 2.0.1 · TypeScript · ⭐ 1 · 💤 2024-05-09).
- [srcfl/device-simulator](https://github.com/srcfl/device-simulator) - Device Simulator is a Go desktop and Docker app for dynamically simulating solar inverters, batteries, EV chargers, and energy meters over Modbus TCP, MQTT, and OCPP for testing (Go · ⭐ 1).
- [soneeee22000/go-charger-ramp](https://github.com/soneeee22000/go-charger-ramp) - A Go charger-supervision service that simulates an OCPP-style heartbeat fleet, tracks charger liveness concurrently, exposes fleet status over HTTP, and shuts down gracefully (OCPP 1.6 · Go · ⭐ 0).
- [dumanburak/ocpp-client-demo](https://github.com/dumanburak/ocpp-client-demo) - A Python asyncio demo OCPP 1.6J charge point client that simulates charging station workflows over WebSocket for testing CSMS implementations (OCPP 1.6 · Python · ⭐ 0).
- [eveys-mobility/Simulator](https://github.com/eveys-mobility/Simulator) - COCPP Charge-Point Simulator simulates one or many OCPP 1.6 charging stations via a web UI to test, debug, load-test, and validate CSMS back-office behavior (OCPP 1.6 · TypeScript · ⭐ 0).
- [LuRSousa/ChargeGrid-Intelligence](https://github.com/LuRSousa/ChargeGrid-Intelligence) - ChargeGrid Intelligence is a browser-based proof-of-concept EV charging management simulator with dynamic load balancing, OCPP event logging, dynamic pricing, and solar-aware charging decisions (JavaScript · ⭐ 0).
- [chankinwui/OCPP7ROS](https://github.com/chankinwui/OCPP7ROS) - A gateway and simulator project connecting OCPP 2.0.1 EV charging systems with ROS 2 robots (⭐ 0 · 💤 2022-11-01).
- [opencpo/opencpo-charger-farm](https://github.com/opencpo/opencpo-charger-farm) - Virtual Charger Farm is an OCPP 1.6j/2.0.1 virtual charger simulator for stress testing EV charging backends with realistic charger behavior, network faults, charging physics, and scenario reporting (OCPP 1.6, 2.0.1 · Python · ⭐ 0).
- [MarekPokornyOva/EvChargerSimulator](https://github.com/MarekPokornyOva/EvChargerSimulator) - Browser-hosted EV charger simulator that communicates with OCPP 1.6J (OCPP 1.6 · TypeScript · ⭐ 0 · 💤 2025-05-06).
- [crakashp2905-hub/CyberDeception-EVSE](https://github.com/crakashp2905-hub/CyberDeception-EVSE) - Research project providing an OCPP-based EVSE honeypot and machine-learning notebooks for detecting attacks on EV charging infrastructure (Jupyter Notebook · ⭐ 0).

#### Libraries

##### C

- [kiranj26/MicroOCPP-on-STM32F4](https://github.com/kiranj26/MicroOCPP-on-STM32F4) - Embedded STM32F4 EVSE firmware integrating MicroOCPP with secure networking to provide OCPP 1.6 support for EV chargers (OCPP 1.6 · ⭐ 11 · 💤 2025-01-27).

##### C#

- [fabyr/ocpp-sharp](https://github.com/fabyr/ocpp-sharp) - Ocpp-sharp is a C#/.NET library for implementing OCPP 1.6 and 2.0.1 message handling, server setup, and example client/server communication (OCPP 1.6, 2.0.1 · ⭐ 10).

##### Go

- [JohnMaddison/ocpp-go](https://github.com/JohnMaddison/ocpp-go) - Ocpp-go is a Go library for building OCPP 1.6 and 2.1 JSON charge point clients and central systems with typed messages, WebSocket transport, routing, and request/response helpers (OCPP 1.6, 2.1 · ⭐ 1).
- [aasanchez/ocpp16j](https://github.com/aasanchez/ocpp16j) - Go library for parsing, validating, decoding, and marshaling OCPP-J 1.6 Call, CallResult, and CallError message envelopes (OCPP 1.6 · ⭐ 0).

##### Java

- [wang007/e-iot](https://github.com/wang007/e-iot) - E-iot is a Vert.x-based Java library for implementing OCPP 1.6J, 2.0.1, 2.1 and Yunkuaichong charging protocols (OCPP 1.6, 2.0.1, 2.1 · ⭐ 29).
- [steve-community/ocpp-jaxb](https://github.com/steve-community/ocpp-jaxb) - Java data model mappings for OCPP requests and responses across versions 1.2, 1.5, 1.6, 1.6 security, 2.0.1, and 2.1 (OCPP 1.2, 1.5, 1.6, 2.0.1, 2.1 · ⭐ 18).

##### JavaScript

- [romfrolov/ocpp-util](https://github.com/romfrolov/ocpp-util) - OCPP Util is a JavaScript utility library for validating OCPP cardinalities and primitive datatypes and accessing OCPP 1.6 and 2.0 enumerations (OCPP 1.6, 2.0 · ⭐ 0 · 💤 2022-12-30).

##### Kotlin

- [Jaypatelbond/ocpp-kotlin](https://github.com/Jaypatelbond/ocpp-kotlin) - OCPP Kotlin is a Kotlin/Android client library for implementing OCPP 1.6 and 2.0.1 communication in EV charging station applications (OCPP 1.6, 2.0.1 · ⭐ 2).

##### PHP

- [solutionforest/ocpp-php](https://github.com/solutionforest/ocpp-php) - PHP library for building OCPP 1.6 and OCPP 2.0.1 charging station and central system implementations over WebSocket (OCPP 1.6, 2.0, 2.0.1 · ⭐ 4).

##### Python

- [QuecPython/OCPP-v1.6](https://github.com/QuecPython/OCPP-v1.6) - A QuecPython Python package implementing OCPP 1.6 JSON building blocks for charge point clients, with demo client and server examples (OCPP 1.6 · ⭐ 11 · 💤 2025-04-30).
- [cdfq384903/Machnata](https://github.com/cdfq384903/Machnata) - Machnata converts JSON Schema definitions, including OCPP and OCPI schemas, into Protocol Buffers and generated multi-language data structures (OCPP 1.6, 2.0.1, 2.1 · ⭐ 1).
- [javierojan/askacharge-python](https://github.com/javierojan/askacharge-python) - Python SDK for the askacharge.com EV charging platform API, providing access to chargers, charging sessions, and signed webhook verification for an OCPP/OCPI-based CSMS (OCPP 1.6 · ⭐ 0).
- [Polyconseil/ocpp-codec](https://github.com/Polyconseil/ocpp-codec) - A Python library that defines OCPP 1.6 and 2.0 message dataclasses and serializes/deserializes them to and from JSON payloads (⭐ 0 · 💤 2020-06-01).

##### Scala

- [ShellRechargeSolutionsEU/ocpp-soap](https://github.com/ShellRechargeSolutionsEU/ocpp-soap) - Scala libraries and generated SOAP bindings for handling OCPP 1.2 and 1.5 messages over SOAP (OCPP 1.2 · ⭐ 3 · 💤 2020-06-12).

##### TypeScript

- [rohittiwari-dev/ocpp-ws-io](https://github.com/rohittiwari-dev/ocpp-ws-io) - TypeScript OCPP WebSocket toolkit for building RPC clients and servers, charge point simulators, version proxies, smart charging components, and CLI tooling (OCPP 1.6, 2.0.1, 2.1 · ⭐ 2).
- [rohittiwari-dev/ocpp-smart-charge-engine](https://github.com/rohittiwari-dev/ocpp-smart-charge-engine) - TypeScript library that computes and dispatches OCPP smart charging profiles to distribute site grid power across EV charging sessions (OCPP 1.6, 2.0.1, 2.1 · ⭐ 1).
- [rohittiwari-dev/voltlog-io](https://github.com/rohittiwari-dev/voltlog-io) - VoltLog is a TypeScript structured logging library for real-time systems, with OCPP-aware context support for WebSocket and IoT infrastructure (⭐ 1).

##### Other

- [Llocer/llocer_ocpp_json](https://github.com/Llocer/llocer_ocpp_json) - JSON schemas for OCPP 2.0.1 messages, with Maven support for generating Java POJOs (OCPP 2.0.1 · ⭐ 3 · 💤 2022-04-22).

#### Misc

- [apundir/wsbalancer](https://github.com/apundir/wsbalancer) - A Go stateful WebSocket reverse proxy and load balancer that preserves client sessions while failing over connections between backends, including OCPP-style EV charger server deployments (Go · ⭐ 31 · 💤 2020-09-10).
- [flashg1/evSolarCharger](https://github.com/flashg1/evSolarCharger) - Home Assistant blueprint that controls EV charging via OCPP and EV-specific APIs to use surplus solar energy, schedules, and weather forecasts (⭐ 17).
- [pazzk-labs/evse](https://github.com/pazzk-labs/evse) - Pazzk EVSE is an archived open-source EVSE firmware project for building charging stations with ISO 15118, IEC 61851, OCPP, and Plug & Charge support (C · ⭐ 16).
- [JoaoPedroBelo/bmw-wallbox-ha](https://github.com/JoaoPedroBelo/bmw-wallbox-ha) - Home Assistant custom integration for locally monitoring and controlling BMW Wallbox chargers over OCPP 2.0.1 with WSS (OCPP 2.0.1 · Python · ⭐ 14).
- [weemaba999/homeassistant-tap-community](https://github.com/weemaba999/homeassistant-tap-community) - Unofficial Home Assistant integration for monitoring and controlling Tap Electric-managed EV chargers via Tap APIs, with optional live session metadata and remote start/stop support (OCPP 1.6 · Python · ⭐ 5).
- [energychain/corrently-charge](https://github.com/energychain/corrently-charge) - Corrently Charge is a Node.js tariff evaluation module that selects EV charging tariffs based on charging goals, time, and energy mix and applies them through a scheduler connection to a CPO backend via OCPP (HTML · ⭐ 4 · 💤 2024-01-10).
- [ChargePi/chargeflow](https://github.com/ChargePi/chargeflow) - ChargeFlow is a CLI tool for validating raw OCPP 1.6, 2.0.1, and 2.1 JSON messages against standard or custom schemas (OCPP 1.6, 2.0.1, 2.1 · Go · ⭐ 3).
- [hsperker/conversational-websocket-server](https://github.com/hsperker/conversational-websocket-server) - A Spring Boot JSR-356 WebSocket server with a command-line shell for listing connected clients and sending broadcast or unicast messages (Java · ⭐ 3 · 💤 2018-02-08).
- [alexs-sh/tom](https://github.com/alexs-sh/tom) - A Python converter that bridges OCPP SOAP charge points to OCPP JSON central systems, with support for OCPP 1.5 messages (OCPP 1.5 · Python · ⭐ 3 · 💤 2024-06-22).
- [jimmyjoseph-web3/ChargeFrog-Hedera](https://github.com/jimmyjoseph-web3/ChargeFrog-Hedera) - ChargeFrog is a Hedera-based platform for proposing, funding, tokenizing, deploying, using, and auditing community-owned EV charging stations with on-chain carbon impact tracking (TypeScript · ⭐ 2).
- [skazemi/awesome-evse](https://github.com/skazemi/awesome-evse) - A curated awesome list of EV charging tools, frameworks, libraries, and software (⭐ 1 · 💤 2024-03-13).
- [mjasinskee/emob-ocpp-slides](https://github.com/mjasinskee/emob-ocpp-slides) - A reveal.js presentation explaining how to model an OCPP charging station as an actor system (JavaScript · ⭐ 1 · 💤 2022-12-07).
- [lex/evse-id-generator](https://github.com/lex/evse-id-generator) - A static web tool that generates, validates, parses, and exports EVSE identifiers for ISO 15118 and OCPP 2.0.1 charging infrastructure (OCPP 2.0.1 · HTML · ⭐ 0).
- [glurp/avere-advenir-json-generator](https://github.com/glurp/avere-advenir-json-generator) - A Ruby script that generates charging curve and charging session data from OCPP 1.5 JSON logs and sends it to advenir.mobi over HTTPS (OCPP 1.5 · Ruby · ⭐ 0 · 💤 2018-06-14).
- [leonard-voss/nocpp](https://github.com/leonard-voss/nocpp) - NOCPP is a Python prototype for targeted OCPP 1.6-J penetration testing of charging stations, including fuzzing scenarios, information gathering, and PDF result export (OCPP 1.6 · Python · ⭐ 0 · 💤 2025-01-22).
- [arcnode-io/ems-industrial-fixtures](https://github.com/arcnode-io/ems-industrial-fixtures) - Rust mock implementations of industrial gateway protocols for testing Modbus, SNMP, Redfish, DNP3, and CANbus integrations (Rust · ⭐ 0).
- [mysmartlife-helsinki/ev-charging](https://github.com/mysmartlife-helsinki/ev-charging) - This repository is an EV charging-related project tagged with OCPP, ECU, and VCCU, but its README does not document specific functionality (⭐ 0 · 💤 2019-06-01).
- [cz-lucas/alphatecmini-ocpp](https://github.com/cz-lucas/alphatecmini-ocpp) - An OCPP v1.6 firmware implementation for ESP32-S3 that wirelessly controls an Alphatec Mini EV wallbox with RFID-based authentication and tariff management (OCPP 1.6 · C++ · ⭐ 0).
- [BBessler/Solarmanager](https://github.com/BBessler/Solarmanager) - Solarmanager is a local home energy management system that monitors PV generation and household consumption to control EV charging, batteries, heating, and smart-home loads (OCPP 1.6 · Shell · ⭐ 0).
- [Veton-ev/Veton-EMS-Integration](https://github.com/Veton-ev/Veton-EMS-Integration) - Developer documentation and examples for integrating Veton/Phoenix Contact CHARX EV chargers with an EMS via Modbus, MQTT, REST, and OCPP 1.6 (OCPP 1.6 · ⭐ 0).
- [slachiewicz/ocpp16jto201gateway](https://github.com/slachiewicz/ocpp16jto201gateway) - OCPP 1.6 JSON to OCPP 2.0.1 gateway for translating charge point communication between protocol versions (OCPP 1.6, 2.0.1 · ⭐ 0 · 💤 2023-12-02).
- [Cano2020/Offshore-software-team](https://github.com/Cano2020/Offshore-software-team) - Canopus is a software services team offering app development, emerging technology prototyping, and data science services (⭐ 0 · 💤 2021-09-30).
- [Emulate-Energy/EDAP](https://github.com/Emulate-Energy/EDAP) - EDAP is a Python library and example gateway for implementing cloud access and low-latency control of energy devices using the Energy Device Aggregation Protocol (Python · ⭐ 0).
- [MostafaMoradii/eveys-console](https://github.com/MostafaMoradii/eveys-console) - Eveys-console is a sign-in protected web administration console for operating and inspecting an OCPP gateway through its existing Kafka, REST, and WebSocket interfaces (TypeScript · ⭐ 0 · 💤 2026-05-14).

#### Compliance Testing

- [opencpo/opencpo-tester](https://github.com/opencpo/opencpo-tester) - OCPP Compliance Tester is a CLI tool that acts as a CSMS to run OCPP 1.6 and 2.0.1 compliance tests against EV chargers and generate PDF, HTML, and JSON reports (OCPP 1.6 · Python · ⭐ 0).

#### Console

- [eveys-mobility/Console](https://github.com/eveys-mobility/Console) - Eveys-console is a protected operator web console for inspecting, diagnosing, and controlling OCPP chargers through an existing OCPP gateway using Kafka-backed live updates and REST mutations (TypeScript · ⭐ 2).

#### Relay

- [michael-adler/ha-ocpp-relay](https://github.com/michael-adler/ha-ocpp-relay) - Home Assistant integration and CLI tools that relay OCPP traffic between an EV charger and CPMS while exposing monitored messages as energy sensors (Python · ⭐ 1).

#### Server UI

- [ocpp-balanz/balanz-ui](https://github.com/ocpp-balanz/balanz-ui) - Balanz UI is a React/TypeScript web interface for managing balanz OCPP server entities, monitoring live charging status, and viewing historic charging sessions (TypeScript · ⭐ 1).

### OCPI

#### Simulator

- [extrawest/bdd_ocpi_2.2.1_emsp](https://github.com/extrawest/bdd_ocpi_2.2.1_emsp) - A Cucumber-based BDD test suite that simulates OCPI 2.2.1 CPO requests to verify eMSP server protocol compliance (OCPI 2.2.1 · Java · ⭐ 3 · 💤 2023-12-06).

#### Libraries

##### Java

- [Llocer/llocer_ocpi_json](https://github.com/Llocer/llocer_ocpi_json) - Provides JSON schemas for OCPI 2.2.1 messages and Maven configuration to generate Java POJOs from them (OCPI 2.2.1 · ⭐ 3 · 💤 2024-11-13).
- [extrawest/Extrawest-OCPI-2.2.1-EMSP-Client](https://github.com/extrawest/Extrawest-OCPI-2.2.1-EMSP-Client) - Java client library generated from OpenAPI for calling an OCPI 2.2.1 eMSP server API (OCPI 2.2.1 · ⭐ 3 · 💤 2023-12-06).

##### Makefile

- [ChargePi/ocpi-sdk-go](https://github.com/ChargePi/ocpi-sdk-go) - Go SDK providing client and server libraries for the OCPI (Open Charge Point Interface) protocol version 2.2.1, auto-generated from OpenAPI specifications (OCPI 2.2.1 · ⭐ 2).

##### Python

- [Hamza-nabil/ocpi-tariffs-py](https://github.com/Hamza-nabil/ocpi-tariffs-py) - Python library for calculating and validating OCPI 2.2.1 EV charging tariffs against CDRs, including tariff dimensions, restrictions, time zones, and step-size rounding (OCPI 2.2.1 · ⭐ 1).
- [codexistente/ocpi-python](https://github.com/codexistente/ocpi-python) - Python library for implementing the Open Charge Point Interface (OCPI) protocol with FastAPI, supporting OCPI versions 2.1.1, 2.2.1, and 2.3.0 (OCPI 2.3.0 · ⭐ 0).

#### Misc

- [BePower/bepower.github.io](https://github.com/BePower/bepower.github.io) - Bepower.github.io is a GitHub Pages repository for bePower, with repository topics indicating OCPI-related CPO/eMSP/MSP content (Ruby · ⭐ 1 · 💤 2022-08-18).
- [alickjoe/test-ocpi](https://github.com/alickjoe/test-ocpi) - A web-based tool that validates JSON payloads against OCPI schemas across multiple OCPI versions and modules (OCPI 2.1.1, 2.2.1, 2.3.0 · JavaScript · ⭐ 1).
- [Ko1103/ocpi-mcp-server](https://github.com/Ko1103/ocpi-mcp-server) - A Node.js MCP server that exposes OCPI documentation for use in tools such as Cursor (TypeScript · ⭐ 0).

### iso15118

#### Plug&Charge

- [OpenV2G/OpenV2G-base](https://github.com/OpenV2G/OpenV2G-base) - OpenV2G-base provides modular V2G Plug and Charge PKI infrastructure components and REST APIs for ISO 15118 market roles, with mock services where hardware integration is required (⭐ 7 · 💤 2017-08-17).

#### Misc

- [uhi22/ccs32](https://github.com/uhi22/ccs32) - An Arduino/ESP32 project that implements the vehicle-side CCS ISO 15118 charging controller on a WT32-ETH01 with a HomePlug modem (C · ⭐ 32 · 💤 2023-07-18).
- [cepsdev/v2g-guru-slac](https://github.com/cepsdev/v2g-guru-slac) - V2g-guru-slac is a C++20 simulation and implementation of ISO 15118-3 SLAC for matching EVs with EVSEs using real SLAC messages over SCTP (C++ · ⭐ 8 · 💤 2022-02-22).
- [Pokiledaa/slac](https://github.com/Pokiledaa/slac) - Python implementation of SLAC for INSYS Powerline GP, usable standalone or connected to an EVSE controller (Python · ⭐ 5 · 💤 2022-09-21).
- [nvdungx/ISO15118_3_TestEnv](https://github.com/nvdungx/ISO15118_3_TestEnv) - ISO15118_3_TestEnv is a C++ conformance test environment for the ISO 15118-3 HPGP powerline and data link layers on Raspberry Pi (C++ · ⭐ 4 · 💤 2024-06-03).
- [majbthrd/V2Gredux](https://github.com/majbthrd/V2Gredux) - ISO 15118-2 EVSE emulator that implements SDP and ISO 15118-2 communication for testing against an electric vehicle, using OpenV2G (C · ⭐ 2).
- [donadelden/EVExchange](https://github.com/donadelden/EVExchange) - EVExchange provides tools, scripts, testbed configurations, and countermeasure materials for studying an ISO 15118/V2G EV charging attack (Python · ⭐ 0 · 💤 2021-11-02).

#### Libraries

##### C

- [Ecognize/openv2g](https://github.com/Ecognize/openv2g) - OpenV2G implements core ISO 15118 and DIN 70121 V2G communication codecs and interfaces for EV charging systems (⭐ 23 · 💤 2021-01-30).
- [oshsos/publicV2G](https://github.com/oshsos/publicV2G) - PublicV2G is a C++ ISO 15118 V2G communication stack for embedded CCS AC/DC smart charging systems (⭐ 0).

##### Go

- [joeky888/exi-go](https://github.com/joeky888/exi-go) - Pure Go EXI encoder/decoder library for ISO 15118-20 messages, with C and Python bindings (⭐ 0).

### OICP

#### Libraries

##### C#

- [OpenChargingCloud/WWCP_OICP](https://github.com/OpenChargingCloud/WWCP_OICP) - WWCP OICP is a .NET implementation that bridges WWCP entities with OICP v2.3 for CPO, EMP, and central service communication (⭐ 11).

##### Makefile

- [ChargePi/oicp-sdk-go](https://github.com/ChargePi/oicp-sdk-go) - A Go HTTP client SDK for the OICP CPO API, generated from the OpenAPI specification (⭐ 1 · 💤 2025-05-18).

### EMIP

#### Libraries

##### C#

- [OpenChargingCloud/WWCP_eMIP](https://github.com/OpenChargingCloud/WWCP_eMIP) - A .NET library for connecting World Wide Charging Protocol entities with Gireve eMIP v0.7.4 roaming entities (⭐ 2).

### OIOI

#### Libraries

##### C#

- [OpenChargingCloud/WWCP_OIOI](https://github.com/OpenChargingCloud/WWCP_OIOI) - A .NET 6 library connecting WWCP entities with PlugSurfing OIOI v4.x e-mobility provider protocol implementations (⭐ 2 · 💤 2023-09-11).

### Eichrecht

#### Misc

- [wiedergruen/ocmf](https://github.com/wiedergruen/ocmf) - Markdown version of the Open Charge Metering Format specification for further development within the SAFE Group (⭐ 3 · 💤 2019-07-08).

#### OCMF

- [ChargePi/ocmf-go](https://github.com/ChargePi/ocmf-go) - Go library for generating, signing, and parsing Open Charge Metering Format messages for EV charging meter data (Go · ⭐ 3).

#### Validator

- [OpenChargingCloud/ChargyDesktopApp](https://github.com/OpenChargingCloud/ChargyDesktopApp) - Chargy is a transparency validation tool and library for verifying e-mobility charging processes and cryptographic energy measurements according to German Calibration Law (Eichrecht) (TypeScript · ⭐ 11).
- [OpenChargingCloud/ChargyWebApp](https://github.com/OpenChargingCloud/ChargyWebApp) - Chargy is an open-source transparency software library that validates cryptographic signatures of EV charging processes according to German Calibration Law (Eichrecht) and related EU regulations (TypeScript · ⭐ 0).

#### Verification

- [OpenChargingCloud/ChargyMobileApp](https://github.com/OpenChargingCloud/ChargyMobileApp) - A transparency application for verifying cryptographic signatures of energy measurements in EV charging transactions according to German Eichrecht regulations (TypeScript · ⭐ 8).

### Other

- [pogopaule/awesome-sustainability-jobs](https://github.com/pogopaule/awesome-sustainability-jobs) - A curated list and map of sustainability-sector companies that offer developer jobs (Python · ⭐ 512 · 💤 2025-05-17).
- [OPCFoundation/UA-EdgeTranslator](https://github.com/OPCFoundation/UA-EdgeTranslator) - An industrial edge gateway application that translates from proprietary protocols (including OCPP) to OPC UA using W3C Web of Things thing descriptions (C# · ⭐ 91).
- [Majkel-code/GE_EvChargingStation](https://github.com/Majkel-code/GE_EvChargingStation) - GE_EvChargingStation is a FastAPI-based charger and vehicle simulator for running configurable EV charging sessions with logging and optional Electron monitoring (Python · ⭐ 1 · 💤 2025-06-05).
- [api-evangelist/tae-technologies](https://github.com/api-evangelist/tae-technologies) - TAE Technologies is a company profile repository about aneutronic p-B11 fusion energy, related life sciences, and power solutions (⭐ 0).
- [M4GNV5/charging-infrastructure-review-paper](https://github.com/M4GNV5/charging-infrastructure-review-paper) - A SECURWARE 2024 review paper on fast charging communication technologies and cybersecurity for EV charging (TeX · ⭐ 0).
- [api-evangelist/schaeffler](https://github.com/api-evangelist/schaeffler) - Schaeffler is a company profile repository documenting a German automotive and industrial supplier of bearings, powertrain components, chassis applications, and e-mobility systems, with no public APIs documented (⭐ 0).
- [Shargus/MasterThesis](https://github.com/Shargus/MasterThesis) - Master thesis project on real-time state-of-health estimation for electric vehicle battery packs using time-series extrinsic regression (TeX · ⭐ 0 · 💤 2022-12-26).
- [OpenChargingCommunity/OpenChargingCommunityAPI](https://github.com/OpenChargingCommunity/OpenChargingCommunityAPI) - Open Charging Community API is an API project for EV charging community functionality (C# · ⭐ 0 · 💤 2025-05-29).

#### Analytics

- [JohnApollos/boda-emobility-viability-engine](https://github.com/JohnApollos/boda-emobility-viability-engine) - A Streamlit-based data analytics and spatial optimization platform for modeling battery swap network expansion and credit default risk assessment in Kenya's electric motorcycle sector (Python · ⭐ 0).

#### Backend

- [kamwro/emobility-backend-app](https://github.com/kamwro/emobility-backend-app) - A NestJS and PostgreSQL backend application for managing e-mobility data, including charging station types and charging stations (TypeScript · ⭐ 0).

#### Carbon accounting

- [geraldkombo/albedo](https://github.com/geraldkombo/albedo) - ALBEDO is a Laravel carbon accounting platform that calculates, aggregates, and prepares registration documents for emission reductions from Kenyan e-mobility fleets (PHP · ⭐ 1).

#### Charging station placement optimization

- [h-waldschmidt/olsp](https://github.com/h-waldschmidt/olsp) - OLSP is a C++ benchmark tool for optimizing electric-vehicle charging station placement on road graphs using hierarchical hub labeling (C++ · ⭐ 0 · 💤 2024-03-20).

#### Cost and travel estimation

- [gerritnowald/electric-car-tools](https://github.com/gerritnowald/electric-car-tools) - Electric car tools provides Tkinter/matplotlib and HTML/JavaScript calculators for estimating EV travel time with DC charging and comparing annual EV versus combustion vehicle operating costs (Jupyter Notebook · ⭐ 1).

#### Driver App

- [SAP-samples/e-mobility-driver-app](https://github.com/SAP-samples/e-mobility-driver-app) - A SAP CAP and Vue.js PWA for EV drivers to manage charging access badges, start and stop charging sessions, find stations, and view charging history, costs, and consumption (TypeScript · ⭐ 1).

#### EEBUS Libraries

- [arasgungore/EEBUS-in-Java](https://github.com/arasgungore/EEBUS-in-Java) - Java library implementing the EEBUS protocol suite, including SHIP and SPINE, for communication and discovery between smart home and energy management devices (Java · ⭐ 10 · 💤 2024-01-30).

#### EEBUS Simulator

- [Coretech-Innovations/EEBus-Hub](https://github.com/Coretech-Innovations/EEBus-Hub) - EEBUS Hub is a testing and simulation framework for orchestrating virtual and real EEBUS actors in EV charging and energy-management integration scenarios (⭐ 10).

#### EEBUS energy management

- [enbility/cemd](https://github.com/enbility/cemd) - Cemd is a deprecated Go EEBUS Central Energy Manager implementation for home energy management and EV charging use cases (Go · ⭐ 12 · 🚫 deprecated · 💤 2024-06-29).

#### Electric bus planning and charging simulation

- [gtfs4ev/gtfs4ev](https://github.com/gtfs4ev/gtfs4ev) - GTFS4EV is a Python library and CLI for simulating electric bus fleet operations, charging demand, infrastructure needs, and impacts from GTFS transit data (Python · ⭐ 4).

#### Electric scooter fleet management

- [rescoot/sunshine](https://github.com/rescoot/sunshine) - Sunshine is a Rails web application and API for monitoring telemetry, tracking trips, managing users, and remotely controlling unu/librescoot electric scooters via MQTT (HTML · ⭐ 4 · 💤 2025-06-03).

#### Energy market analysis

- [Matthias-H-Git/European-Energy-Market-Analysis](https://github.com/Matthias-H-Git/European-Energy-Market-Analysis) - A data analytics project that examines relationships between European electricity markets, renewable generation, EV and heat pump adoption, and electricity price trends using public ENTSO-E and EUROSTAT data (Jupyter Notebook · ⭐ 0).

#### Firmware

- [bodems/controller-firmware](https://github.com/bodems/controller-firmware) - OpenWRT-based firmware build files for Raspberry Pi EV charging controllers following IEC 61851 (JavaScript · ⭐ 0 · 💤 2018-06-24).

#### Industrial protocol gateway

- [arcnode-io/ems-industrial-gateway](https://github.com/arcnode-io/ems-industrial-gateway) - Rust gateway that reads industrial grid/device protocols, derives measurements, and publishes unit-scoped samples and dispatch acknowledgements over MQTT (Rust · ⭐ 0).

#### Integration

- [flashg1/SolarCharger](https://github.com/flashg1/SolarCharger) - Home Assistant custom integration that optimizes electric vehicle charging based on available surplus solar energy (Python · ⭐ 16).
- [JustChr/HAgoe_steve](https://github.com/JustChr/HAgoe_steve) - Home Assistant integration providing smart-charging orchestration for go-e wallboxes by coordinating with SteVe (OCPP) backend and optimizing based on solar production, electricity prices, and home battery state (Python · ⭐ 0).

#### Libraries

##### Makefile

- [ChargePi/oscp-go](https://github.com/ChargePi/oscp-go) - A Go library providing auto-generated OSCP (Open Smart Charging Protocol) compatible server and client implementations for smart charging (⭐ 3).

#### Mobile app

- [sap-labs-france/ev-mobile](https://github.com/sap-labs-france/ev-mobile) - A React Native Android and iOS mobile app for managing electric vehicle charging stations through the Open e-Mobility backend (TypeScript · ⭐ 66 · 💤 2023-10-16).
- [powerly-ev/open-ev-charge-ios-app](https://github.com/powerly-ev/open-ev-charge-ios-app) - Powerly Open EV Charge is an open-source white-label iOS app for locating EV charging stations, signing in users, and viewing station availability, connector type, and pricing (Swift · ⭐ 2).

#### OCHP bridge

- [OpenChargingCloud/WWCP_OCHP](https://github.com/OpenChargingCloud/WWCP_OCHP) - A bridge enabling communication between WWCP entities and OCHP/OCHPdirect roaming and clearing-house implementations (C# · ⭐ 2).

#### Open Data

- [SFOE/ichtankestrom_Documentation](https://github.com/SFOE/ichtankestrom_Documentation) - Documentation for Switzerland’s national electromobility data infrastructure, providing real-time charging point availability and open data access for EV charging stations (⭐ 12).
- [knudmoeller/berlin-charging-stations](https://github.com/knudmoeller/berlin-charging-stations) - A Ruby/Makefile tool that downloads Berlin EV charging station data from a WFS GML source and converts it to CSV (Makefile · ⭐ 0 · 💤 2020-06-15).

#### Optimization

- [fneum/ev_chargingcoordination2017](https://github.com/fneum/ev_chargingcoordination2017) - A research codebase for robust cost-minimizing day-ahead scheduling of residential electric vehicle charging in low-voltage distribution networks under uncertainty (Python · ⭐ 123 · 💤 2018-06-09).

#### Platform

- [Michito49/evcc](https://github.com/Michito49/evcc) - Evcc is a locally-deployed extensible charge controller and energy management system for coordinating EV charging with renewable energy and home systems (HTML · ⭐ 0).

#### Security

- [OpenChargingCloud/PKI](https://github.com/OpenChargingCloud/PKI) - Open Charging Cloud PKI defines a graph-based, multi-signature quorum public key infrastructure for trust and secure communications in e-mobility (⭐ 3 · 💤 2023-08-02).
- [OpenChargingCommunity/PKI](https://github.com/OpenChargingCommunity/PKI) - Open Charging Community PKI defines a graph-based, quorum-controlled public key infrastructure for securing trust relationships in e-mobility (⭐ 0 · 💤 2023-08-02).

#### Site Assessment

- [mohsinali33226/Hamburg-fast-charging-gap-map](https://github.com/mohsinali33226/Hamburg-fast-charging-gap-map) - A GIS-based site assessment case study identifying underserved public fast-charging infrastructure gaps around Hamburg for CPO expansion planning (⭐ 0).

#### Smart energy and DER management

- [api-evangelist/enel-x](https://github.com/api-evangelist/enel-x) - Profile of Enel X smart energy and DER management services, including Enel X Way EV charging products and VPP Connect API integration for aggregating DERs into virtual power plants (⭐ 0).

#### Smart home integration

- [iobroker-community-adapters/ioBroker.kecontact](https://github.com/iobroker-community-adapters/ioBroker.kecontact) - IoBroker.kecontact is an ioBroker adapter that monitors and controls KEBA KeContact P20/P30 and BMW i wallboxes over their UDP protocol, including PV-surplus charging automation (JavaScript · ⭐ 10).
- [pottio/ioBroker.warp](https://github.com/pottio/ioBroker.warp) - IoBroker.warp is an ioBroker adapter that monitors and controls Tinkerforge WARP wallbox chargers over WebSockets (TypeScript · ⭐ 2 · 💤 2023-04-01).
- [JFK344/ioBroker.evsewifi](https://github.com/JFK344/ioBroker.evsewifi) - IoBroker.evsewifi is an ioBroker adapter that reads and controls data for EVSE-WiFi/SimpleEVSE wallboxes in smart home setups (JavaScript · ⭐ 1 · 💤 2023-11-18).

#### Smart-energy simulation

- [GreenCharge/gcsimulator](https://github.com/GreenCharge/gcsimulator) - GreenCharge Simulator is a containerized discrete-event simulation platform for modeling smart energy neighborhoods and integrating energy management schedulers (Python · ⭐ 0 · 💤 2022-02-10).

#### Vehicle API client

- [solectrus/ruze](https://github.com/solectrus/ruze) - RuZE is an unofficial Ruby client for the Renault ZE API that retrieves electric vehicle battery, mileage, charging, and location data (Ruby · ⭐ 2).

#### WWCP Library

- [OpenChargingCloud/WWCP_Core](https://github.com/OpenChargingCloud/WWCP_Core) - WWCP Core defines the core concepts, entities, data structures, and virtual component reference implementations for the World Wide Charging Protocol Suite used in EV charging and roaming networks (C# · ⭐ 7).

#### Wallbox firmware

- [BorisBrock/HeidelBridge](https://github.com/BorisBrock/HeidelBridge) - ESP32 firmware that connects Heidelberg wallboxes to WiFi and exposes Daheimladen-compatible, MQTT, REST, and OTA interfaces for home energy management integration (C · ⭐ 47).

#### Wallbox library

- [vlcty/TeslaWallbox](https://github.com/vlcty/TeslaWallbox) - A Go library for querying version, lifetime statistics, and live vitals from Gen 3 Tesla wallboxes (Go · ⭐ 0 · 💤 2022-12-09).

### Uncategorized

- [vnbaaij/OCPP.NET](https://github.com/vnbaaij/OCPP.NET)
- [glurp/dynamicReverseProxy](https://github.com/glurp/dynamicReverseProxy) - Exemple of a solution for dynamic Http/WS reverse proxy with nginx and /etc/hosts manipulation (⭐ 2 · 💤 2021-09-09).
- [dattaphani899-create/voltgrid](https://github.com/dattaphani899-create/voltgrid) - Full-stack EV Charge Point Operator platform with OCPP 1.6, Node.js, WebSocket, SQLite and live dashboard (HTML · ⭐ 0).
- [shiks2/charlie](https://github.com/shiks2/charlie) - Lightweight OCPP 1.6J Central System in Go. Open-source alternative to heavy Java-based CSMS servers. Powers Volt — hosted EV charging infrastructure management (Makefile · ⭐ 0).
- [salah2277/steve](https://github.com/salah2277/steve) - A macOS CLI tool for automating application control and testing via the Accessibility API, unrelated to EV charging (Swift · ⭐ 0).
