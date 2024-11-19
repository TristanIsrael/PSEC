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

touch /etc/conf.d/xen-pci
source /etc/conf.d/xen-pci
rm -f /usr/lib/psec/tmp/xen-pci

echo "VGA_DEVICES=\"$pciusb\"" >> /usr/lib/psec/tmp/xen-pci

# Restore USB settings
if [ -n "$DEVICES" ]
then
    echo "DEVICES=\"$DEVICES\"" >> /usr/lib/psec/tmp/xen-pci
fi 

rm /etc/conf.d/xen-pci.orig
mv /etc/conf.d/xen-pci /etc/conf.d/xen-pci.orig
mv /usr/lib/psec/tmp/xen-pci /etc/conf.d/xen-pci
