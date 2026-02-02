#!/bin/sh

. /etc/safecor/constants.sh

export APKOVL_TEMPLATE="/usr/lib/safecor/system/domu.apkovl.tar.gz"
export LOCAL_PGP_PUBKEY="/etc/apk/keys/local.rsa.pub"

## Local variables
export WORKDIR="/usr/lib/safecor/tmp/domu.tmp"

if [ $# -lt 4 ]; then
  echo "Mandatory arguments missing."
  echo "$0 [Domain name] [Main package] [Alpine branch (virt|lts)] [blacklist.conf file path]"
  exit 1
fi

DOMAIN=$1
MAIN_PACKAGE=$2
ALPINE_BRANCH=$3
ALPINE_BRANCH=${ALPINE_BRANCH:-virt}
BLACKLIST_CONF=$4

# Vérifier la valeur de $ALPINE_BRANCH et définir $BOOTISO_FILENAME en conséquence
case "$ALPINE_BRANCH" in
  lts)
    export ALPINE_ISO_LOCAL=$ALPINE_LTS_ISO_LOCAL
    ;;
  virt)
    export ALPINE_ISO_LOCAL=$ALPINE_VIRT_ISO_LOCAL
    ;;
  *)
    echo "Valeur inconnue pour ALPINE_BRANCH : $ALPINE_BRANCH"
    exit 1
    ;;
esac

export BOOTISO_FILENAME="bootiso-$DOMAIN.iso"

echo Create new XEN User Domain $DOMAIN 
echo - main package : $MAIN_PACKAGE
echo - Alpine branch : $ALPINE_BRANCH
echo - Alpine ISO comes from : $ALPINE_ISO_LOCAL
echo - Kernel modules blacklist : $BLACKLIST_CONF

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
safecor-lib
$MAIN_PACKAGE" >> $WORKDIR/apkovl/etc/apk/world

echo ... Configure Safecor library
mkdir -p $WORKDIR/apkovl/etc/safecor
echo "{
    \"identifiant_domaine\": \"$DOMAIN\",
    \"chemin_journal\": \"/var/log/safecor/safecor-lib.log\",
    \"niveau_debug\": \"DEBUG\",
    \"chemin_journal_local\": \"/var/log/safecor/safecor-lib.log\",
    \"chemin_socket_messagerie_locale\": \"/var/run/safecor-api.sock\",
    \"nom_domaine_gui\": \"sys-gui\"
}
" > $WORKDIR/apkovl/etc/safecor/global.conf

echo ... Configure hostname
echo "$DOMAIN" > $WORKDIR/apkovl/etc/hostname

echo ... Copy local PGP key
cp $LOCAL_PGP_PUBKEY $WORKDIR/apkovl/etc/apk/keys

echo ... Set permissions
chmod +x etc/init.d/*
chown 0:0 etc/init.d/*

if [ -e "$BLACKLIST_CONF" ]; then
    mkdir -p etc/modprobe.d
    echo ... Patch modules blacklist
    cat $BLACKLIST_CONF >> etc/modprobe.d/blacklist.conf
fi

echo ... Create new APK overlay
cd $WORKDIR/apkovl
tar czf $WORKDIR/iso/domu.apkovl.tar.gz .

echo ... Create new ISO
xorriso -as mkisofs -r -V "BOOT" -cache-inodes -J -l -b boot/syslinux/isolinux.bin -c boot/syslinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table -o /usr/lib/safecor/tmp/$BOOTISO_FILENAME $WORKDIR/iso
mv /usr/lib/safecor/tmp/$BOOTISO_FILENAME /usr/lib/safecor/system/

echo ... Clean
umount /mnt/bootiso
