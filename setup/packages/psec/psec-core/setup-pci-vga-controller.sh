#!/bin/sh

MODE="add"
PCI_VGA_LABEL='VGA'

if [ $# -eq 0 ]
    then
        echo "No argument. Add mode."
    else
        MODE=$1
        echo "Using mode : $MODE."        
fi

# L'objectif est d'assigner les slots PCI du contrôleur VGA
# A la machine virtuelle vm-controleur
echo "Detecting VGA controllers"
pciusb=""
for f in `lspci | grep "$PCI_VGA_LABEL" | cut -d " " -f 1`; do 
    echo "PCI VGA controller identified: $f"
    if [ -z "$pciusb"]
    then 
        pciusb="$f"
    else 
        pciusb="$pciusb $f"; 
    fi
done

source /etc/conf.d/xen-pci
rm -f /tmp/xen-pci

echo "VGA_DEVICES=\"$pciusb\"" >> /tmp/xen-pci

# Restore USB settings
if [ -n "$DEVICES" ]
then
    echo "DEVICES=\"$DEVICES\"" >> /tmp/xen-pci
fi 

mv /etc/conf.d/xen-pci /etc/conf.d/xen-pci.orig
mv /tmp/xen-pci /etc/conf.d/xen-pci
