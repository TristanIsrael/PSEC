#!/bin/sh

while true; do
    agetty -o 38400,8n1 tty-admin vt100
done