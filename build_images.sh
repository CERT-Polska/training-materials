#!/bin/bash

docker build ./docker/Wordpress/Database -t company-db
docker build ./docker/Wordpress/Website -t company-wordpress
docker build ./docker/Malware/DeadlyUrsa -t deadly-ursa
docker build ./docker/moloch -t moloch
docker build ./docker/honeypot -t grumpycatinc-honeypot
docker build ./docker/mailing -t grumpycatinc-mailing
docker build ./docker/intelmq -t intelmq:1.0
docker build ./docker/HIVE/cortex -t cortex:1.0
docker build ./docker/HIVE/hive -t thehive:1.0

(cd ./docker/MISP; ./GrumpyCatIncInit.sh)
(cd ./docker/MISP; ./WildHamsterSecInit.sh)
