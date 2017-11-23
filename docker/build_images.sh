#!/bin/bash

docker build ./Wordpress/Database -t enisa2017/database
docker build ./Wordpress/Website -t enisa2017/wordpress
docker build ./Malware/DeadlyUrsa -t enisa2017/deadly-ursa
docker build ./moloch -t enisa2017/moloch
docker build ./honeypot -t enisa2017/grumpycatinc-honeypot
docker build ./mailing -t enisa2017/grumpycatinc-mailing
docker build ./intelmq -t enisa2017/intelmq:1.1
docker build ./HIVE/cortex -t enisa2017/cortex:1.0
docker build ./HIVE/hive -t enisa2017/thehive:1.0

