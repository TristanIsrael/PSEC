#!/bin/sh

echo Creating domains from topology file located at /etc/psec/topology.json

/usr/bin/python3 /usr/lib/psec/bin/create-domains.py