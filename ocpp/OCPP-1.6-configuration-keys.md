# OCPP 1.6 Configuration Keys

Reference of the OCPP 1.6 configuration keys, grouped by feature profile (plus the
OCPP-J transport keys and the Security extension from the OCPP 1.6 Security Whitepaper,
ext 1.3).

The **Required / Optional** column reflects the OCPP 1.6 specification (edition 2) and
the Security Whitepaper (edition 3): "Required" means the Charge Point must support the
key when it implements the corresponding profile.

## Legend

- **CSL** = Comma Separated List
- **R** = Read-only
- **RW** = Read-Write
- **W** = Write-only
- **Required / Optional** = whether supporting the key is mandatory for the profile

## Core Profile

| Key | Required/Optional | Accessibility | Type |
|---|---|---|---|
| AllowOfflineTxForUnknownId | Optional | RW | boolean |
| AuthorizationCacheEnabled | Optional | RW | boolean |
| AuthorizeRemoteTxRequests | Required | RW | boolean |
| BlinkRepeat | Optional | RW | integer |
| ClockAlignedDataInterval | Required | RW | integer |
| ConnectionTimeOut | Required | RW | integer |
| ConnectorPhaseRotation | Required | R | csl :<br>NotApplicable<br>Unknown<br>RST<br>RTS<br>SRT<br>STR<br>TRS<br>TSR |
| ConnectorPhaseRotationMaxLength | Optional | R | integer |
| GetConfigurationMaxKeys | Required | R | integer |
| HeartbeatInterval | Required | RW | integer |
| LightIntensity | Optional | RW | integer |
| LocalAuthorizeOffline | Required | RW | boolean |
| LocalPreAuthorize | Required | RW | boolean |
| MaxEnergyOnInvalidId | Optional | R | integer |
| MeterValueSampleInterval | Required | RW | integer |
| MeterValuesAlignedData | Required | RW | integer |
| MeterValuesAlignedDataMaxLength | Optional | R | integer |
| MeterValuesSampledData | Required | RW | csl :<br>Energy.Active.Import.Register<br>Power.Active.Import<br>Current.Import<br>Voltage<br>Temperature<br>Current.Offered<br>Frequency<br>Power.Factor |
| MeterValuesSampledDataMaxLength | Optional | R | integer |
| MinimumStatusDuration | Optional | RW | integer |
| NumberOfConnectors | Required | R | integer |
| ResetRetries | Required | RW | integer |
| StopTransactionOnEVSideDisconnect | Required | RW | boolean |
| StopTransactionOnInvalidId | Required | RW | boolean |
| StopTxnAlignedData | Required | R | string |
| StopTxnAlignedDataMaxLength | Optional | R | integer |
| StopTxnSampledData | Required | R | string |
| StopTxnSampledDataMaxLength | Optional | R | integer |
| SupportedFeatureProfiles | Required | R | csl :<br>Core<br>FirmwareManagement<br>LocalAuthListManagement<br>RemoteTrigger<br>Reservation<br>SmartCharging |
| SupportedFeatureProfilesMaxLength | Optional | R | integer |
| SupportedFileTransferProtocols | Required | R | string |
| TransactionMessageAttempts | Required | RW | integer<br>1 - 65535<br>0 (retry indefinitely) |
| TransactionMessageRetryInterval | Required | RW | integer |
| UnlockConnectorOnEVSideDisconnect | Required | RW | boolean |

## Smart Charging Profile

| Key | Required/Optional | Accessibility | Type |
|---|---|---|---|
| ChargeProfileMaxStackLevel | Required | R | integer |
| ChargingScheduleAllowedChargingRateUnit | Required | R | csl :<br>Current<br>Power |
| ChargingScheduleMaxPeriods | Required | R | integer |
| ConnectorSwitch3to1PhaseSupported | Optional | R | boolean |
| MaxChargingProfilesInstalled | Required | R | integer |

## Local Auth List Management Profile

| Key | Required/Optional | Accessibility | Type |
|---|---|---|---|
| LocalAuthListEnabled | Required | RW | boolean |
| LocalAuthListMaxLength | Required | R | integer |
| SendLocalListMaxLength | Required | R | integer |

## Reservation Profile

| Key | Required/Optional | Accessibility | Type |
|---|---|---|---|
| ReserveConnectorZeroSupported | Optional | R | boolean |

## Security Profile (OCPP ext 1.3)

| Key | Required/Optional | Accessibility | Type |
|---|---|---|---|
| AdditionalRootCertificateCheck | Optional | R | boolean |
| CertificateSignedMaxChainSize | Optional | R | integer |
| CertificateStoreMaxLength | Optional | R | integer |
| CpoName | Optional | RW | string |
| SecurityProfile | Optional | RW | integer |

## OCPP-J (transport)

| Key | Required/Optional | Accessibility | Type |
|---|---|---|---|
| AuthorizationKey | Optional | W | string |
| WebSocketPingInterval | Optional | RW | integer |
