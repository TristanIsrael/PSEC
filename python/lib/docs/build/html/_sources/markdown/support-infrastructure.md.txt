# Creating the Deployment Infrastructure

*This document is not up-to-date*

This documentation explains how to implement the deployment infrastructure.

## Topologies

Different topologies can be implemented depending on whether you rely on Internet or not for Alpine mirrors.

### Using Internet 

If you will be using Internet to provide Alpine and PSEC mirrors you will only need to host you own products packages on standard HTTP server. 

### Using local mirror

If your systems are offline with no access to Internet, *or* if you want to implement local mirrors for better performance, you will have to provide a standard HTTP
server for Alpine and PSEC packages, and for your own packages.

### Using network boot

If your system will boot on the network you will have to implement the DHCP, TFTP and NFS servers.

### Summary

This section summarizes the cases and the services to provide locally.

| Use case | DHCP | TFTP | NFS | HTTP | ADMIN |
|--|--|--|--|--|--|
| Network boot | Yes | Yes | Yes (1) | No (2) | Yes |
| USB / embedded boot | No | No | No (2) | No | Yes |
| Local cache | No | No | No | Yes | Yes |
| Offline (no Internet) | No | No | No | Yes | Yes |

*(1) If you want to manage user or specific hardware configurations.*
*(2) Only for your own products' packets.*

## Common implementation

In all the cases you will have to implement the following services on your local area network (LAN):

| Name    | IPv4 Address    | Description |
|---------|-----------------|-------------|
| DHCP    | 192.168.10.1    | DHCP server for PXE boot |
| TFTP    | 192.168.10.1    | TFTP server for PXE boot |
| HTTP    | 192.168.10.2    | HTTP server serving the white stations configurations |
| NFS     | 192.168.10.2    | NFS server allowing the integrator to store or modify white stations configurations |
| REPOSITORIES | 192.168.10.3 | HTTP server serving Alpine packages (APK) |
| ADMIN   | 192.168.10.250  | Machine enabling the administrator to install and configure the deployment infrastructure |

## Assisted deployment

The assisted deployment offers a simple way to create the support infrastructure using the deployment system `Ansible`.

The operations consist in describing the configuration (services and machines) in an Ansible file in a format derived from JSON, and execute the deployment which runs
automatically. This process can also be used to update the support infrastructure.

### Prerequisites

The first step is to define which topology you want to implement (see [Topologies](#topologies)).

(To be continued)

### Configure Ansible

(To be continued)

## Keep the mirrors up-to-date

The mirrors should be kept up-to-date as frequently as possible (daily to weekly) in order to benefit from the bug and security fixes.

The script `infrastructure/scripts/update-alpine-mirror.sh` is dedicated to updating a local Alpine mirror. It should be placed in the path of the mirror on the HTTP server.

Run the script: `./update-alpine-mirror.sh [arch] [version]` where arch is `x86_64`, `armv7` or `aarch64` and version is the version of Alpine to update, for example `3.22`.

The following command will update the local mirror:

`$ ./udpate-alpine-mirror.sh x86_64 3.22`

It will update all files in the folder `./alpine/v3.22/main/x86_64` and `./alpine/v3.22/community/x86_64`. The local mirror will be an exact copy of the remote, meaning that all files removed from the official repository will be removed from the local mirror and all files added on the official repository will be added in the local mirror.


## Steps [ORIGINAL DOCUMENTATION to be refreshed starting here]

The creation of the infrastructure is done in two steps:

1. Creation of virtual machines

2. Deployment and configuration of services

## Prerequisites

The administrator must have available:

- the installation kit which includes this documentation

- the latest Alpine extended ISO

- the latest Alpine XEN ISO image

- the latest Alpine Virtual ISO image

- a mirror of the official Alpine package repository (see *Creating an Alpine package mirror*)

## Creating the Virtual Machines

This section describes the steps to create the infrastructure virtual machines. The machines must be created in the indicated order.

### Administration Workstation

This section describes creating a machine for the administrator.

*to be completed*

### Embedded Repositories

Alpine repositories can be stored on an existing HTTP server if one exists on the network. This section explains how to create a new HTTP server for Alpine repositories.

**The machine must have at least 2 GB of memory.**

- Boot the machine using the standard Alpine ISO.

- At the login prompt, type `root` then Enter. Authentication is done.

- Type the command `setup-keymap`. Then type `fr`, Enter, `fr`, Enter. The keyboard is now set to French.

- Type the command `setup-interfaces`.

- At the question `Which one do you want to initialize?`, type `eth0` then Enter.

- At the question `Ip address for eth0?`, type `192.168.10.3` then Enter.

- At the question `Netmask?`, type `255.255.255.0` then Enter.

- At the question `Gateway?`, type `none` then Enter.

- At the question `Do you want to do any manual network configuration?`, type `n` then Enter.

- Type the command `/etc/init.d/networking restart`. The server is now configured with IP address `192.168.10.3`.

- Type the command `rc-update add networking`.

- Type the command `setup-sshd` then Enter.

- At the question `Which SSH server`, type `openssh` then Enter.

- The SSH server is now configured.

- Type the command `adduser admin` then Enter. Then enter a strong password twice consecutively.

- Type the following commands:
```
mkdir -p /var/depots/alpine/main/x86_64
chown -R admin:admin /var/depots/main/x86_64
chmod -R 770 /var/depots/main/x86_64
```

- From an administration machine connected to the same network, extract the archive alpine.tar containing the Alpine repository files into the `/tmp/alpine` folder, then type the following commands:
```
scp /tmp/alpine/main/x86_64/dosfstools-*.apk admin@192.168.10.3:/var/depots/alpine/main/x86_64
scp /tmp/alpine/main/x86_64/grub-efi-*.apk admin@192.168.10.3:/var/depots/alpine/main/x86_64
scp /tmp/alpine/main/x86_64/sfdisk-*.apk admin@192.168.10.3:/var/depots/alpine/main/x86_64
scp /tmp/alpine/main/x86_64/lddtree-*.apk admin@192.168.10.3:/var/depots/alpine/main/x86_64
scp /tmp/alpine/main/x86_64/xz-libs-*.apk admin@192.168.10.3:/var/depots/alpine/main/x86_64
scp /tmp/alpine/main/x86_64/zstd-libs-*.apk admin@192.168.10.3:/var/depots/alpine/main/x86_64
scp /tmp/alpine/main/x86_64/kmod-*.apk admin@192.168.10.3:/var/depots/alpine/main/x86_64
scp /tmp/alpine/main/x86_64/argon2-libs-*.apk admin@192.168.10.3:/var/depots/alpine/main/x86_64
scp /tmp/alpine/main/x86_64/device-mapper-libs-*.apk admin@192.168.10.3:/var/depots/alpine/main/x86_64
scp /tmp/alpine/main/x86_64/json-c-*.apk admin@192.168.10.3:/var/depots/alpine/main/x86_64
scp /tmp/alpine/main/x86_64/cryptsetup-libs-*.apk admin@192.168.10.3:/var/depots/alpine/main/x86_64
scp /tmp/alpine/main/x86_64/mkinitfs-*.apk admin@192.168.10.3:/var/depots/alpine/main/x86_64
scp /tmp/alpine/main/x86_64/grub-*.apk admin@192.168.10.3:/var/depots/alpine/main/x86_64
scp /tmp/alpine/main/x86_64/libfdisk-*.apk admin@192.168.10.3:/var/depots/alpine/main/x86_64
scp /tmp/alpine/main/x86_64/libsmartcols-*.apk admin@192.168.10.3:/var/depots/alpine/main/x86_64
scp /tmp/alpine/main/x86_64/linux-lts.apk admin@192.168.10.3:/var/depots/alpine/main/x86_64
scp /tmp/alpine/main/x86_64/linux-firmware*.apk admin@192.168.10.3:/var/depots/alpine/main/x86_64
scp /tmp/alpine/main/x86_64/openssh*.apk admin@192.168.10.3:/var/depots/alpine/main/x86_64
scp /tmp/alpine/main/x86_64/ncurses*.apk admin@192.168.10.3:/var/depots/alpine/main/x86_64
scp /tmp/alpine/main/x86_64/libedit*.apk admin@192.168.10.3:/var/depots/alpine/main/x86_64
scp /tmp/alpine/main/x86_64/busybox*.apk admin@192.168.10.3:/var/depots/alpine/main/x86_64
```

- Edit the file `/etc/apk/repositories` and add the line `/var/depots/alpine/main`

- Type the command `apk update` then Enter.

- Type the command `setup-disk` then Enter.

- At the question `Which disk(s) do you like to use?`, type `sda` then Enter.

- At the question `How would you like to use it?`, type `sys` then Enter.

- At the question `WARNING: Erase the above disk(s) and continue?`, type `y` then Enter.

- At the end of installation, type `reboot`.

- At the login prompt, type `root` then Enter. Authentication is done.

- Type the command `setup-hostname` then Enter, then `depots.local`, then Enter.

- Type the command `passwd` then Enter. Enter a strong password for the root account (twice).

- Type the following commands:
```
mkdir -p /var/depots/alpine/
chown -R admin:admin /var/depots/
chmod -R 770 /var/depots/
```

- From the administration machine, type the following commands:
```
cd [directory containing alpine files with folders main and community]
scp -r main community admin@192.168.10.3:/var/depots/alpine
```

- Edit the file `/etc/apk/repositories` and add the following lines:
```
/var/depots/alpine/main
/var/depots/alpine/community
```

- Type the command `apk update` then Enter.

- Type the command `setup-timezone` then Enter, then `Europe/Paris`, then Enter.

- Type the following commands:
```
apk add lighttpd
rc-update add lighttpd default
```

- Edit the file `/etc/lighttpd/lighttpd.conf` and add at the end of the file: `server.dir-listing = "enable"`

### Repositories on Network Storage (CIFS)

If the repository mirror is on a network storage accessible via CIFS (Windows file share), this virtual machine will only serve as an intermediary. Configuration can be done as follows.

**Configuration summary:**  
The virtual machine will be configured as a normal network server with a hostname. 512 MB of RAM is sufficient.

- Boot the machine using the standard Alpine ISO.

- At the login prompt, type `root` then Enter. Authentication is done.

- Type the command `setup-keymap`. Then type `fr`, Enter, `fr`, Enter. The keyboard is now French.

- Type the command `setup-interfaces`.

- At the question `Which one do you want to initialize?`, type `eth0` then Enter.

- At the question `Ip address for eth0?`, type `dhcp` then Enter.

- At the question `Do you want to do any manual network configuration?`, type `n` then Enter.

- Type the command `/etc/init.d/networking restart`. The server is now configured with the IP address provided by the DHCP server.

- Type the command `rc-update add networking`.

- Type the command `setup-sshd` then Enter.

- At the question `Which SSH server`, type `openssh` then Enter.

- The SSH server is now configured.

- Type the command `adduser admin` then Enter. Then enter a strong password twice consecutively.

*TO BE COMPLETED*

### DHCP Server

The DHCP server must be installed from an Alpine Linux standard ISO 3.15 minimum.

- Boot the machine using the standard Alpine ISO.

- At the login prompt, type `root` then Enter. Authentication is done.

- Type the command `setup-alpine` then Enter.

- *to be completed*

Then follow the instructions in the *Common configuration* section.

### HTTP/TFTP/NFS Server

The HTTP/TFTP/NFS server must be installed from an Alpine Linux standard ISO 3.15 minimum.

- Boot the machine using the standard Alpine ISO.

- At the login prompt, type `root` then Enter. Authentication is done.

- Type the command `setup-alpine` then Enter.

- *to be completed*

Then follow the instructions in the *Common configuration* section.

### Common Configuration

Each machine must be configured with a user allowing deployment of services via Ansible.

- Type the command `adduser ansible` then Enter. Enter a strong password for the user (twice consecutively).

- Add the following lines in the file `/etc/apk/repositories`:
```
http://192.168.10.3/alpine/main
http://192.168.10.3/alpine/community
```

- Type the command `visudo` then Enter.

## Services Deployment

*to be written*