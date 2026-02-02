#!/bin/sh

. /etc/safecor/constants.sh

echo "Sign local Alpine repository"
cd $ALPINE_LOCAL_REPOSITORY/`uname -m`
apk index -d ALPINE -o APKINDEX.tar.gz *.apk
abuild-sign -k /.abuild/local.rsa -p /.abuild/local.rsa.pub APKINDEX.tar.gz
