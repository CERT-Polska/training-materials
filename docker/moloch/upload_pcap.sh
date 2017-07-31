#!/bin/bash

docker cp $1 moloch:/traffic.pcap
docker exec moloch /data/moloch/bin/moloch-capture -r /traffic.pcap -t traffic
