#!/bin/sh

# Script: start-debug.sh
# Usage: ./start-debug.sh device-name
# Example: ./start-debug.sh ttyUSB0

if [ -z "$1" ]; then
    echo "Usage: $0 <fichier>"
    exit 1
fi

FILE="/dev/$1"

if [ -e "$FILE" ]; then
    # Authorize root login on this port
    echo $1 >> /etc/securetty

    while true; do
        setsid getty -h -t 60 -L 115200 $1 vt100
    done
else
    echo "The device '$FILE' does not exist."
fi
