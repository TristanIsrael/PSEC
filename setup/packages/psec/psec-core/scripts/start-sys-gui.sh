#!/bin/sh

DISPLAY=:0 xl create -f /etc/psec/xen/sys-gui.conf

# We show the splash back
DISPLAY=:0 feh --fullscreen --zoom fill /boot/Splash.png &