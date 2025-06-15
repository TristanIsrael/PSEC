# Debugging

This document explains how to debug a system running with PSEC.

## Activate debugging

In order to activate the debugging facilities, the file `/etc/default/grub` must be modified.
Add the sequence `DEBUG=ON` (with a space before if needed) at the end of the line `GRUB_CMDLINE_LINUX_DEFAULT`.

## Disable splash screen

Disabling the splash screen might be necessary to see boot messages. In this case add the option `nosplash` to the kernel command line in GRUB during the boot or in the
file `/etc/default/grub` at the end of the line `GRUB_CMDLINE_LINUX_DEFAULT`.

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

## Log files

When in debug mode the following log files are created:

| Location | Description |
|--|--|
| /var/log/psec/messages.log | This log contains all MQTT messages. |

## Verify whether debug is activated

There are two ways of knowing whether debug is activated:

- On Dom0 : `$ grep -i debug=on /proc/cmdline`
- Using the Api : `Api().request_system_info()`. The JSON returned contains `core.debug_on` which is a boolean. Example : 
```
{
    "core": {
        "version": "2.0.0",
        "debug_on": true
    }
}
```