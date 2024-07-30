#!/bin/sh

. "/etc/psec/constants.sh"

# Update overlay PGP key
echo "Injection de la clé du dépôt local dans le fichier d'overlay de boot domU par défaut"
mkdir /tmp/domu.apkovl
tar xzf /usr/local/psec/domu.apkovl.tar.gz -C /tmp/domu.apkovl

# Inject PGP key into the APK Overlay
cp -f /.abuild/local.rsa.pub /tmp/domu.apkovl/etc/apk/keys
rm /usr/local/psec/domu.apkovl.tar.gz

# Add default packages to the DomU configuration 
echo "psec-core
psec-lib" >> /tmp/domu.apkovl/etc/apk/world

# Close APK Overlay file
cd /tmp/domu.apkovl
mkdir -p /usr/local/psec/system
tar czf /usr/local/psec/system/domu.apkovl.tar.gz etc/
ln -s /usr/local/psec/system/domu.apkovl.tar.gz $PSEC_LOCAL_REPOSITORY
rm -r /tmp/domu.apkovl

if grep -q "PANOPTISCAN_CONFIG=nomade" "/proc/cmdline"; then
    echo "Verify Alpine ISO image"
    if [ -f /var/lib/xen/images/alpine-virt.iso ]; then 
        echo "Image ready"
    else 
        echo "Image not found. Abandon."
        exit 1
    fi
else
    echo "Download Alpine ISO image"
    mkdir -p /var/lib/xen/images 
    echo "Source : $ALPINE_ISO_URL"
    wget $ALPINE_ISO_URL -O /var/lib/xen/images/alpine-virt.iso
fi

echo "Download boot files (kernel, initrd)"
mkdir -p /var/lib/xen/boot
mkdir -p /tmp/alpine-virt
wget $ALPINE_PUBLIC_RELEASES_REPOSITORY/`uname -m`/alpine-virt-

vmlinuz-virt -O /var/lib/xen/boot/vmlinuz-virt
wget $DEPOT_ALPINE/release/modloop-virt -O /var/lib/xen/boot/modloop-virt
wget $DEPOT_ALPINE/release/initramfs-virt -O /var/lib/xen/boot/initramfs-virt
ln -s /var/lib/xen/boot $DEPOT_LOCAL