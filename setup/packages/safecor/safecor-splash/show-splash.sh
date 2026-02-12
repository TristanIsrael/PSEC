#!/bin/sh

if grep -qw "nosplash" /proc/cmdline; then
    ewarn "Splash explicitely disabled on kernel command line"
    return 0
fi

nohup fbi -d /dev/fb0 -T 1 -noverbose -nointeractive /boot/splash.png  > /dev/null 2>&1 &