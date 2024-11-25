#!/bin/sh

xl list | grep "^sys-gui" | awk '{print $2}'

return 0