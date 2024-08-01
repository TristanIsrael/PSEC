#!/bin/sh

. /etc/psec/constants.sh

echo Setup XEN environment

if grep -q "PANOPTISCAN_CONFIG=nomade" "/proc/cmdline"; then
    echo ... Verify Alpine ISO image
    if [ -f $ALPINE_ISO_LOCAL ]
    then 
        echo "    Image ready"
    else 
        echo "    Image not found. Abandon."
        exit 1
    fi
else
    if [ -f $ALPINE_ISO_LOCAL ]
    then 
        echo "... Alpine ISO image already downloaded"        
    else
        echo "... Download Alpine ISO image"
        mkdir -p /var/lib/xen/images 
        echo "    Source : $ALPINE_ISO_URL"
        wget $ALPINE_ISO_URL -O $ALPINE_ISO_LOCAL
    fi
fi

echo "... Download boot files (kernel, initrd)"
mkdir -p /var/lib/xen/boot
mkdir -p /tmp/alpine-virt
modprobe iso9660
mount -o loop $ALPINE_ISO_LOCAL /media/cdrom
cp /media/cdrom/boot/vmlinuz-virt /var/lib/xen/boot
cp /media/cdrom/boot/modloop-virt /var/lib/xen/boot
cp /media/cdrom/boot/initramfs-virt /var/lib/xen/boot
umount /media/cdrom

echo Terminé