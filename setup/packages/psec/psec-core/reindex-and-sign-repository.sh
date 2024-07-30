#!/bin/sh

. /etc/psec/constants.sh

echo "Sign local alpine repository"
cd $ALPINE_LOCAL_REPOSITORY/`uname -m`
apk index -d ALPINE -o APKINDEX.tar.gz *.apk
abuild-sign -k /$USER/.abuild/local.rsa -p /$USER/.abuild/local.rsa.pub APKINDEX.tar.gz

echo "Signature du dépôt local Panoptiscan"
cd $PSEC_LOCAL_REPOSITORY/`uname -m`
apk index -d PSEC -o APKINDEX.tar.gz *.apk
abuild-sign -k /$USER/.abuild/local.rsa -p /$USER/.abuild/local.rsa.pub APKINDEX.tar.gz