#!/bin/sh

# Read screen size
#domid=`xenstore-read domid`
screen_size=`xenstore-read /local/domain/system/screen_size`

# Read screen orientation
screen_rotation=`xenstore-read /local/domain/system/screen_rotation`

# Compute the resolution with the orientation
normalized_rotation=$(( (screen_rotation % 360 + 360) % 360 ))

# Extraction de la largeur et de la hauteur
width=$(echo "$screen_size" | cut -d',' -f1)
height=$(echo "$screen_size" | cut -d',' -f2)

# Calcul de la nouvelle résolution en fonction de la rotation
case $normalized_rotation in
    0|360)
        new_width=$width
        new_height=$height
        ;;
    90|270)
        new_width=$height
        new_height=$width
        ;;
    180)
        new_width=$width
        new_height=$height
        ;;
    *)
        echo "Rotation invalide : $screen_rotation"
        exit 1
        ;;
esac

DISPLAY=:0 xl create -f /etc/psec/xen/sys-gui.conf
sleep 1

# Resize GTK window to fill the display
DISPLAY=:0 xdotool windowsize `DISPLAY=:0 xdotool search --name "sys-gui"` $new_width $new_height

# We show the splash back
DISPLAY=:0 feh --fullscreen --zoom fill /boot/Splash.png &