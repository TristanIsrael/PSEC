#!/bin/sh

/usr/lib/psec/bin/finish-core-init.sh

rc-service orchestrator start

#rc-service start-domains start
#rc-service connect-to-gui start


echo "***************************************"
echo "******          Safecor          ******"
echo "******          -------          ******"
echo "******                           ******"
echo "******   Installation finished   ******"
echo "******                           ******"
echo "***************************************"