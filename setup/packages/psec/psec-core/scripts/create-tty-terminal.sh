#!/bin/sh

while [ ! -e "/dev/tty-admin" ]; do
    sleep 1
done

while true; do
    setsid agetty -h -t 60 -L tty-admin vt100
done