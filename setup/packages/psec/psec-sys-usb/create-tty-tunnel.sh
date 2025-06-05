#!/bin/sh

#if [ -e /dev/ttyUSB0 ]; then
#    socat /dev/ttyUSB0,raw,echo=0 /dev/hvc3,raw,echo=0
#fi

for device in /dev/ttyUSB*; do
    if [ -e "$device" ]; then 
        echo Create TTY tunnel for "$device"
        socat /dev/ttyUSB0,raw,echo=0 /dev/hvc3,raw,echo=0 &
    fi 
done
