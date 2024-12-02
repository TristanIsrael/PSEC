#!/bin/sh

mosquitto_sub --unix /var/run/mosquitto/mqtt_msg.sock -t 'system/events' --pretty -v