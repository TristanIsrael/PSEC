#!/bin/sh

echo Starting mosquitto debugging

mkdir -p /var/log/safecor
rm -f /var/log/safecor/messages.log

mosquitto_sub -t "#" -v | while IFS= read -r line; do
    printf "[%s] %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$line"
done >> /var/log/safecor/messages.log
