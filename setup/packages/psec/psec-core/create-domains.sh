#!/bin/sh

. /etc/psec/constants.sh

### A Déplacer dans constants.sh
export APKOVL_TEMPLATE="/usr/lib/psec/system/domu.apkovl.tar.gz"
export LOCAL_PGP_PUBKEY="/etc/apk/keys/local.rsa.pub"

## Local variables
export WORKDIR="/tmp/domu.tmp"

if [ $# -lt 2 ]; then
  echo "Mandatory arguments missing."
  echo $0 DOMAIN_NAME MAIN_PACKAGE
  exit 1
fi

DOMAIN=$1
MAIN_PACKAGE=$2
export BOOTISO_FILENAME="bootiso-$DOMAIN.iso"

echo Create new XEN User Domain $DOMAIN 
echo - main package : $MAIN_PACKAGE

modprobe iso9660

echo ... Prepare
rm -rf $WORKDIR 
mkdir -p $WORKDIR/iso
mkdir -p $WORKDIR/apkovl
umount /mnt/bootiso
mkdir -p /mnt/bootiso

echo ... Mount original ISO
mount -o loop $ALPINE_ISO_LOCAL /mnt/bootiso

echo ... Copy original ISO
cp -r /mnt/bootiso/* $WORKDIR/iso

echo ... Uncompress APK overlay template
tar xzf $APKOVL_TEMPLATE -C $WORKDIR/apkovl

cd $WORKDIR/apkovl

echo ... Configure main package
echo "
psec-lib
$MAIN_PACKAGE" >> $WORKDIR/apkovl/etc/apk/world

echo ... Configure PSEC library
mkdir -p $WORKDIR/apkovl/etc/psec
echo "{
    \"identifiant_domaine\": \"$DOMAIN\",
    \"chemin_journal\": \"/var/log/psec/psec-lib.log\",
    \"niveau_debug\": \"DEBUG\",
    \"chemin_journal_local\": \"/var/log/psec/psec-lib.log\",
    \"chemin_socket_messagerie_locale\": \"/var/run/psec-api.sock\",
    \"nom_domaine_gui\": \"sys-gui\"
}
" > $WORKDIR/apkovl/etc/psec/global.conf

echo ... Copy local PGP key
cp $LOCAL_PGP_PUBKEY $WORKDIR/apkovl/etc/apk/keys

echo ... Set permissions
chmod +x etc/init.d/*
chown 0:0 etc/init.d/*

echo ... Create new APK overlay
cd $WORKDIR/apkovl
tar czf $WORKDIR/iso/domu.apkovl.tar.gz .

echo ... Create new ISO
mkisofs -r -V "BOOT" -cache-inodes -J -l -b boot/syslinux/isolinux.bin -c boot/syslinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table -o /tmp/$BOOTISO_FILENAME $WORKDIR/iso
mv /tmp/$BOOTISO_FILENAME /usr/lib/psec/system/

echo ... Clean
umount /mnt/bootiso

echo ""
echo Creating domains from topology file located at /etc/psec/topology.json
/usr/bin/python3 /usr/lib/psec/bin/create-domains.py