#!/bin/sh

mosquitto_sub --unix /tmp/mqtt_msg_local.sock -t 'system/' --pretty -v