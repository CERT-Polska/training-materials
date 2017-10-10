#!/bin/bash

if [[ -f "$APACHE_PID_FILE" ]]; then
    sudo rm "$APACHE_PID_FILE"
fi
sudo chown 1000:33 /opt/intelmq/etc/*.conf
chmod 664 /opt/intelmq/etc/*.conf
touch /tmp/file-output/events.txt
sudo /usr/sbin/apache2ctl -D FOREGROUND
