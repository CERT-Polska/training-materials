#!/bin/bash

docker build ./docker/Wordpress/Database -t enisa2017/company-db
docker build ./docker/Wordpress/Website -t enisa2017/company-wordpress
docker build ./docker/Malware/DeadlyUrsa -t enisa2017/deadly-ursa
docker build ./docker/moloch -t enisa2017/moloch
docker build ./docker/honeypot -t enisa2017/grumpycatinc-honeypot
docker build ./docker/mailing -t enisa2017/grumpycatinc-mailing
docker build ./docker/intelmq -t enisa2017/intelmq:1.1
docker build ./docker/HIVE/cortex -t enisa2017/cortex:1.0
docker build ./docker/HIVE/hive -t enisa2017/thehive:1.0

(cd ./docker/MISP; ./GrumpyCatIncInit.sh)
(cd ./docker/MISP; ./WildHamsterSecInit.sh)
