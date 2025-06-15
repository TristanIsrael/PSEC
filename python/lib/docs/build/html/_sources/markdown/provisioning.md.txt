# Provisioning

This document describes various methods to provision a device with a PSEC-based system.

## Manual

Manual provisioning consists of going through an installation process step-by-step using a USB drive.

1 - Create an installation USB stick for Alpine Linux.  
  - The Alpine Linux version must match the desired repository version.  
  - The ISO image used must be [**Alpine Standard**](https://dl-cdn.alpinelinux.org/alpine/v3.21/releases/x86_64/alpine-standard-3.21.3-x86_64.iso).

2 - Install Alpine Linux on the device.  
  - Assign a network interface with either DHCP or a static IP depending on the context.  
  - In the APK Mirror section, if using an internet repository, select `f`, otherwise do not select any menu entry but manually enter the URL of the local Alpine `main` repository.  
  - Create an `admin` user account.

3 - Reboot the system at the end of the installation.

4 - After reboot, log in as `admin`.

5 - Add binary repositories  
  - Type `$ su - root` and enter the password defined during the installation.  
  - Run `# vi /etc/apk/repositories` and add the `community` repository, the `PSEC` repository, and any product-specific repositories.  
  - Save and exit with `:wq`.
  - Run `# apk update`

6 - Add PGP keys  
  - Run `# cd /etc/apk/keys` then `# wget [PSEC repository URL]/psec.rsa.pub`, and repeat the process for other product-specific repositories.  
  - Run `# apk update`.

7 - (Optional, only in development phase) Allow the `admin` user to execute root commands  
  - Run `# apk add sudo`, then `# visudo`  
  - Edit the line `# %wheel ALL=(ALL:ALL) NOPASSWD: ALL` and remove the `#` to uncomment it.  
  - Save and exit with `:wq`  
  - Type `# exit`

8 - Install XEN  
  - Run `$ sudo apk add xen xen-hypervisor`  
  - Run `$ sudo reboot`  
  - On reboot, select the first GRUB entry labeled with `Xen`  
  - After booting, log in as `root`  
  - Start the Xen service with `# rc-service xenstored start`

9 - Install the product following the provided documentation.