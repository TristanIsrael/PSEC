#!/bin/sh

if grep -q "serial-debug" "/proc/cmdline"; then 
    PASSWD=""

    for arg in $(cat /proc/cmdline); do
        case "$arg" in
            debug-passwd=*)
                PASSWD="${arg#debug-passwd=}"
                ;;
        esac
    done

    if [ -n "$PASSWD" ]; then
        # Set root's password provided
        logger -t safecor/start-debug "Password provided: setting root's password"
        printf "root:%s\n" "$PASSWD" | chpasswd   
    else
        # Define a random password for root
        PASSWD=$(head -c 16 /dev/urandom | base64 | tr -dc 'A-Za-z0-9')
        logger -t safecor/start-debug "Password not provided: setting random root's password"
        printf "root:%s\n" "$PASSWD" | chpasswd
        exit 0
    fi    

    # Create TTY console on ttyS0
    logger -t safecor/start-debug "Starting terminal on ttyS0"
    nohup /usr/lib/safecor/bin/open-tty.sh ttyS0 &
    if [ $? -ne 0 ]; then
        logger -t safecor/start-debug "... Error when starting terminal on ttyS0"
        exit 1
    fi

    # Create TTY console on ttyUSB0
    logger -t safecor/start-debug "Starting terminal on ttyUSB0"
    nohup /usr/lib/safecor/bin/open-tty.sh ttyUSB0 &
    if [ $? -ne 0 ]; then
        logger -t safecor/start-debug "... Error when starting terminal on ttyUSB0"
        exit 2
    fi    
fi

exit 0