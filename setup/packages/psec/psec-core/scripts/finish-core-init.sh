#!/bin/sh

#if [ -n "$OPENRC_RUNLEVEL" ]
#then
#    echo "Started from initd, ignored"
#else
    . /etc/psec/constants.sh

    mkdir -p /usr/lib/psec/storage
    mkdir -p /usr/lib/psec/packages
    mkdir -p /etc/psec/xen
    mkdir -p /var/log/psec

    /usr/lib/psec/bin/generate-pgp-keys.sh
    /usr/lib/psec/bin/setup-alpine-repositories.sh
    /usr/lib/psec/bin/create-local-alpine-repository.sh
    /usr/lib/psec/bin/setup-xen-environment.sh

    echo ... Start initd scripts
    rc-service setup-pci start

    echo Create XEN Domains
    /usr/bin/python3 /usr/lib/psec/bin/create-domains.py $ALPINE_LOCAL_REPOSITORY/`uname -m`

    rc-service orchestrator start

    #rc-service xen-pci start
    #rc-service attach-pci-devices start    
    #rc-service start-domains start
#fi