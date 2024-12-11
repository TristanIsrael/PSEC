#!/bin/sh

mosquitto_sub --unix /var/run/mosquitto/mqtt_msg.sock -t '#' --pretty -v