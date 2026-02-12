#!/bin/sh

nohup fbi -d /dev/fb0 -T 1 -noverbose -nointeractive /boot/splash.png  > /dev/null 2>&1 &