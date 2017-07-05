#!/bin/sh

MOLOCHDIR=/data/moloch

# set PATH
echo "PATH=\"/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/data/moloch/bin\"" > /etc/environment

source /etc/profile

# set write permissions for moloch
chmod a+rwx /data/moloch/raw /data/moloch/logs /data/moloch/data

# wait for Elasticsearch
echo "Giving ES time to start..."
sleep 5
until curl -sS 'http://elasticsearch:9200/_cluster/health?wait_for_status=yellow&timeout=5s'
do
    echo "Waiting for ES to start"
    sleep 1
done
echo

# intialize moloch
echo INIT | /data/moloch/db/db.pl http://elasticsearch:9200 init
/data/moloch/bin/moloch_add_user.sh admin "Admin User" MOLOCH --admin
/data/moloch/bin/moloch_update_geo.sh

# capture
if [ -z $1 ]; then
	echo "Not starting capture, start capturing with giving 'capture' parameter"
  #start with amqp reader
else
	echo "Starting capture on default interface. Change /data/moloch/etc/config.ini"
	nohup /data/moloch/bin/moloch-capture
fi

echo
echo "How to import pcap?"
echo " - docker run -d --name moloch -v /path/to/host/dir/with/pcap:/data/pcap:rw danielguerra/moloch"
echo " - docker exec moloch /data/moloch/bin/moloch-capture -r /data/pcap/sniff.pcap -t mysniff --copy"
echo
echo "PLEASE ignore error about mising log file. It's standard moloch start script"
echo "Starting viewer. Go with https to port 8005 of container."
cd /data/moloch/viewer
node viewer.js