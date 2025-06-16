# In case we connect from the serial debug port
# We need to set the columns to a larger value
# because by default it is 80.

if [ "$TERM" = "vt100" ]; then 
    stty cols 80
    stty rows 50
fi
