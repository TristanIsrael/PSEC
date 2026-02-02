# safecor-sys-usb

## Boot sequence

- DomU is started with a single disk, which is the ISO of Alpine Linux
- The ISO is booted
- The APK Overlay file is loaded
- Packages repository is mounted from `/etc/fstab`
- Needed packages are installed