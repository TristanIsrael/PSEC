# Create a Bootable USB Drive

This procedure describes the process of creating a bootable USB drive.

## Procedure

- Download the official Alpine Standard ISO image ([Alpine Standard x86_64](`https://dl-cdn.alpinelinux.org/alpine/v3.21/releases/x86_64/alpine-standard-3.21.3-x86_64.iso`)).
- Copy the ISO to a USB drive: `$ sudo dd if=alpine-standard-xxx.iso of=/dev/xxx bs=4m`
- Boot from the USB drive
- Log in as `root`
- Type `# setup-alpine` and configure the system without disk installation or config storage
  - The script will fail
- Type `# apk add dosfstools wipefs`
- Plug in the new USB drive that will become the bootable system
  - Use `dmesg` to identify the new drive (e.g., `sdx`)
- Prepare the drive (see the *Bootable USB Drive Preparation* section)
- Unplug the ISO USB and keep only the new bootable USB drive
- Reboot from the new bootable USB drive
- Configure the repositories in `/etc/apk/repositories`
- If needed, remount the system in R/W mode: `# mount -o remount,rw /dev/sda1 /media/usb`
- Type `# setup-apkcache /media/usb/cache`
- Type `# apk cache -v sync`
- Type `# setup-lbu usb`
- Type `# lbu commit -d`
- The bootable system is ready
  - *Install the necessary packages for building the USB bootable product*
  - The configuration will be stored on the USB drive
  - Optionally, remove network and repository settings for a faster boot

### Bootable USB Drive Preparation

Run the following commands to prepare the bootable USB drive (replace `sdx` with the correct identifier):

```
# wipefs -a /dev/sdx

# fdisk -w always /dev/sdx <<EOF
o
n
p
1
2048
-0
t
0c
a
w
EOF
``` 

Format the drive: `# mkdosfs -F32 /dev/sdx1`

Make it bootable with Alpine: `# setup-bootable -vUfs /media/sda /dev/sdx1`, first check whether the ISO image is mounted on `/media/usb` or `/media/sda` (for example).