#!/bin/sh

PCI_USB_LABEL='USB controller'
MODE="add"

if [ $# -eq 0 ]
    then
        echo "No argument. Add mode."
    else
        MODE=$1
        echo "Using mode : $MODE."        
fi

# L'objectif est d'assigner les slots PCI des contrôleurs USB
# A la machine virtuelle vm-sys-usb
echo "Identify USB controllers"

# Get the PCI blacklist
blacklist=$(sed -n '/"pci":/,/}/p' /etc/psec/topology.json | grep '"blacklist":' | sed -n 's/.*"blacklist": "\([^"]*\)".*/\1/p')

pciusb=""
for f in `lspci | grep "$PCI_USB_LABEL" | cut -d " " -f 1`; do 
    echo "PCI USB controller identified: $f"
    present=$(echo "$blacklist" | grep "$f")
    if [ -z "$pciusb" ]
    then 
        if [ -z "$present" ]; then
            pciusb="$f"
        else
            echo "le bus PCI $pciusb est blacklisté"            
        fi
    else 
        if [ -z "$present" ]; then
            pciusb="$pciusb $f"
        else
            echo "le bus PCI $pciusb est blacklisté"            
        fi
    fi
done

_pciusb=`echo $pciusb | sed "s/ / /g"`

touch /etc/conf.d/xen-pci
source /etc/conf.d/xen-pci
rm -f /usr/lib/psec/tmp/xen-pci
echo "DEVICES=\"$pciusb\"" >> /usr/lib/psec/tmp/xen-pci

# Restore VGA_DEVICES settings
if [ -n "$VGA_DEVICES" ]
then 
    echo "VGA_DEVICES=\"$VGA_DEVICES\"" >> /usr/lib/psec/tmp/xen-pci
fi

rm /etc/conf.d/xen-pci.orig
mv /etc/conf.d/xen-pci /etc/conf.d/xen-pci.orig
mv /usr/lib/psec/tmp/xen-pci /etc/conf.d/xen-pci

