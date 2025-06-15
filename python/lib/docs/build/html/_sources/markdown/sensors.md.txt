# Sensors

This document describes the sensor monitoring system.

Most of the sensors are accessible thru USB and sometimes thru PCI. In all the cases the devices are captures in the Domain `sys-usb`.

The monitoring messages and polling requests are achieved with the [messaging](protocol.md) and the [API](../../build/html/_modules/psec/_api.html).

## Sensors list

This sections lists the sensors monitored.

| Sensor | Since | Type | Description |
|--|--|--|--|
| Battery level | 1.1 | Polling | Returns the battery level in percent. |
| Energy source | 1.1 | Polling | Returns the energy source (battery or power supply) |