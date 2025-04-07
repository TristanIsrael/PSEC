#!/bin/sh

. /etc/psec/constants.sh

echo Setup XEN environment

CONFIG_REPO=`jq -r '.network.repository' /etc/psec/topology.json`
CONFIG_RELEASES=`jq -r '.network.releases' /etc/psec/topology.json`

if grep -q "PANOPTISCAN_CONFIG=nomade" "/proc/cmdline"; then
    echo ... Verify Alpine ISO image
    if [ -f $ALPINE_VIRT_ISO_LOCAL ]
    then 
        echo "    Image ready"
    else 
        echo "    Image not found. Abandon."
        exit 1
    fi
else
    rm -rf /var/lib/xen/boot
    rm -rf /usr/lib/psec/tmp/alpine-virt

    if [ -f $ALPINE_VIRT_ISO_LOCAL ]
    then 
        echo "... Alpine virt ISO image is PRESENT"
    else
        echo "... Alpine virt ISO image is MISSING"
        exit 1

    :'    echo "... Download Alpine ISO image"
        mkdir -p /var/lib/xen/images 

        if [ -n "$CONFIG_RELEASES" ] && [ "$CONFIG_RELEASES" != "null" ]
        then
            echo "    Source : $CONFIG_RELEASES/$ALPINE_VIRT_ISO_FILENAME"
            wget "$CONFIG_RELEASES/$ALPINE_VIRT_ISO_FILENAME" -O $ALPINE_VIRT_ISO_LOCAL             
        else 
            echo "    Source : $ALPINE_VIRT_ISO_URL"
            wget $ALPINE_VIRT_ISO_URL -O $ALPINE_VIRT_ISO_LOCAL
        fi
    '
    fi
    
    echo "... Extract boot files (kernel, initrd)"    
    mkdir -p /var/lib/xen/boot
    mkdir -p /usr/lib/psec/tmp/alpine-virt
    modprobe iso9660
    mount -o loop $ALPINE_VIRT_ISO_LOCAL /media/cdrom
    cp /media/cdrom/boot/vmlinuz-* /var/lib/xen/boot
    cp /media/cdrom/boot/modloop-* /var/lib/xen/boot
    cp /media/cdrom/boot/initramfs-* /var/lib/xen/boot
    umount /media/cdrom

    if [ -f $ALPINE_LTS_ISO_LOCAL ]
    then 
        echo "... Alpine standard ISO image is PRESENT"
    else
        echo "... Alpine standard ISO image is MISSING"
        exit 1

    :'
        mkdir -p /var/lib/xen/images 

        if [ -n "$CONFIG_RELEASES" ] && [ "$CONFIG_RELEASES" != "null" ]
        then 
            echo "    Source : $CONFIG_RELEASES/$ALPINE_LTS_ISO_FILENAME"
            wget "$CONFIG_RELEASES/$ALPINE_LTS_ISO_FILENAME" -O $ALPINE_LTS_ISO_LOCAL
        else
            echo "    Source : $ALPINE_LTS_ISO_URL"
            wget $ALPINE_LTS_ISO_URL -O $ALPINE_LTS_ISO_LOCAL             
        fi
    '
    fi

    echo "... Extract boot files (kernel, initrd)"    
    mkdir -p /var/lib/xen/boot
    mkdir -p /usr/lib/psec/tmp/alpine-standard
    modprobe iso9660
    mount -o loop $ALPINE_LTS_ISO_LOCAL /media/cdrom
    cp /media/cdrom/boot/vmlinuz-* /var/lib/xen/boot
    cp /media/cdrom/boot/modloop-* /var/lib/xen/boot
    cp /media/cdrom/boot/initramfs-* /var/lib/xen/boot
    umount /media/cdrom    
fi

echo Terminé