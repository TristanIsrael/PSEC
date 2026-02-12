#!/bin/sh

# Script: start-debug.sh
# Usage: ./start-debug.sh device-name
# Example: ./start-debug.sh ttyUSB0

FILE="/dev/$1"

if [ -z "$1" ]; then
    echo "Usage: $0 <fichier>"
    exit 1
fi

if [ -e "$FILE" ]; then
    while true; do
        setsid agetty -h -t 60 -L $FILE vt100
    done
else
    echo "The device '$FILE' does not exist."
fi
