#!/bin/bash

out="/etc/cron.d/service_recon"
cmd="/usr/bin/python /opt/recon/service_recon.py localhost:80"
echo -e "MAILTO=\"\"" | tee -a $out
echo -e "* * * * * root $cmd" | tee -a $out
echo -e "* * * * * root (sleep 15; $cmd)" | tee -a $out
echo -e "* * * * * root (sleep 30; $cmd)" | tee -a $out
echo -e "* * * * * root (sleep 45; $cmd)" | tee -a $out
chmod 0600 $out
