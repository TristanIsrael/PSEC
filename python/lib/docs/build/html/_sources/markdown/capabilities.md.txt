# Capabilities

This document describes the capabilities of the PSEC core.

## List of capabilities

The PSEC core offers the following capabilities:

| Capability | Since | Description |
|--|--|--|
| Messaging | v1.0 | The messaging is the way to send and receive commands and notifications inside the system in a secure way. The functions of the core are called using the messagging system; It is recommended to use the [API](../../build/html/api.html) to call core functions. Commands and information can be exchanged between the product business Domains using the messaging. The messaging uses a specific [protocol](protocol.md) |
| Logging | v1.0 | The product can use the embedded [logging](logging.md) system to gather debugging or production information in a log file, which can then be stored on an external device. |
| Sensors | v1.0 | The [sensors](sensors.md) of the platform are monitored and their state is notified thru the [messaging](protocol.md) and can be queried in the [API](../../build/html/api.html). |
| External storage | v1.0 | The external storage is monitored and can be used to read or write files. When an external drive is connected or disconnect, a notification is sent. The [API](../../build/html/api.html) can be used to get the directory tree of a drive, read or write a file. |
| Integrity | v1.0 | The system provides different ways of verifying the integrity of the system and the files. For example, when a file is read, its fingerprint is calculated and verified on each operation of reading, writing, moving, etc. |
| Monitoring | v1.0 | The components (or modules) can be monitored by querying their state or listening to their state change notification. The monitoring can be done thru the [API](../../build/html/api.html). |
