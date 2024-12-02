#!/bin/sh

LABEL=$ID_FS_LABEL_ENC
FS=$ID_FS_TYPE
MOUNT_POINT=/media/usb/$LABEL
DEVICE=$DEVNAME
SCRIPTS_PATH=/usr/lib/psec/bin
LOG_FILENAME=/var/log/psec/udev.log

mkdir -p `dirname $LOG_FILENAME`

#echo "Action : $ACTION" >> $LOG_FILENAME

if [ "$ACTION" == "add" ]
then
	echo "Mouting disk $LABEL with filesystem $FS in $MOUNT_POINT" >> $LOG_FILENAME
	echo mount $DEVICE $MOUNT_POINT >> $LOG_FILENAME >> $LOG_FILENAME
	mkdir -p $MOUNT_POINT
	mount $DEVICE $MOUNT_POINT >> $LOG_FILENAME 2>&1

    if [ $? -eq 0 ]
    then
        echo "... Success, notify PSEC controller" >> $LOG_FILENAME
        #/usr/bin/python3 $SCRIPTS_PATH/notify-disk-added.py "$LABEL"
    fi
fi

if [ "$ACTION" == "remove" ]
then
	echo "Umounting $MOUNT_POINT" >> $LOG_FILENAME >> $LOG_FILENAME
	umount $MOUNT_POINT >> $LOG_FILENAME 2>&1

    if [ $? -eq 0 ]
    then
        echo "... Success, notify PSEC controller" >> $LOG_FILENAME
        #/usr/bin/python3 $SCRIPTS_PATH/notify-disk-removed.py "$LABEL"
    fi

	rmdir $MOUNT_POINT
fi

if [ "$ACTION" == "change" ] 
then
    if [ -n "$FS" ]
    then
        echo "Change state for $MOUNT_POINT with FS $FS and label $LABEL" >> $LOG_FILENAME >> $LOG_FILENAME

        echo "Mouting disk $LABEL with filesystem $FS in $MOUNT_POINT" >> $LOG_FILENAME
        echo mount $DEVICE $MOUNT_POINT >> $LOG_FILENAME >> $LOG_FILENAME
        mkdir -p $MOUNT_POINT
        mount $DEVICE $MOUNT_POINT >> $LOG_FILENAME 2>&1

        if [ $? -eq 0 ]
        then
            echo "... Success, notify PSEC controller" >> $LOG_FILENAME
            #/usr/bin/python3 $SCRIPTS_PATH/notify-disk-added.py "$LABEL"
        fi
    fi
fi