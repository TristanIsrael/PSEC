#!/bin/sh

socat UNIX-CONNECT:/var/run/sys-usb-tty.sock PTY,link=/dev/tty-admin,raw,echo=0