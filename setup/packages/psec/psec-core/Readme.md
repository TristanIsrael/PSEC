# psec-core

The core enables a machine to become a secured platform for security products.

## What is done

The following tasks are achieved:
- Setup and configure a hardened XEN Dom0.
- Prepare a local repository for inter-VM file exchange.
- Setup the main controller and interfaces in order to provide security functions to the VMs.
- Provides a local Alpine repository for the virtual machines.

## How to

This sections provides answers to different questions.

### [Integration] Provide additonal repository for package download

When making a security product on top of PSEC you need to provide your own packages which are hosted on your own repositoy. 
When Alpine boots up, the file `/etc/apk/repositories` is provided with default *and disabled* configuration. You need to provide your own `/etc/apk/repositories` with the correct configuration which points to your own repositories and, *maybe*, the officiel Alpine repositories.

The `repositories` file is documented [here](https://wiki.alpinelinux.org/wiki/Repositories).

#### PXE boot

In case you boot with PXE, you need to provide the configuration on the command line in order to let Alpine download the packages during the boot.

The command line is configured this way : `[A compléter]`.

- initialisation of the DomU template

### Scripts provided

This package provides scripts for