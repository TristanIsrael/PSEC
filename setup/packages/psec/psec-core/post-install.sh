#!/bin/sh

/usr/lib/psec/bin/finish-core-init.sh

rc-service start-domains start
rc-service connect-to-gui start