#!/bin/sh

mosquitto_sub --unix /var/run/mosquitto/mqtt_log.sock -t '#' --pretty -v