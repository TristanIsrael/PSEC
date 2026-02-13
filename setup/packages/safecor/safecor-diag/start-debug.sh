#!/bin/sh

if grep -q "serial-debug" "/proc/cmdline"; then 
    PWD=""

    for arg in $(cat /proc/cmdline); do
        case "$arg" in
            debug-passwd=*)
                PWD="${arg#debug-passwd=}"
                ;;
        esac
    done

    if [ -n "$PWD" ]; then
        # Set root's password provided
        printf "root:%s\n" "$PWD" | chpasswd   
    else
        # Define a random password for root
        PWD=$(head -c 16 /dev/urandom | base64 | tr -dc 'A-Za-z0-9')
        printf "root:%s\n" "$PWD" | chpasswd 
        exit 0
    fi    

    # Create TTY console on ttyS0
    nohup /usr/lib/safecor/bin/open-tty.sh ttyS0 &
    if [ $? -ne 0 ]; then
        echo "... Error"
        exit 1
    fi

    # Create TTY console on ttyUSB0
    nohup /usr/lib/safecor/bin/open-tty.sh ttyUSB0 &
    if [ $? -ne 0 ]; then
        echo "... Error"
        exit 2
    fi    
fi

exit 0