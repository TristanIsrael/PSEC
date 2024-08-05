#!/bin/sh

. /etc/psec/constants.sh

if grep -q "PANOPTISCAN_CONFIG=nomade" "/proc/cmdline"; then
    echo "*** La configuration est déjà nomadisée. Le dépôt est déjà prêt. ***"
    exit 0
fi

#REPODIR=/var/cache/alpine/`uname -m`
#PAN-127 : Le disque peut être préparé avant ou en RAM, la racine du dépôt est définie dans la variable REPO_ROOT
ALPINE_ARCH_DIR=$ALPINE_LOCAL_REPOSITORY/`uname -m`
#PSEC_ARCH_DIR=$PSEC_LOCAL_REPOSITORY/`uname -m`

echo Create local repositories
mkdir -p $ALPINE_ARCH_DIR
#mkdir -p $PSEC_ARCH_DIR
cd $ALPINE_LOCAL_REPOSITORY
ln -s `uname -m` noarch
#cd $PSEC_LOCAL_REPOSITORY
#ln -s `uname -m` noarch

# Construction d'un dépôt local pour les VM domU
# Le dépôt local sera signé avec sa propre clé
# Pour converger avec la configuration nomade il faut
# que les dépôts Alpine et Panoptiscan soient séparés
echo Fetch packages
cd $ALPINE_ARCH_DIR
apk fetch -R psec-lib psec-sys-usb 
# Récupération de dépendances supplémentaires
apk fetch -R libtirpc-conf krb5-conf eudev-openrc udev-init-scripts udev-init-scripts-openrc
# Separate PSEC packages from Alpine official
#mv psec* $PSEC_ARCH_DIR

/usr/lib/psec/bin/reindex-and-sign-repository.sh
