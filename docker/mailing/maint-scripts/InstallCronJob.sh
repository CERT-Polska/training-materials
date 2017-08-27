#!/bin/bash

out="/etc/cron.d/mailgenerator"
cmd="/usr/bin/python /opt/mailgenerator/mailgenerator.py"
echo -e "MAILTO=\"\"" | tee -a $out
echo -e "* * * * * root $cmd" | tee -a $out
echo -e "* * * * * root (sleep 20; $cmd)" | tee -a $out
echo -e "* * * * * root (sleep 40; $cmd)" | tee -a $out
chmod 0600 $out
