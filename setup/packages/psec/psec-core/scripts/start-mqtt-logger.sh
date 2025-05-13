#!/bin/sh

echo Starting mosquitto debugging
mkdir -p /var/log/psec
mosquitto_sub -t "#" -v >> /var/log/psec/messages.log
