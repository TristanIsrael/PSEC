#!/bin/sh

if [ -n "$OPENRC_RUNLEVEL" ]
then
    echo "Started from initd, ignored"
else
    mkdir -p /usr/lib/psec/storage
    mkdir -p /usr/lib/psec/packages

    /usr/lib/psec/bin/generate-pgp-keys.sh
    /usr/lib/psec/bin/setup-alpine-repositories.sh
    /usr/lib/psec/bin/create-local-alpine-repository.sh
    /usr/lib/psec/bin/setup-xen-environment.sh

    echo Create system User Domains

    echo ... sys-usb
    /usr/lib/psec/bin/create-domu.sh sys-usb psec-sys-usb

    echo ... Start initd scripts
    rc-service setup-pci start
    rc-service xen-pci start
    rc-service attach-pci-devices start    
    #rc-service start-domains start
fi