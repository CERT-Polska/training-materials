#!/bin/bash

docker cp $1 enisa2017_moloch_1:/traffic.pcap
docker exec enisa2017_moloch_1 /data/moloch/bin/moloch-capture -r /traffic.pcap -t traffic
