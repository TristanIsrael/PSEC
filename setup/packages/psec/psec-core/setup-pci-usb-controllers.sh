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
pciusb=""
for f in `lspci | grep "$PCI_USB_LABEL" | cut -d " " -f 1`; do 
    echo "PCI USB controller identified: $f"
    if [ -z "$pciusb" ]
    then 
        pciusb="$f"
    else 
        pciusb="$pciusb $f"; 
    fi
done

_pciusb=`echo $pciusb | sed "s/ / /g"`

source /etc/conf.d/xen-pci
rm -f /tmp/xen-pci
#head -n -1 /etc/conf.d/xen-pci > /tmp/xen-pci
if [ -n "$DEVICES" ]
then 
    echo "DEVICES=\"$pciusb\"" >> /tmp/xen-pci
#else
#    echo "DEVICES=\"$DEVICES $pciusb\"" >> /tmp/xen-pci
fi 

# Restore VGA_DEVICES settings
if [ -n "$VGA_DEVICES" ]
then 
    echo "VGA_DEVICES=\"$VGA_DEVICES\"" >> /tmp/xen-pci
fi

mv /etc/conf.d/xen-pci /etc/conf.d/xen-pci.orig
mv /tmp/xen-pci /etc/conf.d/xen-pci

