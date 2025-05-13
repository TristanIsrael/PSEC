#!/bin/sh

while [ ! -e "/var/run/sys-usb-tty.sock" ]; do
    sleep 1
done

socat UNIX-CONNECT:/var/run/sys-usb-tty.sock PTY,link=/dev/tty-admin,raw,echo=0,ctty