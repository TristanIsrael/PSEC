#!/bin/sh

mosquitto_sub --unix /var/run/mosquitto/mqtt_msg_local.sock -t 'system/events' --pretty -v