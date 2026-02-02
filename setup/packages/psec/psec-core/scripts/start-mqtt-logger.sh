#!/bin/sh

echo Starting mosquitto debugging

mkdir -p /var/log/psec
rm -f /var/log/psec/messages.log

mosquitto_sub -t "#" -v | while IFS= read -r line; do
    printf "[%s] %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$line"
done >> /var/log/psec/messages.log
