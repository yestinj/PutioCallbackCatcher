#!/bin/bash
PID=$(cat putiocatcher.pid)
kill -TERM $PID
if [ $? -eq 0 ]
then
    echo "Sent TERM signal to process $PID"
else
    echo "Unable to successfully kill $PID"
fi
