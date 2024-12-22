#!/bin/sh

export ALPINE_VERSION="3.20"

export ALPINE_LOCAL_ROOT=/usr/lib/psec/packages
export ALPINE_LOCAL_REPOSITORY=$ALPINE_LOCAL_ROOT/alpine
#export PSEC_LOCAL_REPOSITORY=$ALPINE_LOCAL_ROOT/psec

export PSEC_PUBLIC_REPOSITORY="https://alefbet.net/wp-content/uploads/repositories/PSEC"

ALPINE_PUBLIC_ROOT="http://dl-cdn.alpinelinux.org/alpine"
export ALPINE_PUBLIC_MAIN_REPOSITORY="$ALPINE_PUBLIC_ROOT/v$ALPINE_VERSION/main"
export ALPINE_PUBLIC_COMMUNITY_REPOSITORY="$ALPINE_PUBLIC_ROOT/v$ALPINE_VERSION/community"
export ALPINE_PUBLIC_RELEASES_REPOSITORY="$ALPINE_PUBLIC_ROOT/v$ALPINE_VERSION/releases"
ALPINE_RELEASE=`cat /etc/alpine-release`
ARCH=`uname -m`
RELEASES_ALPINE="$ALPINE_PUBLIC_ROOT/v$ALPINE_VERSION/releases"
export ALPINE_VIRT_ISO_URL="$RELEASES_ALPINE/$ARCH/alpine-virt-$ALPINE_RELEASE-$ARCH.iso"
export ALPINE_VIRT_ISO_LOCAL=/var/lib/xen/images/alpine-virt.iso
export ALPINE_LTS_ISO_URL="$RELEASES_ALPINE/$ARCH/alpine-standard-$ALPINE_RELEASE-$ARCH.iso"
export ALPINE_LTS_ISO_LOCAL=/var/lib/xen/images/alpine-standard.iso

export LOCAL_PGP_PUBKEY=/etc/apk/keys/local.rsa.pub
