#!/bin/bash

employees=`cat $1`
out="/etc/aliases"
echo -e "\n" | tee -a $out
for e in ${employees[@]}
do
    user=`echo "$e" | cut -d'@' -f1`
    echo -e "$user: | \"/usr/bin/procmail -m /opt/procmail/procmailrc $user\"" | tee -a $out
done
