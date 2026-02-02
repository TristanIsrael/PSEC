#!/bin/sh

mosquitto_sub --unix /tmp/mqtt_msg_local.sock -t 'system/events' --pretty -v