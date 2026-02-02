#!/bin/sh

NEW_ARGS=$(echo "$@" | sed 's/-vnc none//g')
#echo $NEW_ARGS > /tmp/debug.cmd
exec /usr/bin/qemu-system-x86_64.real $NEW_ARGS