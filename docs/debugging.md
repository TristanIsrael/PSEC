# Debugging

This document explains how to debug a system running with PSEC.

## Boot options

In order to activate the debugging facilities, the file `/etc/default/grub` must be modified.
Add the sequence `DEBUG=ON` (with a space before if needed) at the end of the line `GRUB_CMDLINE_LINUX_DEFAULT`.

## RS-232 Serial link

The main debugging channel uses the RS-232 serial port of the system when it has one. Otherwise an USB-serial device can be used as long as its chipset is recognized by the kernel embedded in the `sys-usb` DomD.

## PTY terminal

After connecting a serial cable (RS-232 or USB), a serial connection can be opened with the following settings:
- speed: 9 600 bps
- bits : 8
- parity : none
- stop bits: 1

After opening a serial connection a login prompt is opened.

**If no login has been provided in the topology file the session can be opened as root**.

## MQTT console

After logging in the system, the MQTT broker can be queried using the command `mosquitto_sub` and connect it on the local MQTT socket located at `/vr/run/mqtt_msg_local.sock`.

For example:
```
$ mosquitto_sub --unix /var/run/mqtt_msg_local.sock -t '#' --pretty -v
```