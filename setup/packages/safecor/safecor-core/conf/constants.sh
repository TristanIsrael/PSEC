#!/bin/sh

export ALPINE_VERSION=`cut -d'.' -f1,2 < /etc/alpine-release`

export ALPINE_LOCAL_ROOT=/usr/lib/safecor/packages
export ALPINE_LOCAL_REPOSITORY=$ALPINE_LOCAL_ROOT/alpine

export SAFECOR_PUBLIC_REPOSITORY="https://www.alefbet.net/github/safecor"

ALPINE_PUBLIC_ROOT="http://dl-cdn.alpinelinux.org/alpine"
export ALPINE_PUBLIC_MAIN_REPOSITORY="$ALPINE_PUBLIC_ROOT/v$ALPINE_VERSION/main"
export ALPINE_PUBLIC_COMMUNITY_REPOSITORY="$ALPINE_PUBLIC_ROOT/v$ALPINE_VERSION/community"
export ALPINE_PUBLIC_RELEASES_REPOSITORY="$ALPINE_PUBLIC_ROOT/v$ALPINE_VERSION/releases"
ALPINE_RELEASE=`cat /etc/alpine-release`
ARCH=`uname -m`
RELEASES_ALPINE="$ALPINE_PUBLIC_ROOT/v$ALPINE_VERSION/releases"
# Branch Alpine virt
export ALPINE_VIRT_ISO_URL="$RELEASES_ALPINE/$ARCH/alpine-virt-$ALPINE_RELEASE-$ARCH.iso"
export ALPINE_VIRT_ISO_LOCAL=/var/lib/xen/images/alpine-virt.iso
export ALPINE_VIRT_ISO_FILENAME="alpine-virt-$ALPINE_RELEASE-$ARCH.iso"
# Branch Alpine LTS (standard)
export ALPINE_LTS_ISO_URL="$RELEASES_ALPINE/$ARCH/alpine-standard-$ALPINE_RELEASE-$ARCH.iso"
export ALPINE_LTS_ISO_LOCAL=/var/lib/xen/images/alpine-standard.iso
export ALPINE_LTS_ISO_FILENAME="alpine-standard-$ALPINE_RELEASE-$ARCH.iso"

export LOCAL_PGP_PUBKEY=/etc/apk/keys/local.rsa.pub
