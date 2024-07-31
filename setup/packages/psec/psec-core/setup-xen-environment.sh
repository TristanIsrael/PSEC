#!/bin/sh

. "/etc/psec/constants.sh"

echo Setup XEN environment

if grep -q "PANOPTISCAN_CONFIG=nomade" "/proc/cmdline"; then
    echo ... Verify Alpine ISO image
    if [ -f /var/lib/xen/images/alpine-virt.iso ]; then 
        echo "    Image ready"
    else 
        echo "    Image not found. Abandon."
        exit 1
    fi
else
    echo "... Download Alpine ISO image"
    mkdir -p /var/lib/xen/images 
    echo "    Source : $ALPINE_ISO_URL"
    wget $ALPINE_ISO_URL -O /var/lib/xen/images/alpine-virt.iso
fi

echo "... Download boot files (kernel, initrd)"
mkdir -p /var/lib/xen/boot
mkdir -p /tmp/alpine-virt
wget $ALPINE_PUBLIC_RELEASES_REPOSITORY/`uname -m`/alpine-virt-

vmlinuz-virt -O /var/lib/xen/boot/vmlinuz-virt
wget $DEPOT_ALPINE/release/modloop-virt -O /var/lib/xen/boot/modloop-virt
wget $DEPOT_ALPINE/release/initramfs-virt -O /var/lib/xen/boot/initramfs-virt
ln -s /var/lib/xen/boot $DEPOT_LOCAL