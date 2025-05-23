# Platform Description

This document describes the architecture of the security-oriented technical platform.

## Virtual Machines (Domains)

The platform includes the following virtual machines:

| Name | Description | Trust Level |
|---|---|---|
| Dom0 | Domain 0 is a special virtual machine used to manage user domains and interface with the XenBus | High |
| vm-sys-usb | This user domain is responsible for managing USB devices (keyboard, mouse, storage devices) and isolating them from the rest of the system | Low |
|  |  |  |

### Dom0

This section provides technical details about `Domain 0`.

**The XEN toolstack must be installed on Dom0. It is typically provided by the PXE installation during network boot.**

Installed packages:
- python (`python3`)

### vm-sys-usb

This section provides technical details about the user domain `vm-sys-usb`.

The `vm-sys-usb` domain provides the following functions via XenStore:
- keyboard input
- mouse position
- mouse button states
- touchscreen position
- reading the file catalog from a USB device
- reading a file from a USB device
- writing a file to a USB device

Resources:
| Resource | Capacity |
|---|---|
| RAM | 400 MB |

Installed packages:
- python3
- py3-pyserial
- ntfs-3g 
- evtest (development only) 
- py3-libevdev

Removed files:
- none

#### USB Device Detection

USB device detection is handled by `udev`. A specific rule is added using the `99-usbdisks.rules` file placed in the `/etc/udev/rules.d` directory.

When a USB device is connected, the `mdev-usb-storage` script is executed. It checks for the presence of the device and creates a mount point in `/media/usb` with the same name as the connected disk. A notification is then sent on the Xenbus via the messaging system.