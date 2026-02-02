#!/bin/sh

echo Setup Alpine local repository

echo *** Deprecated ***
exit 0

. /etc/safecor/constants.sh

echo "$ALPINE_PUBLIC_MAIN_REPOSITORY
$ALPINE_PUBLIC_COMMUNITY_REPOSITORY
$SAPHIR_PUBLIC_REPOSITORY
" > /etc/apk/repositories

apk update