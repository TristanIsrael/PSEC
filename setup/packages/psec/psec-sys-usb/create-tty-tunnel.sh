#!/bin/sh

if [ -e /dev/ttyUSB0 ]; then
    socat /dev/ttyUSB0,raw,echo=0 /dev/hvc3,raw,echo=0
fi