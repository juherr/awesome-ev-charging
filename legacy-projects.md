# Legacy & pending EV charging projects

Projects kept out of the main [README](README.md) list — which only features actively maintained, curated tools — but preserved here for reference: dormant, archived, or deprecated projects, plus candidates still awaiting curation.

## Dormant (146)

### OCPP

#### Server

- [thoughtworks/maeve-csms](https://github.com/thoughtworks/maeve-csms) - An experimental EV Charging Station Management System implementing OCPP 1.6j/2.0.1 and ISO 15118-2 Plug and Charge (OCPP 1.6, 2.0.1 · Go · ⭐ 119 · 💤 2024-08-01).
- [sap-labs-france/ev-server](https://github.com/sap-labs-france/ev-server) - Node.js backend server that collects and stores charging station data via OCPP protocol and provides a REST API for charging station management, real-time monitoring, remote control, smart charging, and billing integration (TypeScript · ⭐ 176 · 💤 2024-08-07).
- [yuncitys/YunCharging](https://github.com/yuncitys/YunCharging) - An open-source enterprise charging station management platform with OCPP 1.5/2.0 support, billing system, and web/mobile interfaces built on SpringCloud Alibaba and Vue (OCPP 1.5, 2.0 · Java · ⭐ 75 · 💤 2024-10-17).
- [gregszalay/ocpp-csms](https://github.com/gregszalay/ocpp-csms) - A microservice-based OCPP 2.0.1 Charging Station Management System server implemented in Go with GCP Pub/Sub messaging, Firestore persistence, and mutual TLS authentication (OCPP 2.0.1 · Go · ⭐ 59 · 💤 2023-02-11).
- [digitaltwinconsortium/iot-edge-ocpp-central-system](https://github.com/digitaltwinconsortium/iot-edge-ocpp-central-system) - An OCPP V1.5 and V1.6 Central System server deployed as a Docker container on Azure IoT Edge that manages charging stations, user authentication, billing, and reservations with MQTT telemetry integration (C# · ⭐ 27 · 💤 2025-05-09).
- [v-bodnar/ocpp-server](https://github.com/v-bodnar/ocpp-server) - Java OCPP server with GUI and CLI modes, REST API, and SSL/TLS support (Java · ⭐ 24 · 💤 2021-11-20).
- [codelabsab/ocpp-csms-server](https://github.com/codelabsab/ocpp-csms-server) - OCPP v2.0.1 WebSocket server implementation for charging station management systems (archived) (OCPP 2.0.1 · Rust · ⭐ 20 · 💤 2024-08-29).
- [ChagataiDuru/OCPP-Framework](https://github.com/ChagataiDuru/OCPP-Framework) - A Charge Station Management System implementing OCPP protocols with NestJS microservices backend, RabbitMQ messaging, and AngularJS frontend for managing multiple charge stations (TypeScript · ⭐ 13 · 💤 2024-01-25).
- [gio-del/eMall](https://github.com/gio-del/eMall) - A JavaScript web application platform providing e-Mobility Service Provider (eMSP) and Charging Point Operator (CPO) management with integrated OCPP server functionality for charging point communication and session booking (JavaScript · ⭐ 11 · 💤 2023-06-06).
- [stromenergy/strom](https://github.com/stromenergy/strom) - An open source OCPP charging management system that enables Lightning Network payments for EV charging sessions with Nostr protocol integration (OCPP 1.6, 2.0.1 · Go · ⭐ 11 · 💤 2023-05-20).
- [morosanag/OCPP-Project](https://github.com/morosanag/OCPP-Project) - OCPP-compliant server for managing electrical charging stations via WebSocket and SOAP interfaces (Java · ⭐ 10 · 💤 2017-03-19).
- [elifTech/ocpp-tester](https://github.com/elifTech/ocpp-tester) - An OCPP server providing a web dashboard and WebServices endpoints for managing charging point connections (JavaScript · ⭐ 7 · 💤 2019-05-22).
- [jagwarthegreat/EVerythingcharge](https://github.com/jagwarthegreat/EVerythingcharge) - OCPP 1.6 and 2.0.1 compliant management system for charge point operators with distributed server architecture for WebSocket connection handling across multiple worker nodes (⭐ 6 · 💤 2024-03-21).
- [smartenergycontrol-be/ocpp-proxy](https://github.com/smartenergycontrol-be/ocpp-proxy) - An OCPP proxy server designed as a Home Assistant add-on that enables multiple backend services to share a single EV charger while maintaining homeowner control (OCPP 1.6, 2.0.1, 2.1 · Python · ⭐ 6 · 💤 2025-09-29).
- [Llocer/llocer_cso](https://github.com/Llocer/llocer_cso) - A Charging Station Management System (CSMS) and Charging Point Operator (CPO) implementation that manages OCPP-enabled electric vehicle charging stations and supports eMSP roaming via OCPI (Java · ⭐ 5 · 💤 2022-05-01).
- [ocpp-balanz/balanz](https://github.com/ocpp-balanz/balanz) - A feature-rich OCPP server implementation for Charging Station Management Systems (CSMS) and Local Controllers with smart charging capabilities (Python · ⭐ 5 · 💤 2025-07-01).
- [siddharthsabron/ocpp](https://github.com/siddharthsabron/ocpp) - An OCPP WebSocket server implementation in TypeScript for EV charging station communication (TypeScript · ⭐ 5 · 💤 2024-04-18).
- [zzerk/OCPP-J-Server](https://github.com/zzerk/OCPP-J-Server) - An early-stage OCPP 1.6J server implementation written in Node.js (OCPP 1.6 · JavaScript · ⭐ 5 · 💤 2022-02-12).
- [alexs-sh/dummy-central-system](https://github.com/alexs-sh/dummy-central-system) - Fast OCPP Central System in Rust for testing ISO 15118 certificate operations (Rust · ⭐ 4 · 💤 2021-08-11).
- [LastProject-ESIEE/OCPPConfigurationServer](https://github.com/LastProject-ESIEE/OCPPConfigurationServer) - A web application for configuring and managing OCPP-enabled electric vehicle charging points (Java · ⭐ 1 · 💤 2025-07-28).

#### Simulator

- [kubarskii/OCPP-J-CP-Simulator](https://github.com/kubarskii/OCPP-J-CP-Simulator) - A simple charging point (CP) simulator implementing OCPP 1.6 with configurable endpoint registration and a basic user interface (OCPP 1.6 · HTML · ⭐ 100 · 💤 2020-04-08).
- [glurp/ocpp_simulator](https://github.com/glurp/ocpp_simulator) - Ruby gem for simulating OCPP charge points with support for SOAP dialogs, multiple connectors, and batch operations (Ruby · ⭐ 21 · 💤 2018-06-26).
- [matth-x/MicroOcppSimulator](https://github.com/matth-x/MicroOcppSimulator) - A desktop and web-based simulator for testing OCPP charging station client implementations against OCPP servers, featuring a graphical user interface for development and demonstration (C++ · ⭐ 171 · 💤 2025-07-26).
- [victormunoz/OCPP-1.6-Chargebox-Simulator](https://github.com/victormunoz/OCPP-1.6-Chargebox-Simulator) - A charging point simulator implementing OCPP 1.6 protocol with configurable central station connection and standard message events (OCPP 1.6 · HTML · ⭐ 122 · 💤 2024-07-08).
- [ShellRechargeSolutionsEU/docile-charge-point](https://github.com/ShellRechargeSolutionsEU/docile-charge-point) - A Scala-based scriptable simulator for OCPP 1.5/1.6/2.0 charge points with a domain-specific language for behavior scripting and testing (OCPP 1.5, 1.6, 2.0 · Scala · ⭐ 82 · 💤 2022-01-20).
- [oglimmer/scriptable-ocpp-chargepoint-simulator](https://github.com/oglimmer/scriptable-ocpp-chargepoint-simulator) - A scriptable OCPP 1.6J chargepoint simulator with REST API, HTML frontend, and JavaScript batch automation support (OCPP 1.6 · TypeScript · ⭐ 72 · 💤 2023-05-16).
- [vasyas/charger-simulator](https://github.com/vasyas/charger-simulator) - OCPP charging station simulator supporting OCPP/J 1.6 and OCPP/SOAP 1.5 (TypeScript · ⭐ 68 · 💤 2025-04-09).
- [JavaIsJavaScript/OCPP-2.0-CP-Simulator](https://github.com/JavaIsJavaScript/OCPP-2.0-CP-Simulator) - A simple OCPP 2.0 charge point simulator for testing against OCPP 2.0 compliant charging management systems (OCPP 2.0 · HTML · ⭐ 65 · 💤 2024-01-02).
- [evbox/station-simulator](https://github.com/evbox/station-simulator) - A Java-based OCPP charging station simulator that implements the OCPP protocol and communicates with Charging Station Management Systems via WebSocket (Java · ⭐ 64 · 💤 2024-02-27).
- [JavaIsJavaScript/OCPP-1.6-CP-Simulator](https://github.com/JavaIsJavaScript/OCPP-1.6-CP-Simulator) - Node.js-based OCPP 1.6 charge point simulator supporting bidirectional communication with a central system for testing (OCPP 1.6 · JavaScript · ⭐ 43 · 💤 2019-01-18).
- [ZeMorfe/nodejs_ocpp16_client](https://github.com/ZeMorfe/nodejs_ocpp16_client) - A Node.js implementation of an OCPP 1.6 charge point client with a web interface for testing central system communication (OCPP 1.6 · JavaScript · ⭐ 40 · 💤 2020-03-23).
- [ShellRechargeSolutionsEU/ocpp-charger](https://github.com/ShellRechargeSolutionsEU/ocpp-charger) - Standalone OCPP charger simulator implemented as Scala/Akka actors, supporting OCPP-SOAP and OCPP-J (JSON/WebSocket) protocols (Scala · ⭐ 38 · 💤 2021-08-17).
- [extrawest/Charge-Point-Simulator-via-OCPP-2.0.1](https://github.com/extrawest/Charge-Point-Simulator-via-OCPP-2.0.1) - Java application that simulates multiple OCPP 2.0.1 charge points connecting via WebSocket to a central system, designed for load testing and CSMS validation (OCPP 2.0, 2.0.1 · Java · ⭐ 37 · 💤 2023-03-07).
- [romfrolov/station-emulator](https://github.com/romfrolov/station-emulator) - An OCPP 2.0 charging station simulator that connects to a Charging Station Management System over WebSocket (OCPP 2.0 · Rust · ⭐ 18 · 💤 2023-06-21).
- [TECHS-Technological-Solutions/ocpp-simulator](https://github.com/TECHS-Technological-Solutions/ocpp-simulator) - An OCPP charge point simulator built on the mobilityhouse/ocpp library for testing OCPP implementations (Python · ⭐ 17 · 💤 2022-08-29).
- [extrawest/BDD-Charge-Point-Tester-via-OCPP-J-](https://github.com/extrawest/BDD-Charge-Point-Tester-via-OCPP-J-) - A Cucumber-based OCPP 1.6 charge point simulator framework that enables behavioral testing of Central System implementations through predefined OCPP message exchanges (OCPP 1.6 · Java · ⭐ 15 · 💤 2023-03-17).
- [Lamerat/OCPP-Charge-Point-Simulator](https://github.com/Lamerat/OCPP-Charge-Point-Simulator) - OCPP JSON-1.6 charge point simulator implementing boot notification, authorization, transactions, meter values, and remote control operations (JavaScript · ⭐ 13 · 💤 2025-01-29).
- [m-villalilla/VirtualChargePoint](https://github.com/m-villalilla/VirtualChargePoint) - A virtual OCPP charging point application for testing OCPP server implementations through GUI or programmatic API (Java · ⭐ 11 · 💤 2018-07-14).
- [ocpp-balanz/ocppsim](https://github.com/ocpp-balanz/ocppsim) - An OCPP v1.6 charge point simulator with WebSocket command interface for testing OCPP central systems (OCPP 1.6 · Python · ⭐ 8 · 💤 2025-06-16).
- [yohannlog/OCPP_ChargingStation_2_0_1](https://github.com/yohannlog/OCPP_ChargingStation_2_0_1) - A Java-based OCPP 2.0.1 charging station simulator with a JavaFX graphical interface for testing central management systems (Java · ⭐ 7 · 💤 2022-05-20).
- [chargegrid/abusive-charge-point](https://github.com/chargegrid/abusive-charge-point) - An OCPP 1.5-j charge point simulator that sends randomized protocol messages to test and load-test OCPP backoffice systems (OCPP 1.5 · Clojure · ⭐ 6 · 💤 2017-08-02).
- [elumobility/elu-twins](https://github.com/elumobility/elu-twins) - An open-source e-mobility ecosystem simulator providing OCPP 1.6/2.0.1 charging point emulation and electric vehicle telemetry simulation for testing charge management systems (OCPP 1.6, 2.0.1 · Python · ⭐ 4 · 💤 2024-09-12).
- [esiebert/v16-fcs](https://github.com/esiebert/v16-fcs) - A OCPP 1.6 charging station simulator with REST API for controlling behavior and testing CSMS edge cases (Python · ⭐ 3 · 💤 2025-06-23).
- [JavaIsJavaScript/OCPP-J-CP-Simulator](https://github.com/JavaIsJavaScript/OCPP-J-CP-Simulator) - A simple charge point simulator for OCPP 1.6 protocol (OCPP 1.6 · HTML · ⭐ 2 · 💤 2018-05-14).
- [ges0909/ocpp-charge-point-simulator-dashboard](https://github.com/ges0909/ocpp-charge-point-simulator-dashboard) - Web-based OCPP charge point simulator dashboard built with Deno, Vue 3 and Vuetify (TypeScript · ⭐ 1 · 💤 2024-11-03).
- [LastProject-ESIEE/dummy-chargepoint](https://github.com/LastProject-ESIEE/dummy-chargepoint) - A Java command-line application that emulates a charging point using the OCPP protocol for manual testing (Java · ⭐ 1 · 💤 2025-08-26).

#### Libraries

##### C

- [parikshittyagi/ocppClientJ1.6](https://github.com/parikshittyagi/ocppClientJ1.6) - C implementation of an OCPP-J 1.6 client library for connecting charging points to OCPP-compliant management servers via WebSockets (OCPP 1.6 · ⭐ 54 · 💤 2020-05-17).

##### C++

- [EVerest/libocpp](https://github.com/EVerest/libocpp) - A C++ library implementing OCPP 1.6, 2.0.1, and 2.1 protocols for charging station firmware with ISO 15118 Plug and Charge support (OCPP 1.6, 2.0.1, 2.1 · ⭐ 151 · 💤 2026-04-27).
- [markrpo/ocppws](https://github.com/markrpo/ocppws) - A C++ library implementing the Open Charge Point Protocol (OCPP) over WebSockets (⭐ 2 · 💤 2025-09-01).

##### Erlang

- [wfvining/ocpp](https://github.com/wfvining/ocpp) - An Erlang/OTP library implementing the Open Charge Point Protocol (OCPP) 2.0.1 as a protocol layer for charging station management systems (⭐ 11 · 💤 2025-02-24).

##### Go

- [lorenzodonini/ocpp-go](https://github.com/lorenzodonini/ocpp-go) - Go library implementing OCPP 1.6 and 2.0.1 protocols for charge points and central systems (OCPP 1.6, 2.0.1 · ⭐ 375 · 💤 2025-08-24).
- [iclay/ocpp](https://github.com/iclay/ocpp) - A Go-based OCPP 1.6 network communication library with WS/WSS support and pluggable architecture for integrating charging stations with central management systems (OCPP 1.6, 2.0 · ⭐ 79 · 💤 2022-06-23).
- [voltbras/go-ocpp](https://github.com/voltbras/go-ocpp) - A Go library implementing OCPP v1.5 (SOAP) and v1.6 (JSON) protocols with support for both charge point and central system roles (OCPP 1.5, 1.6 · ⭐ 49 · 💤 2022-02-16).
- [gregszalay/ocpp-csms-common-types](https://github.com/gregszalay/ocpp-csms-common-types) - A library providing common type definitions and shared models for OCPP-based Charging Station Management System implementations (⭐ 5 · 💤 2022-10-14).
- [CoderSergiy/ocpp16-go](https://github.com/CoderSergiy/ocpp16-go) - A Go library implementing OCPP 1.6 (JSON-based) protocol for communication between charging stations and central charging systems (OCPP 1.6 · ⭐ 4 · 💤 2022-08-04).
- [gregszalay/ocpp-messages-go](https://github.com/gregszalay/ocpp-messages-go) - Go library providing data types for OCPP 2.0.1 protocol messages and message wrappers (OCPP 2.0.1 · ⭐ 3 · 💤 2024-10-13).

##### Java

- [Llocer/llocer_ocpp](https://github.com/Llocer/llocer_ocpp) - A base library for building OCPP 2.0.1 server implementations (⭐ 6 · 💤 2022-04-18).

##### JavaScript

- [elifTech/cpd-ocpp](https://github.com/elifTech/cpd-ocpp) - JavaScript library providing OCPP 1.6 protocol abstractions with server and client implementations and request validation (OCPP 2.0 · ⭐ 68 · 💤 2022-12-06).
- [aymen-mouelhi/ocpp-js](https://github.com/aymen-mouelhi/ocpp-js) - JavaScript library implementing the Open Charge Point Protocol (OCPP 1.2/1.5) for building central systems and charging point applications (⭐ 62 · 💤 2021-08-09).
- [psnehanshu/ocpp-task-manager](https://github.com/psnehanshu/ocpp-task-manager) - A transport-agnostic Node.js framework for building OCPP-compliant charge points, central systems, and simulators (OCPP 1.6 · ⭐ 12 · 💤 2023-12-23).

##### Python

- [villekr/ocpp-asgi](https://github.com/villekr/ocpp-asgi) - Python library extending ocpp to provide an ASGI-compliant interface for implementing event-driven OCPP Central Systems (OCPP 2.0.1 · ⭐ 23 · 💤 2022-12-23).
- [OrangeTux/zeegat](https://github.com/OrangeTux/zeegat) - A Python library providing a service-based routing and middleware framework for handling OCPP protocol messages (⭐ 5 · 💤 2022-06-26).

##### Rust

- [choudhary463/rocpp](https://github.com/choudhary463/rocpp) - A modular Rust library implementing OCPP 1.6 with client-side support, a charger simulator, and conformance testing (OCPP 1.6, 2.0 · ⭐ 13 · 💤 2025-06-04).
- [OrangeTux/rauts](https://github.com/OrangeTux/rauts) - A Rust library for building OCPP servers and clients with handler-based request routing (⭐ 4 · 💤 2023-01-04).
- [tux-evse/ocpp-binding-rs](https://github.com/tux-evse/ocpp-binding-rs) - Rust library implementing OCPP 1.6 and 2.0.1 charger stack functionality using the afb-binding micro service architecture (OCPP 1.6, 2.0.1 · ⭐ 2 · 💤 2024-11-18).

##### Scala

- [ShellRechargeSolutionsEU/ocpp](https://github.com/ShellRechargeSolutionsEU/ocpp) - Scala library implementing Open Charge Point Protocol (OCPP) versions 1.5, 1.6, and partial 2.0 with JSON/WebSocket transport and message serialization (OCPP 1.2, 1.5, 1.6, 2.0 · ⭐ 212 · 💤 2021-10-08).
- [IHomer/scala-ocpp](https://github.com/IHomer/scala-ocpp) - Scala library implementing the OCPP 1.5/1.6 network protocol with WebSocket/JSON transport, providing message types, serialization, and remote procedure call handling (OCPP 1.2, 1.5, 1.6, 2.0 · ⭐ 21 · 💤 2024-05-27).

##### TypeScript

- [extrawest/ocpp-node-ts](https://github.com/extrawest/ocpp-node-ts) - TypeScript library implementing OCPP 2.0.1 JSON protocol with server (central system) and client (charging point) components (OCPP 1.6, 2.0.1 · ⭐ 19 · 💤 2023-09-14).
- [sepych/ocpp-ts](https://github.com/sepych/ocpp-ts) - A TypeScript library implementing OCPP 1.6 in JSON format for building charging point and central management system applications (OCPP 1.6 · ⭐ 9 · 💤 2021-12-26).
- [evorada/browser-ocpp-client](https://github.com/evorada/browser-ocpp-client) - Browser-based OCPP 1.6 client library for connecting JavaScript/TypeScript applications to OCPP-compliant charging station management systems (OCPP 1.6 · ⭐ 6 · 💤 2022-04-15).
- [node-ocpp/core](https://github.com/node-ocpp/core) - A Node.js TypeScript library for implementing OCPP Central Systems with WebSocket transport and OCPP 1.6 message type definitions (OCPP 1.2, 2.0.1 · ⭐ 2 · 💤 2023-09-25).
- [ChilG/zod-ocpp](https://github.com/ChilG/zod-ocpp) - TypeScript library providing Zod-based validation schemas for OCPP 1.6J protocol messages and payloads (OCPP 1.6 · ⭐ 1 · 💤 2024-08-02).

#### Misc

- [aws-solutions-library-samples/guidance-for-modernizing-electric-vehicle-charging-on-aws](https://github.com/aws-solutions-library-samples/guidance-for-modernizing-electric-vehicle-charging-on-aws) - AWS reference architecture and deployment guidance for building an OCPP Gateway that proxies charging points to AWS IoT Core services for Charging Point Operator applications (OCPP 2.0, 2.0.1 · TypeScript · ⭐ 94 · 💤 2025-02-28).
- [gennadiygnezdilov/ocpp-1.6J-example-request-response](https://github.com/gennadiygnezdilov/ocpp-1.6J-example-request-response) - OCPP 1.6J protocol documentation with example request and response messages for charging station communication (OCPP 1.6 · ⭐ 29 · 💤 2024-08-08).
- [OCPP-fuzzer/ocpp-fuzzer](https://github.com/OCPP-fuzzer/ocpp-fuzzer) - OCPP 1.6 fuzzer that generates and validates test messages to verify charging infrastructure implementation robustness (OCPP 1.6, 2.0 · Python · ⭐ 29 · 💤 2025-07-27).
- [gregszalay/ocpp-charging-station](https://github.com/gregszalay/ocpp-charging-station) - OCPP 2.0.1-compliant charging station firmware for ESP32-based devices (C++ · ⭐ 22 · 💤 2022-10-14).
- [Anmirazik/Open-Source-Ev-charger-End-to-End-Solution](https://github.com/Anmirazik/Open-Source-Ev-charger-End-to-End-Solution) - A step-by-step integration guide for connecting Everest-based EV chargers to open-source CSMS platforms via OCPP (⭐ 19 · 💤 2023-12-07).
- [digitaltwinconsortium/OCPP-Charging-Dashboard](https://github.com/digitaltwinconsortium/OCPP-Charging-Dashboard) - A dockerized web dashboard for displaying EV charging station status based on the OCPP standard data model (JavaScript · ⭐ 17 · 💤 2023-06-27).
- [brandonprry/VolatileOCPP](https://github.com/brandonprry/VolatileOCPP) - A .NET-based tool that runs Open Charge Alliance OCPP compliance test scenarios to validate charging station management system implementations (OCPP 1.6 · C# · ⭐ 12 · 💤 2025-03-18).
- [DeltaVetal26/SteVe-OCPP-HTTP-Client](https://github.com/DeltaVetal26/SteVe-OCPP-HTTP-Client) - An HTTP client that enables external systems to remotely execute OCPP commands on charging points managed by the SteVe OCPP server (PHP · ⭐ 12 · 💤 2023-10-07).
- [tux-evse/ocpp-csms](https://github.com/tux-evse/ocpp-csms) - Podman containerization configuration and orchestration toolkit for deploying the maeve-csms OCPP charging station management system (OCPP 1.6 · Shell · ⭐ 4 · 💤 2023-10-17).
- [vorchunpaul/ocpp-gateway](https://github.com/vorchunpaul/ocpp-gateway) - A gateway that translates OCPP 2.0.1 messages from charge points to OCPP 1.6 format for backward compatibility with older charging management systems (OCPP 2.0.1 · Python · ⭐ 4 · 💤 2022-02-28).
- [IdahoLabUnsupported/OCPP-2.0.1-Interim-KPI-Calculator](https://github.com/IdahoLabUnsupported/OCPP-2.0.1-Interim-KPI-Calculator) - A tool for parsing OCPP 2.0.1 logs and calculating aggregate interim Key Performance Indicators from charging point event data (OCPP 2.0.1 · Python · ⭐ 2 · 💤 2026-06-18).

### OCPI

#### Server

- [energywebfoundation/ocn-node](https://github.com/energywebfoundation/ocn-node) - An OCPI v2.2 server implementing a decentralized roaming hub to broker charging-related requests and communications between platform parties (OCPI 2.2 · Kotlin · ⭐ 5 · 💤 2024-12-23).

#### Simulator

- [energywebfoundation/ocn-tools](https://github.com/energywebfoundation/ocn-tools) - Mock OCPI server toolkit for testing E-Mobility Service Provider and Charge Point Operator implementations (TypeScript · ⭐ 11 · 💤 2022-04-26).
- [MTES-MCT/ocpi-playground](https://github.com/MTES-MCT/ocpi-playground) - A Docker-based playground environment for testing and demonstrating OCPI server topologies using CPO and eMSP instances (Python · ⭐ 6 · 💤 2026-03-27).

#### Libraries

##### Java

- [extrawest/Extrawest-OCPI-2.2.1-CPO-Server](https://github.com/extrawest/Extrawest-OCPI-2.2.1-CPO-Server) - OCPI 2.2.1 library providing pre-built models, controllers, and APIs for Java developers implementing Charging Point Operator applications (OCPI 2.1.1, 2.2, 2.2.1 · ⭐ 11 · 💤 2024-03-11).
- [Llocer/llocer_ocpi](https://github.com/Llocer/llocer_ocpi) - A free and open-source Java library providing OCPI 2.2.1 sender/receiver interfaces and HTTP handling for implementing OCPI nodes (OCPI 2.2.1 · ⭐ 10 · 💤 2024-09-29).
- [extrawest/Extrawest-OCPI-2.2.1-EMSP-Server](https://github.com/extrawest/Extrawest-OCPI-2.2.1-EMSP-Server) - Java library providing pre-built models and controllers to implement OCPI 2.2.1-compliant E-Mobility Service Provider (eMSP) applications (OCPI 2.1.1, 2.2, 2.2.1 · ⭐ 7 · 💤 2024-02-29).
- [extrawest/Extrawest-OCPI-2.2.1-CPO-Client](https://github.com/extrawest/Extrawest-OCPI-2.2.1-CPO-Client) - Java client library for OCPI 2.2.1 CPO Server, providing programmatic API access for charging point operator operations (OCPI 2.2.1 · ⭐ 5 · 💤 2023-11-23).

##### JavaScript

- [hyndex/node-ocpi](https://github.com/hyndex/node-ocpi) - A Node.js library providing data models and validation for OCPI (Open Charge Point Interface) protocol entities and operations in EV charging systems (⭐ 7 · 💤 2023-12-26).

##### PHP

- [ChargeMap/ocpi-protocol](https://github.com/ChargeMap/ocpi-protocol) - PHP library implementing OCPI request/response classes and models for eMSP and CPO interfaces with PSR-7 compatibility (⭐ 22 · 💤 2021-11-12).
- [Codivores/Laravel-OCPI-eMSP](https://github.com/Codivores/Laravel-OCPI-eMSP) - A Laravel PHP package implementing the OCPI 2.1.1 protocol for e-Mobility Service Providers (eMSPs) (⭐ 2 · 💤 2025-06-27).

##### Python

- [extrawest/extrawest_ocpi](https://github.com/extrawest/extrawest_ocpi) - Python library for implementing the Open Charge Point Interface (OCPI 2.1.1 and 2.2.1) protocol using FastAPI (⭐ 11 · 💤 2025-07-16).
- [NOWUM/pyOCPI](https://github.com/NOWUM/pyOCPI) - A Python Flask-RESTX library for implementing OCPI 2.2 REST interfaces (⭐ 10 · 💤 2025-03-19).
- [hyndex/OCPIPyBridge](https://github.com/hyndex/OCPIPyBridge) - A Python library providing Pydantic models and validation for the Open Charge Point Interface (OCPI) protocol (⭐ 4 · 💤 2023-12-26).

##### Scala

- [ShellRechargeSolutionsEU/ocpi-endpoints](https://github.com/ShellRechargeSolutionsEU/ocpi-endpoints) - Scala library implementing common OCPI protocol endpoints with Akka-HTTP and pluggable JSON serialization support (OCPI 2.1.1 · ⭐ 15 · 💤 2021-07-29).

##### TypeScript

- [energywebfoundation/ocn-bridge](https://github.com/energywebfoundation/ocn-bridge) - An OCPI library that bridges Charge Point Operator backoffice systems to Open Charging Network nodes via a pluggable API interface (⭐ 5 · 💤 2022-04-07).
- [andreibesleaga/ocpi-sdk](https://github.com/andreibesleaga/ocpi-sdk) - TypeScript/JavaScript SDK library providing convenient access to the OCPI REST API for EV charging applications, with integrated MCP server support for AI communication (⭐ 3 · 💤 2026-02-09).
- [niklam/ocpi-types](https://github.com/niklam/ocpi-types) - A TypeScript library providing data transfer objects and enums for the OCPI 2.2.1 specification with built-in validation support (OCPI 2.2.1 · ⭐ 3 · 💤 2025-06-18).

##### Other

- [GLCharge/ocpi](https://github.com/GLCharge/ocpi) - Go client library for the OCPI (Open Charge Point Interface) protocol, auto-generated from OpenAPI specifications using oapi-codegen (OCPI 2.1.1, 2.2.1 · ⭐ 11 · 💤 2024-04-19).

#### Misc

- [plugoinc/ocpi-openapi](https://github.com/plugoinc/ocpi-openapi) - OpenAPI specification definition and documentation tooling for the OCPI charging protocol (⭐ 5 · 💤 2024-02-19).
- [kelseymok/ocpi-implementation](https://github.com/kelseymok/ocpi-implementation) - A proof-of-concept OCPI Charge Detail Record (CDR) implementation using Kafka for OCPP event processing and DynamoDB for storage, with a REST API gateway (Python · ⭐ 4 · 💤 2023-03-23).
- [energywebfoundation/ocn-registry](https://github.com/energywebfoundation/ocn-registry) - Ethereum smart contracts for managing the Open Charging Network registry, enabling OCPI parties and node operators to register and discover each other on blockchain-based networks (OCPI 2.2 · Java · ⭐ 4 · 💤 2022-06-13).
- [ocpi-register/ocpi-register](https://github.com/ocpi-register/ocpi-register) - A federated registry of OCPI Location module implementations enabling discovery of electric vehicle charge points across operators (⭐ 3 · 💤 2020-04-28).
- [suroorhussain/ev-protocols](https://github.com/suroorhussain/ev-protocols) - A Docusaurus documentation site providing translated and navigable reference material for the OCPI (Open Charge Point Interface) protocol specification (⭐ 2 · 💤 2023-08-16).

### iso15118

#### Plug&Charge

- [OpenV2G/OpenV2G-base](https://github.com/OpenV2G/OpenV2G-base) - Open-source base infrastructure providing PKI and certificate management components for ISO 15118 Plug and Charge implementations (⭐ 9 · 💤 2017-08-17).
- [charinev/opnc](https://github.com/charinev/opnc) - Open-source specification of a protocol for ISO 15118 Plug&Charge authentication and secure communication in EV charging ecosystems (JavaScript · ⭐ 25 · 💤 2025-08-14).

#### Misc

- [EVerest/libiso15118](https://github.com/EVerest/libiso15118) - C++ library implementation of ISO 15118-20, ISO 15118-2, and DIN70121 charging protocols with support for DC/AC charging, Plug&Charge, and multiple operational modes (C++ · ⭐ 34 · 💤 2026-02-17).
- [endland/sniffer-iso15118vse](https://github.com/endland/sniffer-iso15118vse) - Wireshark plugin for capturing and analyzing ISO 15118 Vendor-Specific Elements in 802.11 management frames for EV-EVSE association debugging (⭐ 23 · 💤 2019-11-04).
- [FlUxIuS/V2GInjector](https://github.com/FlUxIuS/V2GInjector) - Penetration testing tool for capturing and injecting V2G packets on PowerLine Communication networks to assess security vulnerabilities in electric vehicles and charging stations (Python · ⭐ 143 · 💤 2024-12-19).
- [Ecognize/openv2g](https://github.com/Ecognize/openv2g) - OpenV2G is a C library implementing the ISO 15118 and DIN 70121 vehicle-to-grid (V2G) communication protocol stack (C · ⭐ 25 · 💤 2021-01-30).
- [endland/wifi15118](https://github.com/endland/wifi15118) - Software implementation of ISO 15118 part 8-compliant SECC and EVCC controllers enabling wireless (802.11n) discovery and association between electric vehicles and charging equipment (⭐ 21 · 💤 2019-10-22).
- [rcuquemelle/ISO15118_4_TestEnv](https://github.com/rcuquemelle/ISO15118_4_TestEnv) - ISO 15118 HLC/V2G conformance test environment emulating an EV controller to validate charging station implementations (⭐ 17 · 💤 2022-07-29).
- [tux-evse/iso15118-simulator-rs](https://github.com/tux-evse/iso15118-simulator-rs) - An ISO 15118 simulator providing JSON/REST/WebSocket APIs to simulate electric vehicle and charging equipment communication protocols (Rust · ⭐ 13 · 💤 2025-03-07).
- [tux-evse/iso15118-encoders](https://github.com/tux-evse/iso15118-encoders) - C libraries for encoding and decoding ISO 15118 protocol messages (DIN, ISO-2, ISO-20) using EXI format, generated from XSD schemas using cbexigen (C · ⭐ 10 · 💤 2025-03-07).
- [nvdungx/ISO15118_TestUI](https://github.com/nvdungx/ISO15118_TestUI) - A web-based UI for ISO 15118 conformance testing, built with Vue.js and Django (Python · ⭐ 7 · 💤 2022-07-31).
- [tux-evse/iso15118-encoders-rs](https://github.com/tux-evse/iso15118-encoders-rs) - Rust library providing ISO 15118 EXI message encoding and decoding APIs for electric vehicle charging protocols (Rust · ⭐ 5 · 💤 2025-03-07).
- [tux-evse/josev-binding-rs](https://github.com/tux-evse/josev-binding-rs) - An AFB binding that exposes the Josev ISO 15118-2 stack to application frameworks for charging station implementations (Rust · ⭐ 1 · 💤 2025-02-20).
- [tux-evse/iso15118-binding-rs](https://github.com/tux-evse/iso15118-binding-rs) - Rust binding for ISO 15118 protocol using AFB framework v4 (Rust · ⭐ 1 · 💤 2024-07-25).

### OICP

#### Libraries

##### Other

- [GLCharge/oicp-client-go](https://github.com/GLCharge/oicp-client-go) - Go client library for OICP (Open Intercharge Protocol) auto-generated from OpenAPI specifications (⭐ 6 · 💤 2024-04-19).

### Other

#### Analytics & data

- [openchargemap/ocm-data](https://github.com/openchargemap/ocm-data) - Deprecated repository containing gzipped JSON snapshots of Open Charge Map's charging point database and reference data, moved to a more efficient per-POI export format (Shell · ⭐ 29 · 🚫 deprecated · 💤 2021-11-05).
- [ruchikumari-jha/Electric-Vehicle-Population-Data](https://github.com/ruchikumari-jha/Electric-Vehicle-Population-Data) - A dataset tracking the distribution, characteristics, and adoption trends of registered electric vehicles in a region, including battery capacity and charging infrastructure details (⭐ 9 · 💤 2025-05-02).
- [chargex-consortium/OCPP-2.0.1-Interim-KPI-Calculator](https://github.com/chargex-consortium/OCPP-2.0.1-Interim-KPI-Calculator) - A tool that processes OCPP 2.0.1 log data to calculate aggregate interim Key Performance Indicators (⭐ 4 · 💤 2025-05-19).
- [ptachukf/ev-data](https://github.com/ptachukf/ev-data) - Data analysis project analyzing electric vehicle popularity worldwide by cross-referencing EV specifications with Wikipedia pageviews and other open datasets (Ruby · ⭐ 1 · 💤 2025-09-02).

#### Charging management system

- [sap-labs-france/ev-dashboard](https://github.com/sap-labs-france/ev-dashboard) - An Angular web dashboard for real-time monitoring and management of EV charging stations, supporting remote control, billing, smart charging, and roaming integration (TypeScript · ⭐ 78 · 💤 2024-08-02).
- [motown-io/motown](https://github.com/motown-io/motown) - Apache2-licensed platform providing modular architecture for EV charge infrastructure (Java · ⭐ 44 · 💤 2019-02-01).
- [thepaulcooper/victron-openEVSE](https://github.com/thepaulcooper/victron-openEVSE) - Node-Red controller that manages openEVSE charging based on available solar generation and battery storage state in a Victron energy system (⭐ 6 · 💤 2021-10-23).
- [gregszalay/ocpp-csms-frontend](https://github.com/gregszalay/ocpp-csms-frontend) - Frontend application for an OCPP Charging Station Management System (TypeScript · ⭐ 4 · 💤 2022-10-10).
- [vishalrj291/Smart-EV-Charge-Monitoring](https://github.com/vishalrj291/Smart-EV-Charge-Monitoring) - An IoT-based platform that monitors, controls, and optimizes electric vehicle charging in real time with data analytics, safety detection, and remote management capabilities (⭐ 3 · 💤 2025-09-22).

#### Developer tools & libraries

- [agruenb/micro-ocpp-dashboard](https://github.com/agruenb/micro-ocpp-dashboard) - A lightweight web-based dashboard for monitoring and controlling OCPP charging stations via the MicroOcpp library, optimized for microcontroller deployment (CSS · ⭐ 13 · 💤 2024-10-16).
- [Namoshek/OpenChargeMeteringFormat](https://github.com/Namoshek/OpenChargeMeteringFormat) - A .NET library that provides parsing and verification for Open Charge Metering Format (OCMF) messages (C# · ⭐ 5 · 💤 2025-01-20).
- [abhishandilya/ocpp.ai](https://github.com/abhishandilya/ocpp.ai) - An open source chat user interface template for building AI-powered conversational applications with OpenAI or compatible APIs (TypeScript · ⭐ 1 · 💤 2023-11-07).
- [EVerest/everest-framework](https://github.com/EVerest/everest-framework) - EVerest framework component that manages module dependencies, validates configurations against manifests, and orchestrates charging system startup via MQTT communication (C++ · ⭐ 29 · 💤 2025-12-04).

#### EVSE firmware

- [slezoric/ISO15118-car-charging](https://github.com/slezoric/ISO15118-car-charging) - A repository containing the main files for a car charging station project (C · ⭐ 39 · 💤 2017-06-05).

#### Energy management

- [pieterh/energy-management-system](https://github.com/pieterh/energy-management-system) - Home Energy Management System that monitors, configures, and automates EV chargers, smart meters, and solar panels for residential energy optimization (C# · ⭐ 26 · 💤 2024-04-24).

#### Home automation

- [foxriver76/ioBroker.ocpp](https://github.com/foxriver76/ioBroker.ocpp) - IoBroker adapter that integrates OCPP 1.6-compliant wallboxes into the ioBroker smart home automation platform for monitoring and control (TypeScript · ⭐ 19 · 💤 2023-02-09).
- [CreasolTech/DomBusEVSE_ha](https://github.com/CreasolTech/DomBusEVSE_ha) - Home Assistant configuration files for the DomBusEVSE hardware EVSE module to manage a DIY smart EV charging wallbox (⭐ 10 · 💤 2023-09-04).

#### Maps & route planning

- [formidablae/EV_Route_Planner](https://github.com/formidablae/EV_Route_Planner) - A Vue.js web application that calculates optimal EV routes with intermediate charging station stops based on vehicle autonomy, consuming OpenChargeMap and OpenStreetMap APIs (Vue · ⭐ 27 · 💤 2024-04-08).

#### Mobile app

- [acervenky/ev_charge_tracker](https://github.com/acervenky/ev_charge_tracker) - Flutter mobile app that tracks charge cycles and battery statistics for EV scooters, storing all data locally on the device (Dart · ⭐ 1 · 💤 2021-11-02).
- [Rajkumar1963/EV_WEBS](https://github.com/Rajkumar1963/EV_WEBS) - A full-stack web application enabling EV drivers to discover and book nearby charging stations using geolocation and map services (⭐ 1 · 💤 2023-10-15).
- [pedroeverett/ev-charge-tracker](https://github.com/pedroeverett/ev-charge-tracker) - A personal, mobile-oriented Next.js web app backed by MongoDB for tracking EV charging (JavaScript · ⭐ 1 · 💤 2022-11-30).
- [iaewing/ev-charge-tracker](https://github.com/iaewing/ev-charge-tracker) - An iOS and web application for tracking electric vehicle charging events, costs, and efficiency metrics with offline support and interactive analytics visualization (TypeScript · ⭐ 1 · 💤 2025-06-01).

#### Specifications & documentation

- [EVerest/EVerest-archived](https://github.com/EVerest/EVerest-archived) - Archived repository that redirects to the active EVerest open-source EV charging infrastructure software project at github.com/EVerest/EVerest (⭐ 346 · 💤 2026-03-16).
- [e-clearing-net/OCHP](https://github.com/e-clearing-net/OCHP) - Specification and documentation repository for the Open Clearing House Protocol (OCHP), a protocol connecting market actors in electric vehicle charging infrastructure clearing operations (XSLT · ⭐ 49 · 💤 2024-05-02).

### Uncategorized

- [ChargeMap/autocharge-vehicles-database](https://github.com/ChargeMap/autocharge-vehicles-database) (⭐ 1 · 💤 2025-02-18)

## To refine (250 projects)

### OCPP

#### Server

- [gennadiygnezdilov/php-ocpp-1.6J](https://github.com/gennadiygnezdilov/php-ocpp-1.6J) - A PHP WebSocket server implementing the OCPP 1.6J protocol for managing electric vehicle charging stations with MySQL backend support (OCPP 1.6 · PHP · ⭐ 15 · 💤 2024-08-09).
- [opencpo/opencpo](https://github.com/opencpo/opencpo) - An open-source EV charging platform providing an OCPP 1.6/2.0.1-compliant CSMS server, network management dashboard, driver PWA, and virtual charger simulator (OCPP 1.6, 2.0.1 · Shell · ⭐ 12).
- [psnehanshu/ocpp-central-system-boilerplate-code](https://github.com/psnehanshu/ocpp-central-system-boilerplate-code) - Node.js boilerplate code for implementing OCPP central system (server) functionality (JavaScript · ⭐ 6 · 💤 2022-12-13).
- [Llocer/llocer_ev_examples](https://github.com/Llocer/llocer_ev_examples) - Example implementations of OCPP servers, OCPI nodes, and a simulated OCPP charging station client in Java and Python (Java · ⭐ 5 · 💤 2022-07-16).
- [u2ware/ocpp-boot-server](https://github.com/u2ware/ocpp-boot-server) - Spring Boot-based OCPP server supporting versions 1.6, 2.0.1, and 2.1 with pluggable handler architecture and console UI (Java · ⭐ 5).
- [opencpo/opencpo-core](https://github.com/opencpo/opencpo-core) - OCPP 1.6j and 2.0.1 Central System (CSMS) with built-in PKI for ISO 15118 Plug & Charge, OCPI 2.2.1 roaming, and profile-driven charger compatibility (OCPP 1.6, 2.0.1 · Python · ⭐ 5).
- [apostoldevel/ocpp-css](https://github.com/apostoldevel/ocpp-css) - An OCPP 1.6-J and OCPP 2.0.1 Central System server with a public sandbox for testing charging stations via live message logs and direct command console (OCPP 1.5, 1.6, 2.0.1 · ⭐ 4).
- [Cyb0rg42/Charger-OCPP](https://github.com/Cyb0rg42/Charger-OCPP) - A suite of OCPP 1.6-J services comprising a production-capable Central System, a charge-point simulator, and a transparent proxy for inspecting and routing messages between charge points and backend systems (OCPP 1.6 · Python · ⭐ 4).
- [ruslan-hut/evsys](https://github.com/ruslan-hut/evsys) - A Go-based OCPP 1.6J Central System server that manages electric vehicle charging points, users, and charging sessions (OCPP 1.6, 2.0.1 · Go · ⭐ 3).
- [mschmitt/shocpp](https://github.com/mschmitt/shocpp) - A Bash-based OCPP 1.6 charging management backend supporting RFID-based authorization and remote charge control (Shell · ⭐ 3).
- [BashTheDog/elecq-ocpp-ha](https://github.com/BashTheDog/elecq-ocpp-ha) - Home Assistant custom integration that embeds an OCPP 2.0.1 WebSocket server for local control of Elecq AU101/AE106 EV chargers (OCPP 2.0.1 · Python · ⭐ 3).
- [OpenChargingCloud/CSMSApp](https://github.com/OpenChargingCloud/CSMSApp) - OCPP Charging Station Management System application built with Electron for testing and certification of e-mobility protocols and vendor extensions (OCPP 2.1 · TypeScript · ⭐ 2).
- [FlipSoftware/moovolt-mvp](https://github.com/FlipSoftware/moovolt-mvp) - An OCPP-based Charging Station Management System for managing and controlling electric vehicle chargers across platforms and vendors (TypeScript · ⭐ 2 · 💤 2024-09-19).
- [seanlee0923/csms-platform](https://github.com/seanlee0923/csms-platform) - OCPP 1.6/2.0.1/2.1 CSMS server and Kubernetes Operator with Redis distributed session management and MySQL persistence (OCPP 1.6, 2.0.1, 2.1 · Go · ⭐ 1).
- [hpxix/Aviator-Beta](https://github.com/hpxix/Aviator-Beta) - An OCPP 2.0.1 compliant charging station management server implemented in TypeScript for Node.js (OCPP 2.0.1 · TypeScript · ⭐ 1 · 💤 2024-11-28).
- [Anmirazik/OCPP1.6J-Server-Nodered](https://github.com/Anmirazik/OCPP1.6J-Server-Nodered) - An OCPP 1.6J server prototype built with Node-RED that relays charging station messages to Thingsboard via MQTT for visualization and remote control (OCPP 1.6 · ⭐ 1 · 💤 2023-11-25).
- [DJBenson/GivEVC-OCPPv2](https://github.com/DJBenson/GivEVC-OCPPv2) - An OCPP 1.6J server and multi-user management portal for GivEnergy EV chargers, providing web UI, REST API, real-time state monitoring, charging control, scheduling, and RFID tag management in a self-hosted Docker container (OCPP 1.6 · Python · ⭐ 1).
- [loafoe/go-occp-server](https://github.com/loafoe/go-occp-server) - An OCPP 1.6-J Central System server written in Go for managing and controlling EV chargers like Wallbox (OCPP 1.6 · Go · ⭐ 1).
- [hilman2/easy-ocpp](https://github.com/hilman2/easy-ocpp) - OCPP 1.6J/2.0.1 self-hosted charging station management server (CSMS) for small businesses, providing wallbox management, RFID authentication, charging limits, and transaction reporting (OCPP 1.5, 1.6, 2.0.1 · Rust · ⭐ 1).
- [hupe1980/emob](https://github.com/hupe1980/emob) - Open-source Rust CSMS and roaming node implementing OCPP, OCPI, and OICP protocols with Eichrecht metering compliance and billing integration (OCPP 1.6, 2.0.1, 2.1 · Rust · ⭐ 0).
- [ChargePi/chargeflow-registry](https://github.com/ChargePi/chargeflow-registry) - An OCPP schema registry service with gRPC and MCP APIs for validating CPMS and EV charger compliance and cross-vendor compatibility across OCPP versions (OCPP 1.6, 2.0.1, 2.1 · Go · ⭐ 0).
- [ZANNABI-LAB/swapve](https://github.com/ZANNABI-LAB/swapve) - OCPP 2.1 battery swapping server (CSMS) and libraries for the JVM (OCPP 2.0.1, 2.1 · Kotlin · ⭐ 0).
- [dattaphani899-create/voltgrid](https://github.com/dattaphani899-create/voltgrid) - Node.js-based OCPP 1.6 Charge Point Operator platform with real-time WebSocket dashboard for managing electric vehicle charging stations (HTML · ⭐ 0).
- [shiks2/charlie](https://github.com/shiks2/charlie) - A lightweight OCPP 1.6J Central System implementation in Go that serves as an open-source alternative to Java-based CSMS servers (Makefile · ⭐ 0).
- [ekkehard-lutz/wallbox-manager](https://github.com/ekkehard-lutz/wallbox-manager) - Home Assistant integration providing an OCPP server for discovering and managing EV charging stations with metering, session tracking, and charge profile dispatch (OCPP 1.6, 2.0.1, 2.1 · Python · ⭐ 0).
- [Lansharkza/jtech-grid-control](https://github.com/Lansharkza/jtech-grid-control) - Self-hosted OCPP 1.6J central management system and dashboard for EV chargers with live monitoring, charging schedules, solar integration, and usage tracking (OCPP 1.6 · Python · ⭐ 0).
- [chethanbhatbs/CMS](https://github.com/chethanbhatbs/CMS) - OCPP 1.6 charging station management system for CPOs, with a Python WebSocket backend and a React dashboard for managing stations, live sessions, remote start/stop, CRM, and RBAC (OCPP 1.6 · JavaScript · ⭐ 0 · 💤 2026-06-15).
- [humoge7502/VoltHub-CSMS](https://github.com/humoge7502/VoltHub-CSMS) - OCPP 1.6J Charging Station Management System with Oracle 23ai for billing, TimescaleDB for telemetry, and race-tested simulator fleet (OCPP 1.6, 2.0.1 · JavaScript · ⭐ 0).
- [steve-white/ocpp-server](https://github.com/steve-white/ocpp-server) - A Golang-based OCPP v1.6 Charge Station Management System (CSMS) server that manages charging points via websocket and provides a REST API for remote charger commands (OCPP 1.6 · Go · ⭐ 0).
- [alex89rm/ha-ocpp](https://github.com/alex89rm/ha-ocpp) - A Home Assistant integration implementing an OCPP 1.6/2.0/2.1 server for managing OCPP-compatible charging stations, users, and charging limits (OCPP 1.6, 2.0.1, 2.1 · Python · ⭐ 0).
- [MihaelaAghirculesei/chargehub-csms](https://github.com/MihaelaAghirculesei/chargehub-csms) - Java/Spring Boot OCPP 1.6J charging station management system (CSMS) server for the ChargeHub dashboard (OCPP 1.6, 2.0.1 · Java · ⭐ 0).
- [tiger19935/ocpp-bench](https://github.com/tiger19935/ocpp-bench) - OCPP 1.6J and 2.0.1 central system server with an integrated charging station simulator for load testing and failure scenario validation (OCPP 1.6, 2.0.1 · Python · ⭐ 0).

#### Simulator

- [sap-labs-france/ev-simulator](https://github.com/sap-labs-france/ev-simulator) - OCPP-J charging stations simulator for testing and development of e-mobility charging infrastructure (⭐ 39 · 💤 2024-01-04).
- [TumbleOwlee/ferrowl](https://github.com/TumbleOwlee/ferrowl) - A Rust TUI/CLI application that simulates Modbus devices (server, client, monitor) and OCPP charging infrastructure (charging stations and central systems) (OCPP 1.6, 2.0.1, 2.1 · Rust · ⭐ 5).
- [u2ware/ocpp-boot-client](https://github.com/u2ware/ocpp-boot-client) - Spring Boot-based OCPP 1.6/2.0.1/2.1 client emulator with customizable message handlers and console UI (Java · ⭐ 5).
- [rohittiwari-dev/ocpp-ws-simulator](https://github.com/rohittiwari-dev/ocpp-ws-simulator) - A browser-based OCPP 1.6, 2.0.1, and 2.1 charge point simulator for testing CSMS implementations (OCPP 1.6, 2.0.1, 2.1 · TypeScript · ⭐ 5).
- [ruslan-hut/ocpp-emu](https://github.com/ruslan-hut/ocpp-emu) - A web-based EV charging station emulator supporting OCPP 1.6, 2.0.1, and 2.1 protocols (OCPP 1.6, 2.0.1, 2.1 · Go · ⭐ 4).
- [srcfl/device-simulator](https://github.com/srcfl/device-simulator) - A multi-protocol device simulator supporting OCPP, Modbus TCP, and MQTT for testing solar inverters, batteries, EV chargers, and energy meters (Go · ⭐ 3).
- [psnehanshu/charge-point-simulator](https://github.com/psnehanshu/charge-point-simulator) - A chargepoint simulator using OCPP 1.5 JSON to simulate multiple concurrent charging sessions (JavaScript · ⭐ 2 · 💤 2020-10-09).
- [dumanburak/ocpp-client-demo](https://github.com/dumanburak/ocpp-client-demo) - An asynchronous Python OCPP 1.6J Charge Point simulator that demonstrates realistic transaction workflows communicating with a CSMS via WebSocket (OCPP 1.6 · Python · ⭐ 2 · 💤 2025-10-10).
- [autimit/ocpp-zig-poc](https://github.com/autimit/ocpp-zig-poc) - Zig-based simulator for OCPP 1.6 EV charging sessions with mocked data and energy/cost calculations for host-based charging networks (Zig · ⭐ 2 · 💤 2025-07-02).
- [brunoluiz/ocpp-server-tool](https://github.com/brunoluiz/ocpp-server-tool) - OCPP 1.5 SOAP Central System server simulator written in Java that sends commands to real charging stations (OCPP 1.5 · Java · ⭐ 2 · 💤 2017-03-03).
- [MuhammedAlmaz/ma-ocpp-simulator](https://github.com/MuhammedAlmaz/ma-ocpp-simulator) - An OCPP 1.6 charging point simulator with a web UI for testing backend charging management systems, deployable via Docker (OCPP 1.6, 2.0.1 · TypeScript · ⭐ 1 · 💤 2024-05-09).
- [LearnEVCharging/rey-virtual-ev-charger](https://github.com/LearnEVCharging/rey-virtual-ev-charger) - Browser-based OCPP 1.6/2.0.1/2.1 charge-point simulator that connects to external CSMS or runs with a built-in demo (OCPP 1.6, 2.0.1, 2.1 · JavaScript · ⭐ 1).
- [opencpo/opencpo-charger-farm](https://github.com/opencpo/opencpo-charger-farm) - Virtual OCPP charger simulator for load-testing EV charging infrastructure with stress scenarios, realistic physics, and Plug & Charge support (OCPP 1.6, 2.0.1 · Python · ⭐ 1).
- [soneeee22000/go-charger-ramp](https://github.com/soneeee22000/go-charger-ramp) - A Go simulator of an OCPP charger fleet that demonstrates concurrent supervision and graceful shutdown patterns (OCPP 1.6 · Go · ⭐ 0).
- [mysmartlife-helsinki/ev-charging](https://github.com/mysmartlife-helsinki/ev-charging) - An OCPP charge control unit (ECU/VCCU) implementation developed under the EU's Horizon 2020 MySmartLife project (⭐ 0 · 💤 2019-06-01).
- [MarekPokornyOva/EvChargerSimulator](https://github.com/MarekPokornyOva/EvChargerSimulator) - A browser-hosted simulator for electric vehicle chargers that communicates via the OCPP 1.6J protocol (OCPP 1.6 · TypeScript · ⭐ 0 · 💤 2025-05-06).
- [eveys-mobility/Simulator](https://github.com/eveys-mobility/Simulator) - An OCPP 1.6 charging station simulator with web UI for developing, testing, and load-testing CSMS back-office systems against realistic station behaviors (OCPP 1.6 · TypeScript · ⭐ 0).
- [crakashp2905-hub/CyberDeception-EVSE](https://github.com/crakashp2905-hub/CyberDeception-EVSE) - An OCPP-based honeypot simulating EV charging stations paired with machine-learning models for detecting attacks using network traffic, host events, and power consumption data (Jupyter Notebook · ⭐ 0).
- [LeonardoTakachi/ev-charging-station-manager](https://github.com/LeonardoTakachi/ev-charging-station-manager) - Python simulator for EV charging session management with smart power distribution and simulated OCPP messages (Python · ⭐ 0).
- [JuanFerInc/charge-point-console-simulator](https://github.com/JuanFerInc/charge-point-console-simulator) - A browser-based OCPP 1.6-J charge point simulator for testing CSMS integration without physical hardware (OCPP 1.6 · JavaScript · ⭐ 0).
- [LeonardoTakachi/Sprint02-DSA](https://github.com/LeonardoTakachi/Sprint02-DSA) - OCPP protocol simulator for electric vehicle charging management with power balancing and dynamic hourly pricing (Python · ⭐ 0).

#### Libraries

##### C

- [kiranj26/MicroOCPP-on-STM32F4](https://github.com/kiranj26/MicroOCPP-on-STM32F4) - STM32F4 firmware implementation of OCPP 1.6 protocol using MicroOCPP library with TLS-secured WebSocket communication and FreeRTOS task management for EV charger hardware (OCPP 1.6 · ⭐ 13 · 💤 2025-01-27).

##### C\#

- [fabyr/ocpp-sharp](https://github.com/fabyr/ocpp-sharp) - C# library implementing OCPP protocol (1.6, 2.0.1) with message classes and server/client infrastructure for charging station communication (OCPP 1.6, 2.0.1 · ⭐ 9).

##### Go

- [road-labs/ocpps-go](https://github.com/road-labs/ocpps-go) - Go library implementing the OCPP-S (SOAP over HTTP) protocol binding with client and server support (OCPP 1.5, 1.6 · ⭐ 2).
- [JohnMaddison/ocpp-go](https://github.com/JohnMaddison/ocpp-go) - A Go library for building OCPP 1.6 and 2.1 clients and servers with typed message structs and WebSocket support (OCPP 1.6, 2.1 · ⭐ 1).
- [feightree/gocpp](https://github.com/feightree/gocpp) - A Go library providing spec-compliant types and message definitions for OCPP 1.6, 2.0.1, and 2.1 (OCPP 1.6, 2.0.1, 2.1 · ⭐ 1).
- [aasanchez/ocpp16j](https://github.com/aasanchez/ocpp16j) - Go library for parsing, validating, and marshalling OCPP-J 1.6 RPC messages (Call, CallResult, and CallError) (OCPP 1.6 · ⭐ 0).
- [seanlee0923/ocpp](https://github.com/seanlee0923/ocpp) - A type-safe Go library for OCPP-J providing CSMS WebSocket server and Charging Station client implementations for OCPP 1.6, 2.0.1, and 2.1 (OCPP 1.6, 2.0.1, 2.1 · ⭐ 0).

##### Java

- [wang007/e-iot](https://github.com/wang007/e-iot) - Vert.x-based Java library implementing OCPP 1.6/2.0/2.1 and YunKuaiChong charging protocols as Maven dependencies (OCPP 1.6, 2.0.1, 2.1 · ⭐ 30 · 💤 2025-10-10).
- [steve-community/ocpp-jaxb](https://github.com/steve-community/ocpp-jaxb) - Java library providing JAXB data model mappings for OCPP protocol versions 1.2 through 2.1, covering all requests and responses between central systems and charge points (OCPP 1.2, 1.5, 1.6, 2.0.1, 2.1 · ⭐ 20).
- [zonnedev/ocpp-java](https://github.com/zonnedev/ocpp-java) - Java 25 library providing strongly typed models and strict JSON codec for OCPP 1.6 JSON and OCPP 2.0.1 protocol messages (OCPP 1.6, 2.0.1 · ⭐ 0).

##### JavaScript

- [adriandotdev/ocpp-central-system](https://github.com/adriandotdev/ocpp-central-system) - A NodeJS library providing core command implementations for OCPP (Open Charge Point Protocol) communication between charging stations and central management systems (⭐ 1 · 💤 2024-12-12).
- [romfrolov/ocpp-util](https://github.com/romfrolov/ocpp-util) - JavaScript utility library for validating OCPP primitive datatypes and accessing OCPP 1.6/2.0 enumerations (OCPP 1.6, 2.0 · ⭐ 0 · 💤 2022-12-30).

##### Kotlin

- [Jaypatelbond/ocpp-kotlin](https://github.com/Jaypatelbond/ocpp-kotlin) - Kotlin/Android client library providing type-safe OCPP 1.6 and 2.0.1 protocol support with WebSocket, coroutines, and auto-reconnect capabilities (OCPP 1.6, 2.0.1 · ⭐ 3).

##### PHP

- [solutionforest/ocpp-php](https://github.com/solutionforest/ocpp-php) - PHP library for implementing OCPP 1.6 and 2.0.1 to build charging stations and central systems (OCPP 1.6, 2.0, 2.0.1 · ⭐ 5).

##### Python

- [QuecPython/OCPP-v1.6](https://github.com/QuecPython/OCPP-v1.6) - A Python library implementing the OCPP 1.6 JSON protocol for constructing charging stations and charge points (OCPP 1.6 · ⭐ 12 · 💤 2025-04-30).
- [javierojan/askacharge-python](https://github.com/javierojan/askacharge-python) - Python SDK for the askacharge.com EV charging management platform, providing client-side access to OCPP/OCPI-based charger and session management with webhook signature verification (OCPP 1.6, 2.0.1 · ⭐ 0).
- [Polyconseil/ocpp-codec](https://github.com/Polyconseil/ocpp-codec) - A Python library for encoding and decoding OCPP 1.6 and 2.0 messages with dataclass definitions and JSON serialization utilities (⭐ 0 · 💤 2020-06-01).

##### Rust

- [flowionab/ocpp-types](https://github.com/flowionab/ocpp-types) - A strongly typed Rust library implementing OCPP message types for versions 1.6J, 2.0.1, and 2.1 with no_std support and allocation-free field bounds (OCPP 1.6, 2.0.1, 2.1 · ⭐ 0).

##### Scala

- [ShellRechargeSolutionsEU/ocpp-soap](https://github.com/ShellRechargeSolutionsEU/ocpp-soap) - A Scala library providing OCPP 1.2 and 1.5 support with SOAP-based RPC messaging (OCPP 1.2, 1.5 · ⭐ 3 · 💤 2020-06-12).

##### TypeScript

- [rohittiwari-dev/ocpp-ws-io](https://github.com/rohittiwari-dev/ocpp-ws-io) - TypeScript OCPP library providing type-safe WebSocket RPC client and server implementations with clustering, session management, and ecosystem tools for smart charging and simulation (OCPP 1.6, 2.0.1, 2.1 · ⭐ 4).
- [rohittiwari-dev/ocpp-smart-charge-engine](https://github.com/rohittiwari-dev/ocpp-smart-charge-engine) - TypeScript library for distributing grid power among OCPP chargers using SetChargingProfile with pluggable constraint-solving strategies (OCPP 1.6, 2.0.1, 2.1 · ⭐ 1).

#### Misc

- [ChargePi/ChargePi](https://github.com/ChargePi/ChargePi) - Deprecated Raspberry Pi-based OCPP 1.6 charging point with multiple EVSE connectors, relay control, and power metering (OCPP 1.6, 2.0.1 · Python · ⭐ 27 · 🚫 deprecated · 💤 2024-07-25).
- [vnbaaij/OCPP.NET](https://github.com/vnbaaij/OCPP.NET) - An OCPP 1.6 / OCPP 1.6J (JSON) related project that ships no description or README stating its specific purpose (C# · ⭐ 10 · 💤 2020-12-27).
- [Llocer/llocer_ocpp_json](https://github.com/Llocer/llocer_ocpp_json) - A collection of JSON schemas that define the structure of OCPP 2.0.1 protocol messages, with tooling to generate language-specific bindings (e.g. Java POJOs) (OCPP 2.0.1 · ⭐ 3 · 💤 2022-04-22).
- [eva-sean/oye-proxy](https://github.com/eva-sean/oye-proxy) - A transparent OCPP proxy that enables real-time monitoring, logging, and owner control of electric vehicle chargers independently of charging management systems (OCPP 1.6, 2.0.1 · JavaScript · ⭐ 3).
- [alexs-sh/tom](https://github.com/alexs-sh/tom) - Python converter for translating OCPP messages between SOAP and JSON formats, enabling charging stations and central systems using different OCPP versions to communicate (OCPP 1.5 · Python · ⭐ 3 · 💤 2024-06-22).
- [glurp/dynamicReverseProxy](https://github.com/glurp/dynamicReverseProxy) - A dynamic HTTP/WebSocket reverse proxy using Nginx and Lua scripting that routes OCPP charging equipment requests to their assigned backend systems by extracting equipment identifiers from request payloads (⭐ 2 · 💤 2021-09-09).
- [electroop-engineering/electroop-ev-charging-platform](https://github.com/electroop-engineering/electroop-ev-charging-platform) - Documentation, public API examples, and MCP server for Electroop's OCPP 1.6J/2.0.1/2.1 and OCPI 2.2.1 EV charging platform (CPMS, eMSP, payment integration) (OCPP 1.6, 2.0.1, 2.1 · ⭐ 1).
- [OpenChargingCloud/DynamicQRCodes.Android](https://github.com/OpenChargingCloud/DynamicQRCodes.Android) - An Android testing and validation application for OCPP v2.1 secure dynamic QR-codes used in ad-hoc payment at charging stations (OCPP 2.1 · Kotlin · ⭐ 1).
- [cbrandlehner/ocpp-fanout](https://github.com/cbrandlehner/ocpp-fanout) - OCPP 1.6-J proxy that fans out a single wallbox connection to multiple CSMS backends with vendor shims and command allowlisting (OCPP 1.6 · Python · ⭐ 1).
- [mjasinskee/emob-ocpp-slides](https://github.com/mjasinskee/emob-ocpp-slides) - A presentation on modeling OCPP charging stations as an Actor System (JavaScript · ⭐ 1 · 💤 2022-12-07).
- [opencpo/opencpo-admin](https://github.com/opencpo/opencpo-admin) - A FastAPI web dashboard for managing OCPP-connected EV charging networks, with features for charger control, session monitoring, PKI management, and operator authentication (HTML · ⭐ 1).
- [javierojan/awesome-ocpp](https://github.com/javierojan/awesome-ocpp) - A curated awesome list of Open Charge Point Protocol (OCPP) resources including servers, libraries, simulators, roaming protocols, and standards (OCPP 1.5, 1.6, 2.0, 2.0.1, 2.1 · ⭐ 0).
- [matiebird/ocular-ocpp-compatibility-relay](https://github.com/matiebird/ocular-ocpp-compatibility-relay) - A WebSocket compatibility relay for Home Assistant that bridges Ocular LTE Plus V3 chargers to the Home Assistant OCPP integration to resolve connection stability issues (OCPP 1.6 · Python · ⭐ 0).
- [kccricket/grizzle-ocpp-proxy](https://github.com/kccricket/grizzle-ocpp-proxy) - Proxy that repairs malformed OCPP frames from Grizzl-E chargers and forwards them to an OCPP server, deployable as a Home Assistant add-on or Docker container (OCPP 1.6 · Python · ⭐ 0).
- [chankinwui/OCPP7ROS](https://github.com/chankinwui/OCPP7ROS) - A gateway connecting OCPP 2.0.1 (EV charging) and ROS 2 (robotics) protocols with included simulators for electric vehicles, chargers, and robots (⭐ 0 · 💤 2022-11-01).
- [Pyroil/Alfen_manager](https://github.com/Pyroil/Alfen_manager) - Python application for reading and controlling Alfen Eve charging stations via Modbus TCP and OCPP 1.6 with dynamic load balancing (OCPP 1.6 · Python · ⭐ 0).
- [purcell-lab/ha-bsv-settlement](https://github.com/purcell-lab/ha-bsv-settlement) - Home Assistant integration and mock wallet service for BSV-based settlement of OCPP electric vehicle charging sessions (Python · ⭐ 0).
- [SolarNetwork/solarnetwork-node-ocpp](https://github.com/SolarNetwork/solarnetwork-node-ocpp) - SolarNode plugins that add OCPP protocol support to the SolarNode distributed energy management platform (Java · ⭐ 0).
- [opencpo/opencpo-tester](https://github.com/opencpo/opencpo-tester) - An automated OCPP compliance testing tool that acts as a CSMS to validate charger firmware against OCPP 1.6 and 2.0.1 specifications and generates detailed PDF, HTML, and JSON test reports (OCPP 1.6, 2.0.1 · Python · ⭐ 0).
- [MostafaMoradii/eveys-console](https://github.com/MostafaMoradii/eveys-console) - Web-based system-administration console for OCPP gateways, offering real-time operator dashboards, charger inspection, alerts management, and configuration viewing via React interface backed by WebSocket subscriptions (TypeScript · ⭐ 0 · 💤 2026-05-14).
- [seanlee0923/ocpp-schema-gen](https://github.com/seanlee0923/ocpp-schema-gen) - An independent Go code generator that reproduces OCPP 1.6/2.0.1/2.1 types from official OCA JSON schemas to verify their byte-for-byte fidelity (OCPP 1.6, 2.0.1, 2.1 · Go · ⭐ 0).

### OCPI

#### Simulator

- [extrawest/bdd_ocpi_2.2.1_emsp](https://github.com/extrawest/bdd_ocpi_2.2.1_emsp) - BDD test framework using Cucumber that simulates OCPI 2.2.1 CPO-to-eMSP interactions to validate eMSP server compliance (OCPI 2.2.1 · Java · ⭐ 3 · 💤 2023-12-06).

#### Libraries

##### Java

- [extrawest/Extrawest-OCPI-2.2.1-EMSP-Client](https://github.com/extrawest/Extrawest-OCPI-2.2.1-EMSP-Client) - Java client library for OCPI 2.2.1 eMSP servers enabling integration with charging network roaming platforms (OCPI 2.2.1 · ⭐ 3 · 💤 2023-12-06).

##### Python

- [Hamza-nabil/ocpi-tariffs-py](https://github.com/Hamza-nabil/ocpi-tariffs-py) - A Python library for calculating and validating EV charging tariffs according to the OCPI 2.2.1 protocol (OCPI 2.2.1 · ⭐ 1).
- [codexistente/ocpi-python](https://github.com/codexistente/ocpi-python) - A Python library implementing the Open Charge Point Interface (OCPI) protocol for electric vehicle charging station management (OCPI 2.1.1, 2.2.1, 2.3.0 · ⭐ 0).

##### TypeScript

- [nitishagar/voltbase](https://github.com/nitishagar/voltbase) - A TypeScript normalisation library and discovery API for querying EV charging data from open sources including OCPI, DATEX II, OSM, and OCM (⭐ 0).

#### Misc

- [Llocer/llocer_ocpi_json](https://github.com/Llocer/llocer_ocpi_json) - JSON schema definitions for OCPI 2.2.1 protocol messages with Maven tooling to generate Java POJOs (OCPI 2.2.1 · Java · ⭐ 3 · 💤 2024-11-13).
- [alickjoe/test-ocpi](https://github.com/alickjoe/test-ocpi) - A web-based JSON validator tool that checks EV charging data conformity against OCPI protocol specifications across multiple versions (OCPI 2.1.1, 2.2.1, 2.3.0 · JavaScript · ⭐ 1).
- [BePower/bepower.github.io](https://github.com/BePower/bepower.github.io) - GitHub Pages website for bepower, an e-mobility and charging management platform supporting OCPI protocol (Ruby · ⭐ 1 · 💤 2022-08-18).
- [Ko1103/ocpi-mcp-server](https://github.com/Ko1103/ocpi-mcp-server) - An MCP (Model Context Protocol) server that provides OCPI documentation for use in AI coding assistants (TypeScript · ⭐ 0).
- [chargerdojo/dojo-connect](https://github.com/chargerdojo/dojo-connect) - A CLI connector that forwards OCPI requests from ChargerDojo to local endpoints through an outbound WebSocket tunnel, enabling testing without public internet exposure (⭐ 0).

### iso15118

#### Misc

- [uhi22/ccs32](https://github.com/uhi22/ccs32) - Arduino sketch implementing the ISO 15118 CCS vehicle-side protocol stack on ESP32 using HomePlug PLC communication (C · ⭐ 33 · 💤 2023-07-18).
- [cepsdev/v2g-guru-slac](https://github.com/cepsdev/v2g-guru-slac) - C++20 implementation and simulator of SLAC for ISO 15118-3 EVSE-EV matching (C++ · ⭐ 8 · 💤 2022-02-22).
- [konicst1/ChargeSploit](https://github.com/konicst1/ChargeSploit) - V2G security testing tool that simulates ISO 15118-2 and DIN SPEC 70121 charging station and vehicle endpoints (Python · ⭐ 6).
- [OpenChargingCloud/WWCP_ISO15118](https://github.com/OpenChargingCloud/WWCP_ISO15118) - C# .NET library implementing ISO/IEC 15118-2, -20, and -8 protocols for EV-to-charging-station communication, providing codec and session layers with Plug & Charge support and security testing tools (C# · ⭐ 6).
- [nvdungx/ISO15118_3_TestEnv](https://github.com/nvdungx/ISO15118_3_TestEnv) - A conformance test environment for ISO 15118-3 specification (HPGPpowerline and datalink layer) built in C++ with Raspberry Pi integration (C++ · ⭐ 5 · 💤 2024-06-03).
- [OpenChargingCloud/ISO15118ConformanceTests](https://github.com/OpenChargingCloud/ISO15118ConformanceTests) - Conformance and interoperability test suite for ISO/IEC 15118 (Plug & Charge) implementations, validating protocol stacks against standards and independent implementations (Josev, EVerest, EVDriveFlow, tux-evse) (C# · ⭐ 3).
- [majbthrd/V2Gredux](https://github.com/majbthrd/V2Gredux) - ISO 15118-2 EVSE emulator implementing charger-side protocol communication for testing electric vehicle charging interactions (C · ⭐ 2).
- [SukritJaAIproject/EV_Charger_Fault_Detection_AI](https://github.com/SukritJaAIproject/EV_Charger_Fault_Detection_AI) - A Windows application for AI-based fault detection in DC EV chargers analyzing ISO 15118-2 / DIN 70121 packet captures (Python · ⭐ 1).
- [oshsos/publicV2G](https://github.com/oshsos/publicV2G) - C++ vehicle-to-grid communication stack implementing ISO 15118-2/-20 for CCS-based smart charging on embedded systems (C · ⭐ 0).
- [donadelden/EVExchange](https://github.com/donadelden/EVExchange) - Tools and testbed implementations for demonstrating the EVExchange attack on ISO 15118 V2G systems and providing a countermeasure (Python · ⭐ 0 · 💤 2021-11-02).
- [uhi22/ccs32ebony](https://github.com/uhi22/ccs32ebony) - A passive web-based viewer that monitors and decodes DIN 70121 (ISO 15118) V2G communication between electric vehicles and chargers on a tablet or phone (C · ⭐ 0).

#### Libraries

##### Go

- [joeky888/exi-go](https://github.com/joeky888/exi-go) - Pure Go EXI encoder/decoder library for ISO 15118-20 with C and Python bindings (⭐ 0).

##### Python

- [Pokiledaa/slac](https://github.com/Pokiledaa/slac) - Python implementation of SLAC for INSYS PowerLine GP powerline communication in EV charging (⭐ 5 · 💤 2022-09-21).

#### Simulator

- [OpenChargingCloud/EVSimulatorApp](https://github.com/OpenChargingCloud/EVSimulatorApp) - A C# .NET application that simulates an electric vehicle implementing ISO/IEC 15118-2 and -20 protocols for testing and security research (Kotlin · ⭐ 1).

### OICP

#### Libraries

##### C\#

- [OpenChargingCloud/WWCP_OICP](https://github.com/OpenChargingCloud/WWCP_OICP) - A .NET 7+ library implementing the Open InterCharge Protocol (OICP) v2.3 for CPO, EMP, and central service communication in e-mobility roaming networks (⭐ 11).

##### Makefile

- [ChargePi/oicp-sdk-go](https://github.com/ChargePi/oicp-sdk-go) - A Go SDK library providing an HTTP client for OICP (Open Intercharge Protocol) CPO operations, generated from the official OpenAPI specification (⭐ 1 · 💤 2025-05-18).

### EMIP

#### Libraries

##### C\#

- [OpenChargingCloud/WWCP_eMIP](https://github.com/OpenChargingCloud/WWCP_eMIP) - A .NET library enabling protocol translation and communication between World Wide Charging Protocol (WWCP) entities and the eMobility Interoperation Protocol (eMIP) (⭐ 2).

### OIOI

#### Libraries

##### C\#

- [OpenChargingCloud/WWCP_OIOI](https://github.com/OpenChargingCloud/WWCP_OIOI) - A .NET library enabling communication between the World Wide Charging Protocol (WWCP) and the PlugSurfing OIOI protocol (⭐ 2 · 💤 2023-09-11).

### Eichrecht

#### Misc

- [OpenChargingCloud/ChargyDesktopApp](https://github.com/OpenChargingCloud/ChargyDesktopApp) - A transparency validation software and library for e-mobility charging records under German Calibration Law (Eichrecht) (TypeScript · ⭐ 11).
- [OpenChargingCloud/ChargyMobileApp](https://github.com/OpenChargingCloud/ChargyMobileApp) - A mobile application for iOS and Android that verifies cryptographic signatures of e-mobility charging records to ensure transparency and compliance with German Eichrecht standards (TypeScript · ⭐ 8).
- [ChargePi/ocmf-go](https://github.com/ChargePi/ocmf-go) - A Go library for generating and parsing OCMF (Open Charge Metering Format) messages with cryptographic signing for EV charging metering compliance (Go · ⭐ 3).
- [OpenChargingCloud/ChargyWebApp](https://github.com/OpenChargingCloud/ChargyWebApp) - A web application and transparency validation library for verifying cryptographic signatures of EV charging processes according to German Calibration Law (Eichrecht) and EU regulations (TypeScript · ⭐ 1).
- [OpenChargingCloud/ChargyCore.NET](https://github.com/OpenChargingCloud/ChargyCore.NET) - A C# .NET library for validating and verifying e-mobility charging transparency and cryptographic signatures in compliance with German Calibration Law (Eichrecht) and EU regulations (C# · ⭐ 1).
- [OpenChargingCommunity/OpenChargingCommunityAPI](https://github.com/OpenChargingCommunity/OpenChargingCommunityAPI) - Open Charging Community API specification for electric vehicle charging infrastructure with eichrecht metrology compliance (C# · ⭐ 0 · 💤 2025-05-29).

### Other

#### Analytics & data

- [SFOE/ichtankestrom_Documentation](https://github.com/SFOE/ichtankestrom_Documentation) - A Swiss national open data infrastructure providing real-time information on electric vehicle charging station availability through interactive maps and publicly accessible APIs (⭐ 12).
- [rescoot/sunshine](https://github.com/rescoot/sunshine) - A Rails web application and API for real-time telemetry monitoring, trip tracking, and remote control of unu/librescoot electric scooters (HTML · ⭐ 4 · 💤 2025-06-03).
- [Paritosh8-AI/AgenticEV_RCA](https://github.com/Paritosh8-AI/AgenticEV_RCA) - An AI-driven root cause analysis platform that diagnoses EV fast-charging network failures through automated analysis of OCPP 1.6-J and OCPI roaming telemetry (Python · ⭐ 1).
- [geraldkombo/albedo](https://github.com/geraldkombo/albedo) - A carbon accounting platform for Kenya's e-mobility SACCO fleets that calculates, aggregates, and registers greenhouse gas emission reductions from EV adoption using UNFCCC-approved methodologies (PHP · ⭐ 1).
- [vabhishekprakash/ev-apm-agent](https://github.com/vabhishekprakash/ev-apm-agent) - An OCPP-aware anomaly detection engine that analyzes charging station telemetry using machine learning and state machines to identify faults and predict charger degradation in real-time (Jupyter Notebook · ⭐ 1).
- [glurp/avere-advenir-json-generator](https://github.com/glurp/avere-advenir-json-generator) - Ruby script that processes OCPP 1.5 charging station data and transmits aggregated charge curves and charging operations to the Advenir platform (Ruby · ⭐ 0 · 💤 2018-06-14).
- [Matthias-H-Git/European-Energy-Market-Analysis](https://github.com/Matthias-H-Git/European-Energy-Market-Analysis) - A data analytics project investigating correlations between renewable energy generation, electrification adoption (e-mobility and heat pumps), and European electricity market prices using public ENTSO-E and EUROSTAT datasets (Jupyter Notebook · ⭐ 0).
- [DeepWazed/Location-based-Probabilistic-Load-Forecasting-of-EV-Charging-Sites-Transfer-Learning-with-MQ-TCN](https://github.com/DeepWazed/Location-based-Probabilistic-Load-Forecasting-of-EV-Charging-Sites-Transfer-Learning-with-MQ-TCN) - Deep learning framework for probabilistic load forecasting at EV charging sites using Multi-Quantile Temporal Convolutional Networks with transfer learning (Jupyter Notebook · ⭐ 0).
- [JohnApollos/boda-emobility-viability-engine](https://github.com/JohnApollos/boda-emobility-viability-engine) - Interactive Streamlit dashboard and Python analytical framework for optimizing battery swap network placement and modeling credit risk in Kenya's electric motorcycle sector (Python · ⭐ 0).
- [knudmoeller/berlin-charging-stations](https://github.com/knudmoeller/berlin-charging-stations) - Ruby script and makefile that downloads Berlin charging station location data from a public WFS service and converts it from GML to CSV format (Makefile · ⭐ 0 · 💤 2020-06-15).
- [Akhil-Prasad09/ev-apm-agent-demo](https://github.com/Akhil-Prasad09/ev-apm-agent-demo) - A synthetic-data demonstration of an EV charger fault detector that replays OCPP telemetry through anomaly detection models with an interactive web-based replay interface (Python · ⭐ 0).

#### Battery

- [Shargus/MasterThesis](https://github.com/Shargus/MasterThesis) - Master's thesis implementing machine learning techniques for real-time state of health estimation of EV battery packs using time series analysis (TeX · ⭐ 0 · 💤 2022-12-26).
- [Locusbura680/battery-simulator-energy](https://github.com/Locusbura680/battery-simulator-energy) - A browser-based simulator for modeling battery energy storage systems with scenarios for load response, arbitrage optimization, backup duration, and solar-aware dispatch (HTML · ⭐ 0).

#### Charging management system

- [ChargeTimeEU/ChargeTime-HQ](https://github.com/ChargeTimeEU/ChargeTime-HQ) - Desktop application for managing and operating EV charging equipment (Java · ⭐ 9 · 💤 2020-10-13).
- [jimmyjoseph-web3/ChargeFrog-Hedera](https://github.com/jimmyjoseph-web3/ChargeFrog-Hedera) - A Hedera blockchain platform for financing, deploying, and tokenizing EV charging infrastructure through agent-driven workflows with carbon tracking (TypeScript · ⭐ 2).
- [eveys-mobility/Console](https://github.com/eveys-mobility/Console) - Web-based operations console for real-time monitoring and control of OCPP charging stations, powered by WebSocket subscriptions to Kafka event streams (TypeScript · ⭐ 2).
- [ocpp-balanz/balanz-ui](https://github.com/ocpp-balanz/balanz-ui) - A React-based web management interface for the balanz OCPP Charging Station Management System, providing charger and group management, live charging status monitoring, and session history access (TypeScript · ⭐ 1).
- [LuRSousa/ChargeGrid-Intelligence](https://github.com/LuRSousa/ChargeGrid-Intelligence) - A comprehensive EV charging management platform for commercial locations with dynamic load balancing, tariff calculation, and AI-based power distribution decision module (JavaScript · ⭐ 1).
- [kamwro/emobility-backend-app](https://github.com/kamwro/emobility-backend-app) - NestJS-based backend server for managing EV charging stations with Postgres persistence and Docker containerization (TypeScript · ⭐ 0).
- [DrVelvetFog/x402-charging-agent](https://github.com/DrVelvetFog/x402-charging-agent) - An autonomous EV charging agent that authorizes a payment ceiling, meters kWh consumption, and settles actual charges on-chain via the x402 protocol with OCPI CDR binding (TypeScript · ⭐ 0).
- [RenatoBoranga1/solis-charge](https://github.com/RenatoBoranga1/solis-charge) - Full-stack EV charging platform with NestJS backend, React Native driver mobile app, admin web portal, PostgreSQL/Redis persistence, and OCPP 1.6J charging station integration (TypeScript · ⭐ 0).

#### Developer tools & libraries

- [OPCFoundation/UA-EdgeTranslator](https://github.com/OPCFoundation/UA-EdgeTranslator) - An industrial edge application translating proprietary protocols (including BACNET, Modbus, IEC 61850, Ethernet/IP, S7, and others) to OPC UA using W3C Web of Things thing descriptions (C# · ⭐ 101).
- [apundir/wsbalancer](https://github.com/apundir/wsbalancer) - WebSocket reverse proxy with stateful failover and REST administration APIs for DevOps automation, originally designed for OCPP but protocol-agnostic (Go · ⭐ 32 · 💤 2020-09-10).
- [arasgungore/EEBUS-in-Java](https://github.com/arasgungore/EEBUS-in-Java) - Java library implementing the EEBUS protocol suite with support for the SHIP and SPINE protocols for smart home IoT device communication (Java · ⭐ 10 · 💤 2024-01-30).
- [OpenChargingCloud/WWCP_Core](https://github.com/OpenChargingCloud/WWCP_Core) - World Wide Charging Protocol Suite core library providing reference implementations and data structures with mappings to OCPP, OCPI, OICP, and ISO 15118 (C# · ⭐ 7).
- [energychain/corrently-charge](https://github.com/energychain/corrently-charge) - A Node.js library that automates tariff selection for EV charging based on state of charge, available time, and local energy generation with OCPP integration (HTML · ⭐ 5 · 💤 2024-01-10).
- [ChargePi/oscp-go](https://github.com/ChargePi/oscp-go) - A Go SDK providing OSCP-compatible server and client code generation via OpenAPI specifications (Makefile · ⭐ 3).
- [hsperker/conversational-websocket-server](https://github.com/hsperker/conversational-websocket-server) - Spring Boot WebSocket server with command-line interface for bidirectional communication with connected clients (Java · ⭐ 3 · 💤 2018-02-08).
- [DigitalCurrensy/bayline](https://github.com/DigitalCurrensy/bayline) - A Python fault validator that processes charger alerts from management systems, validates them against protocol rules and state criteria, and routes validated faults to repair-job systems while locking the charger (Python · ⭐ 3).
- [EVtivity/evtivity-csms-helm](https://github.com/EVtivity/evtivity-csms-helm) - Helm chart for deploying EVtivity CSMS on Kubernetes (JavaScript · ⭐ 2).
- [OpenChargingCloud/WWCP_OCHP](https://github.com/OpenChargingCloud/WWCP_OCHP) - A software library enabling communication between the World Wide Charging Protocol (WWCP) and the Open Clearing House Protocol (OCHP v1.4/OCHPdirect v0.2) (C# · ⭐ 2).
- [solectrus/ruze](https://github.com/solectrus/ruze) - Unofficial Ruby client library for accessing Renault ZE vehicle data (battery status, location, mileage) via their proprietary API (Ruby · ⭐ 2).
- [DigitalCurrensy/module-kinetic-ltd](https://github.com/DigitalCurrensy/module-kinetic-ltd) - A Python-based validation framework that authorizes EV charging station fault recovery through seven sequential compliance checks on fault messages (Python · ⭐ 2).
- [kiranj26/evse-fault-injector](https://github.com/kiranj26/evse-fault-injector) - A fault injection testing tool for validating OCPP and ISO 15118 implementations in electric vehicle chargers (Makefile · ⭐ 1 · 💤 2024-12-16).
- [cdfq384903/Machnata](https://github.com/cdfq384903/Machnata) - JSON Schema to Protocol Buffer code generator that produces cross-language data structures for C/C++, Java, C#, Python, Go and others, validated against OCPP, OCPI and HL7 specifications (Python · ⭐ 1).
- [gerritnowald/electric-car-tools](https://github.com/gerritnowald/electric-car-tools) - Desktop GUI tool for optimizing electric car long-distance travel time with DC charging and estimating yearly operating costs compared to combustion vehicles (Jupyter Notebook · ⭐ 1).
- [vabhishekprakash/rag-eval-system](https://github.com/vabhishekprakash/rag-eval-system) - A local Retrieval-Augmented Generation evaluation framework that benchmarks document chunking strategies against an OCPP specification corpus using FAISS, Ollama, and RAGAs metrics (Python · ⭐ 1).
- [rohittiwari-dev/voltlog-io](https://github.com/rohittiwari-dev/voltlog-io) - VoltLog is a type-safe, zero-dependency structured logging library designed for high-throughput real-time systems such as OCPP WebSocket servers and IoT microservices (TypeScript · ⭐ 1).
- [lex/evse-id-generator](https://github.com/lex/evse-id-generator) - Web tool for generating, validating, and bulk-provisioning EVSE identifiers compliant with ISO 15118 and OCPP 2.0.1 standards (HTML · ⭐ 0).
- [javierojan/askacharge-mcp](https://github.com/javierojan/askacharge-mcp) - Remote MCP server that enables AI agents to operate OCPP charging stations, manage billing and tariffs, and access OCPI roaming through askacharge.com's CSMS (⭐ 0).
- [EVtivity/evtivity-csms-cdk](https://github.com/EVtivity/evtivity-csms-cdk) - AWS CDK infrastructure-as-code for deploying the EVtivity CSMS to AWS with ECS Fargate, Aurora PostgreSQL, and ElastiCache (TypeScript · ⭐ 0).
- [ChargePi/oecs-scraper](https://github.com/ChargePi/oecs-scraper) - A Go application that scrapes EV charger manufacturer specifications from websites and stores them in OECS (Open EV Charger Specification) format using Firecrawl, with gRPC APIs and Kafka-based microservices for processing and validation (Go · ⭐ 0).
- [vlcty/TeslaWallbox](https://github.com/vlcty/TeslaWallbox) - Go library providing programmatic access to Tesla Gen 3 wallboxes for retrieving device information, lifetime statistics, and operational metrics (Go · ⭐ 0 · 💤 2022-12-09).
- [ChargePi/oecs-helm](https://github.com/ChargePi/oecs-helm) - Helm charts for deploying the OECS charging platform services to Kubernetes clusters (Go Template · ⭐ 0).
- [ChargePi/open-ev-data-helm](https://github.com/ChargePi/open-ev-data-helm) - Helm chart for deploying the Open EV Data API platform, which provides access to EV charging point data via a SQLite dataset (Go Template · ⭐ 0).
- [fransiscuss/greenflux-node](https://github.com/fransiscuss/greenflux-node) - TypeScript SDK for interacting with Greenflux CPMS APIs, providing clients for Charge Assist, Platform/CPO/eMSP, Location Management, and Remote Commands (TypeScript · ⭐ 0).
- [fransiscuss/greenflux-dotnet](https://github.com/fransiscuss/greenflux-dotnet) - Unofficial strongly-typed .NET SDK providing clients for Greenflux charging management platform APIs including platform operations, charge location management, remote commands, and charge assist services (C# · ⭐ 0).
- [salah2277/steve](https://github.com/salah2277/steve) - Steve is a command-line tool that automates control and testing of macOS applications through the Accessibility API (Swift · ⭐ 0).
- [camuh3/macos-ai-commander](https://github.com/camuh3/macos-ai-commander) - MacOS command-line tool that automates native application UIs through the Accessibility API, with no EV-charging functionality despite its OCPP-related topics (HTML · ⭐ 0).
- [arcnode-io/ems-industrial-gateway](https://github.com/arcnode-io/ems-industrial-gateway) - A Rust industrial protocol gateway that translates Modbus TCP, SNMP, Redfish, DNP3, and BACnet/IP to MQTT with metric metadata and synthetic derivations (Rust · ⭐ 0).

#### EVSE firmware

- [BorisBrock/HeidelBridge](https://github.com/BorisBrock/HeidelBridge) - ESP32 firmware that integrates Heidelberg wallbox EV chargers into home WiFi networks for compatibility with home energy management systems and home automation platforms (C · ⭐ 52).
- [bodems/controller-firmware](https://github.com/bodems/controller-firmware) - An OpenWRT-based firmware generator for EV charging controllers following the IEC 61851 standard, with web-based configuration and updates (JavaScript · ⭐ 0 · 💤 2018-06-24).
- [cz-lucas/alphatecmini-ocpp](https://github.com/cz-lucas/alphatecmini-ocpp) - ESP32-S3 firmware implementing an OCPP charge point for the Alphatec Mini wallbox with RFID authentication, real-time monitoring, and tariff switching (C++ · ⭐ 0).
- [fransiscuss/EVFirmwares](https://github.com/fransiscuss/EVFirmwares) - Archive of EV charger firmware organized by device type (⭐ 0 · 💤 2024-10-30).

#### Energy management

- [fneum/ev_chargingcoordination2017](https://github.com/fneum/ev_chargingcoordination2017) - A stochastic optimization framework for cost-minimizing day-ahead scheduling of electric vehicle charging in residential distribution networks subject to grid constraints and uncertain demand (Python · ⭐ 125 · 💤 2018-06-09).
- [flashg1/SolarCharger](https://github.com/flashg1/SolarCharger) - Home Assistant integration that allocates surplus solar energy to EV charging and home heating according to user-defined device priorities (Python · ⭐ 20).
- [enbility/cemd](https://github.com/enbility/cemd) - A deprecated Go library implementing an EEBUS-based Central Energy Manager with use cases for coordinated EV charging and power management (Go · ⭐ 12 · 🚫 deprecated · 💤 2024-06-29).
- [iceccarelli/derim-middleware](https://github.com/iceccarelli/derim-middleware) - Open-source middleware platform for integrating and managing distributed energy resources (solar, batteries, EV chargers) with protocol adapters and digital twin simulation for smart grid applications (Python · ⭐ 1).
- [Michito49/evcc](https://github.com/Michito49/evcc) - A local charge controller and energy management system for managing EV charging integrated with home energy systems (HTML · ⭐ 0).
- [BBessler/Solarmanager](https://github.com/BBessler/Solarmanager) - A home energy management system that automatically distributes excess solar power to EV chargers, battery storage, heat pumps, and household appliances, running locally on Raspberry Pi or Docker without cloud dependency (Shell · ⭐ 0).

#### Home automation

- [flashg1/evSolarCharger](https://github.com/flashg1/evSolarCharger) - A Home Assistant automation blueprint for controlling EV charging from surplus solar energy and weather forecasts using OCPP and EV-specific APIs (⭐ 17).
- [JoaoPedroBelo/bmw-wallbox-ha](https://github.com/JoaoPedroBelo/bmw-wallbox-ha) - Home Assistant integration that enables local monitoring and control of BMW wallbox chargers via the OCPP 2.0.1 protocol (Python · ⭐ 14).
- [iobroker-community-adapters/ioBroker.kecontact](https://github.com/iobroker-community-adapters/ioBroker.kecontact) - An ioBroker home automation adapter for KEBA KeContact P20/P30 and BMW i wallboxes that enables control via UDP protocol and automatic charging management based on photovoltaic surplus and battery storage (JavaScript · ⭐ 10).
- [weemaba999/homeassistant-tap-community](https://github.com/weemaba999/homeassistant-tap-community) - A Home Assistant integration for monitoring and controlling EV chargers managed through the Tap Electric platform (Python · ⭐ 10).
- [henrikekblad/spotnav-home-assistant](https://github.com/henrikekblad/spotnav-home-assistant) - A Home Assistant integration that optimizes EV charging timing based on spot electricity prices and solar surplus, with load balancing and local fuse management (Python · ⭐ 7).
- [pottio/ioBroker.warp](https://github.com/pottio/ioBroker.warp) - IoBroker adapter for monitoring and controlling Tinkerforge WARP wallbox chargers via WebSocket (TypeScript · ⭐ 2 · 💤 2023-04-01).
- [JFK344/ioBroker.evsewifi](https://github.com/JFK344/ioBroker.evsewifi) - An ioBroker adapter that integrates SimpleEVSE-WiFi charging stations into smart home automation systems, exposing vehicle state, charging current, power consumption, and energy metering (JavaScript · ⭐ 1 · 💤 2023-11-18).
- [ZaBug/duosida-lan](https://github.com/ZaBug/duosida-lan) - Home Assistant integration providing local LAN control of Duosida EV wallboxes over TCP 9988 without cloud connectivity (Python · ⭐ 1).
- [GNLT-EV/gnlt-home-assistant](https://github.com/GNLT-EV/gnlt-home-assistant) - A Home Assistant integration for controlling and monitoring GNLT EV chargers locally via the OCPP 1.6J protocol (Python · ⭐ 0).
- [HarshBhardwaj/gridradar-ha](https://github.com/HarshBhardwaj/gridradar-ha) - A Home Assistant integration that exposes GridRadar EV chargers as HA devices with live sensors and remote control actions via the GridRadar REST API (Python · ⭐ 0).
- [javierojan/askacharge-homeassistant](https://github.com/javierojan/askacharge-homeassistant) - Home Assistant custom integration that reads OCPP charger status, energy, and power metrics from askacharge.com and provides remote start/stop control via Home Assistant entities (Python · ⭐ 0).
- [jedifr/ha-plugchoice](https://github.com/jedifr/ha-plugchoice) - Home Assistant custom integration for Plugchoice EV charging stations (OCPP 1.6J) providing auto-discovery, remote control, and multi-station load balancing (Python · ⭐ 0).
- [JustChr/HAgoe_steve](https://github.com/JustChr/HAgoe_steve) - A Home Assistant custom integration providing intelligent charging control for go-e wallboxes, optimizing power based on solar generation, grid electricity pricing, and home battery state (Python · ⭐ 0).
- [augustas2/morek-charger-card](https://github.com/augustas2/morek-charger-card) - A Home Assistant Lovelace dashboard card for monitoring and controlling Morek EV chargers via OCPP (TypeScript · ⭐ 0).
- [TeMo62/HA_EV_Charge_Halo_Nordpool](https://github.com/TeMo62/HA_EV_Charge_Halo_Nordpool) - Home Assistant integration that controls a Charge Amps Halo EV charger via OCPP and optimizes charging schedules based on Nord Pool electricity prices (⭐ 0).

#### Maps & route planning

- [mohsinali33226/Hamburg-fast-charging-gap-map](https://github.com/mohsinali33226/Hamburg-fast-charging-gap-map) - A GIS-based site assessment project that identifies potential gaps in fast-charging coverage around Hamburg using public charging infrastructure data and interactive mapping (⭐ 0).
- [h-waldschmidt/olsp](https://github.com/h-waldschmidt/olsp) - C++ tool and library implementing hub-labeling pathfinding algorithms to optimize electric vehicle charging station placement on geographic road networks (C++ · ⭐ 0 · 💤 2024-03-20).

#### Mobile app

- [sap-labs-france/ev-mobile](https://github.com/sap-labs-france/ev-mobile) - A React-Native mobile application for Android and iOS providing electric vehicle charging station management functionality integrated with the Open e-Mobility backend (TypeScript · ⭐ 66 · 💤 2023-10-16).
- [powerly-ev/open-ev-charge-ios-app](https://github.com/powerly-ev/open-ev-charge-ios-app) - Open-source iOS application for discovering and managing electric vehicle charging stations with white-label customization support (Swift · ⭐ 3).
- [SAP-samples/e-mobility-driver-app](https://github.com/SAP-samples/e-mobility-driver-app) - A progressive web application for electric vehicle drivers to manage charging sessions, find charging stations, and track energy consumption and costs (TypeScript · ⭐ 1).
- [jeroentrappers/charging](https://github.com/jeroentrappers/charging) - A PWA and HTTP API service aggregating real-time EV charging data from European National Access Points (via OCPI, DATEX II, and Monta APIs) to help drivers find the cheapest available chargers ranked by total cost including detour (Go · ⭐ 0).
- [PinguPeng2010/volty-charge](https://github.com/PinguPeng2010/volty-charge) - Mobile app for discovering EV charging infrastructure with OCPI 2.2.1 integration and planned payment capabilities (⭐ 0).
- [jerthermit/charge-hermitedge](https://github.com/jerthermit/charge-hermitedge) - A mobile-first EV charging application for Philippine drivers and network operators, featuring maps-based station discovery, session management, payment workflows, and AI-assisted network operations (TypeScript · ⭐ 0).

#### Other protocols

- [Emulate-Energy/EDAP](https://github.com/Emulate-Energy/EDAP) - Python library implementing EDAP, a low-latency protocol for cloud-based energy device control and data access (Python · ⭐ 0).

#### Security

- [leonard-voss/nocpp](https://github.com/leonard-voss/nocpp) - A Python application for penetration testing OCPP charging stations through fuzzing attacks and information gathering against Charge Point-to-CSMS connections (Python · ⭐ 0 · 💤 2025-01-22).
- [OpenChargingCommunity/PKI](https://github.com/OpenChargingCommunity/PKI) - A public key infrastructure specification for the e-mobility ecosystem using multi-signature quorum-based certificates to enable secure many-to-many trust relationships among diverse stakeholders (⭐ 0 · 💤 2023-08-02).

#### Simulators

- [Coretech-Innovations/EEBus-Hub](https://github.com/Coretech-Innovations/EEBus-Hub) - EEBUS Hub is a testing and simulation framework for validating EEBUS device integration over an EEBUS network, supporting energy management scenarios including EV charging and grid control (⭐ 10).
- [gtfs4ev/gtfs4ev](https://github.com/gtfs4ev/gtfs4ev) - GTFS4EV is an open-source Python framework for simulating electric bus fleet operations and charging scenarios based on standardized GTFS transit data (Python · ⭐ 5).
- [Majkel-code/GE_EvChargingStation](https://github.com/Majkel-code/GE_EvChargingStation) - A lightweight Python and FastAPI-based simulator with separate charger and vehicle server components for simulating electric vehicle charging sessions and exploring charging flows (Python · ⭐ 1).
- [GreenCharge/gcsimulator](https://github.com/GreenCharge/gcsimulator) - GreenCharge is a discrete-event simulator for energy smart neighborhoods that reproduces real-world EV charging and energy management scenarios using measured data in containerized virtual environments (Python · ⭐ 0 · 💤 2022-02-10).
- [arcnode-io/ems-industrial-fixtures](https://github.com/arcnode-io/ems-industrial-fixtures) - Rust library providing mock implementations of industrial gateway protocols (Modbus TCP, SNMP, DNP3, CANbus, Redfish) for testing (Rust · ⭐ 0).

#### Specifications & documentation

- [OpenChargingCloud/OCC_PKI](https://github.com/OpenChargingCloud/OCC_PKI) - A public key infrastructure specification for the e-mobility sector proposing graph-based multi-signature quorum certificates as an alternative to traditional X.509 hierarchies (⭐ 4 · 💤 2023-08-02).
- [wiedergruen/ocmf](https://github.com/wiedergruen/ocmf) - A markdown specification document for the Open Charge Metering Format (OCMF), a data format standard for metering in EV charging (⭐ 3 · 💤 2019-07-08).
- [skazemi/awesome-evse](https://github.com/skazemi/awesome-evse) - A curated awesome list of EV charging tools, frameworks, libraries, and software (⭐ 1 · 💤 2024-03-13).
- [api-evangelist/enapi](https://github.com/api-evangelist/enapi) - API Evangelist's independent third-party profile documenting Enapi's unified roaming and clearing platform API for electric vehicle charging (⭐ 0).
- [api-evangelist/lemonflow-ai](https://github.com/api-evangelist/lemonflow-ai) - An API Evangelist third-party profile documenting the public API surface of Lemonflow, an AI-driven platform for EV charging customer support (⭐ 0).
- [api-evangelist/ev-connect](https://github.com/api-evangelist/ev-connect) - Third-party API documentation profile of EV Connect's charge point management platform API surface, maintained by API Evangelist (⭐ 0).
- [api-evangelist/flo-ev](https://github.com/api-evangelist/flo-ev) - API Evangelist's independent third-party documentation profile of FLO's public EV charging APIs, including OpenAPI and AsyncAPI specifications (⭐ 0).
- [api-evangelist/blink](https://github.com/api-evangelist/blink) - API Evangelist's independent third-party documentation profile of Blink Charging's public API surface (⭐ 0).
- [api-evangelist/flipturn](https://github.com/api-evangelist/flipturn) - An API Evangelist-maintained documentation profile of Flipturn's EV charging fleet management platform's public API surface (⭐ 0).
- [M4GNV5/charging-infrastructure-review-paper](https://github.com/M4GNV5/charging-infrastructure-review-paper) - A research paper reviewing fast charging communication protocols and cybersecurity implications, published at SECURWARE 2024 (TeX · ⭐ 0).
- [api-evangelist/cariqa](https://github.com/api-evangelist/cariqa) - An API Evangelist third-party profile of Cariqa's public API surface for EV charging payment and access infrastructure (⭐ 0).
- [api-evangelist/evie-networks](https://github.com/api-evangelist/evie-networks) - An API Evangelist profile and specification documentation of Evie Networks' public EV charging infrastructure APIs (⭐ 0).
- [Autoknigge/Autoknigge.de](https://github.com/Autoknigge/Autoknigge.de) - German-language automotive advice website covering road etiquette, vehicle care, car purchasing, insurance, registration, and money-saving tips (HTML · ⭐ 0).
- [api-evangelist/schaeffler](https://github.com/api-evangelist/schaeffler) - A third-party API profile of Schaeffler's public APIs, maintained by API Evangelist, documenting the Tier 1 automotive and industrial supplier's publicly available API surface (⭐ 0).
- [api-evangelist/enel-x](https://github.com/api-evangelist/enel-x) - A third-party machine-readable API specification profile of Enel X's public APIs for advanced energy services, e-mobility, and demand response, maintained by API Evangelist (⭐ 0).
- [ChargePi/oecs-website](https://github.com/ChargePi/oecs-website) - A presentation website for OECS, a standardized, computer-readable schema for describing EV charger specifications (TypeScript · ⭐ 0).
- [pmreis/emobility](https://github.com/pmreis/emobility) - A repository collecting legal frameworks, regulatory documents, technical specifications, and policy information for electric mobility in Europe, with focus on AFIR compliance and Portuguese eMobility evolution (Python · ⭐ 0).
- [ChargePi/oecs-hub](https://github.com/ChargePi/oecs-hub) - A web-based registry and database of EV charger specifications with gRPC APIs, submission workflows, and a graph-based search interface powered by PostgreSQL, Redis, and Memgraph (JavaScript · ⭐ 0).
- [api-evangelist/chargy](https://github.com/api-evangelist/chargy) - Third-party API profile of char.gy's public API surface maintained by API Evangelist, containing OpenAPI, AsyncAPI, and JSON Schema specifications for a British on-street EV charge point operator (⭐ 0).
- [api-evangelist/shellrecharge](https://github.com/api-evangelist/shellrecharge) - Third-party OpenAPI and AsyncAPI profiles of Shell's ShellRecharge public APIs for EV charging network and location management, maintained by API Evangelist (⭐ 0).
- [api-evangelist/pod-point](https://github.com/api-evangelist/pod-point) - API Evangelist's independent third-party profile and documentation of Pod Point's publicly available EV charging APIs, using machine-readable specifications (⭐ 0).
- [api-evangelist/chargefox](https://github.com/api-evangelist/chargefox) - Independent third-party API specification profile of Chargefox's public EV charging network platform API, maintained by API Evangelist (⭐ 0).
- [api-evangelist/gireve](https://github.com/api-evangelist/gireve) - A third-party API documentation and profile repository of Gireve's public platform for EV charging and e-mobility services in Europe, maintained by API Evangelist (⭐ 0).
- [api-evangelist/presto](https://github.com/api-evangelist/presto) - A third-party API profile and documentation repository for Presto, an electric-vehicle charging aggregation platform that provides unified access to public chargers across North American networks (⭐ 0).
- [api-evangelist/blink-charging](https://github.com/api-evangelist/blink-charging) - Independent third-party API profile and documentation of Blink Charging's public EV charging API surface, provided by API Evangelist with OpenAPI and JSON Schema specifications (⭐ 0 · 💤 2026-09-04).
- [api-evangelist/ubitricity](https://github.com/api-evangelist/ubitricity) - A third-party API profile and documentation repository of Ubitricity's public EV charging APIs, maintained by API Evangelist (⭐ 0).
- [Veton-ev/Veton-EMS-Integration](https://github.com/Veton-ev/Veton-EMS-Integration) - Developer guide and reference documentation for integrating Veton EV chargers into Energy Management Systems, covering Modbus, MQTT, REST APIs, and OCPP 1.6 interfaces with code examples (Shell · ⭐ 0).
- [ishandutta2007/Awesome-EV-Charging-Management](https://github.com/ishandutta2007/Awesome-EV-Charging-Management) - A curated awesome list of open-source and commercial EV charging management systems, protocols (OCPP, OCPI, ISO 15118), and infrastructure tools (⭐ 0).
- [ishandutta2007/Awesome-Electric-Vehicle-Charging-Management](https://github.com/ishandutta2007/Awesome-Electric-Vehicle-Charging-Management) - A curated awesome list cataloging Electric Vehicle charging management platforms, Charging Station Management Systems, and open-source tools covering OCPP, OCPI, and related protocols (⭐ 0).
- [api-evangelist/meshcrafts](https://github.com/api-evangelist/meshcrafts) - Third-party API profile and specifications documentation for Meshcrafts/CURRENT, a charge point management system provider, maintained by API Evangelist (⭐ 0).
