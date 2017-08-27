#!/bin/bash

if [[ -f "$APACHE_PID_FILE" ]]; then
    rm "$APACHE_PID_FILE"
fi

/usr/sbin/apache2ctl -D FOREGROUND
