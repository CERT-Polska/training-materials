#!/bin/sh
MOLOCHDIR=/data/moloch

chmod a+rwx /data/moloch/raw /data/moloch/logs /data/moloch/data /data/pcap

wget --no-check-certificate https://cert.pl/enisa2017/traffic.pcap -P /data/pcap

echo "Giving ES time to start..."
sleep 3
until curl -sS 'http://10.34.1.20:9200/_cluster/health?wait_for_status=yellow&timeout=5s'
do
    echo "Waiting for ES to start"
    sleep 1
done
#echo

# intialize moloch
echo INIT | /data/moloch/db/db.pl http://10.34.1.20:9200 init
/data/moloch/bin/moloch_add_user.sh admin "Admin User" MOLOCH --admin
/data/moloch/bin/moloch_update_geo.sh

echo "Starting reading PCAP: /data/pcap/traffic.pcap"

/data/moloch/bin/moloch-capture -r /data/pcap/traffic.pcap
