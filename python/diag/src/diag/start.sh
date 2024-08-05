#!/bin/sh

# Chargement des variables d'environnement n..cessaires .. l'ex..cution du programme
# On n'utilise plus le driver evdev de Qt car il fonctionne pas sur les premiers essais
# Nous utilisons notre propre driver (voir LocalEventListener)
# source /etc/panoptiscan/commun.sh
# touchdev=`cat /proc/bus/input/devices | grep -B7 EV=1b | grep -B6 PROP=2 | grep Handlers | tr " " "\n" | grep "event" | sed "s/Handlers=//g"`
# echo Utilisation du périphérique tactile $touchdev
# export QT_QPA_EVDEV_TOUCHSCREEN_PARAMETERS=/dev/input/$touchdev
# export QT_QPA_GENERIC_PLUGINS=evdevtouch:/dev/input/$touchdev

while true
do
        /usr/bin/python3 /usr/lib/psec/diag/src/diag/main.py -platform linuxfb 
        #-plugin evdevtouch
done

# Configuration Touch
# touchdev=`cat /proc/bus/input/devices | grep -B7 EV=1b | grep Handlers | cut -d " " -f3`
# touchdev=`cat /proc/bus/input/devices | grep -B7 EV=1b | grep -B6 PROP=2 | grep Handlers | tr " " "\n" | grep "event" | sed "s/Handlers=//g"`
# export QT_QPA_EVDEV_TOUCHSCREEN_PARAMETERS=/dev/input/$touchdev:rotate=0
# export QT_QPA_GENERIC_PLUGINS=evdevtouch:/dev/input/$touchdev
# export QT_LOGGING_RULES="qt.qpa.input=true"
# export FORCE_PAYSAGE="Vrai" # Ou "Faux" pour laisser le mode par défaut
# 
# /usr/bin/python3 /usr/lib/panoptiscan/gui/main.py -platform linuxfb:fb=/dev/fb0 -plugin evdevtouch 