# Boot sequence

This document describes the boot sequence of a system built upon PSEC.

## Provisioning

The provisioning of the system is not described here, please look at [this document](provisioning.md).

## Steps

- The system is started by the user
- Depending on the [provisioning type](provisioning.md), the local boot loader or the PXE boot loader is executed
- XEN kernel is loaded
- Linux kernel is loaded
- Initial RAM FS is loaded
- XEN kernel is executed
- Linux kernel is executed
- Root filesystem is mounted
- OpenRC is started
  - Runlevel sysinit is executed
    - Hardware drivers are loaded
    - ...
    - Splash screen is shown
    - ...
  - Runlevel boot is executed
    - ...
- PSEC initialization sequence is started
  - Depending on the [provisioning type](provisioning.md), Alpine packages may be *downloaded* from the public repository, including PSEC and specific application packages, into the local repository
  - Also depending on the provisioning type, Alpine ISO image may be *downloaded*
  - Local PGP key is generated
  - Local repository is signed with the new PGP key
  - PSEC Dom0 daemon is started
    - USB devices are identified and attached to XEN
    - Communication channels are created
        - *Message channel*
        - *Log channel*
        - *Input channel*
    - PSEC packages are installed for the VMs
        - *psec-sys-usb*
        - *psec-sys-gui*
    
