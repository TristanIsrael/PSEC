#!/bin/sh

echo Setup Alpine local repository

. /etc/psec/constants.sh

echo "$ALPINE_PUBLIC_MAIN_REPOSITORY
$ALPINE_PUBLIC_COMMUNITY_REPOSITORY
$PSEC_PUBLIC_REPOSITORY
" > /etc/apk/repositories

apk update