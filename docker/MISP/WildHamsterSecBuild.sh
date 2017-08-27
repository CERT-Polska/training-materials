#!/bin/bash

MISP_DB_LOCATION=/tmp/misp-db-wildhamstersec
BUILD_NAME=wildhamstersec-misp

if [[ -d "$MISP_DB_LOCATION" ]]; then
	rm -rf $MISP_DB_LOCATION
fi

docker pull harvarditsecurity/misp:latest
docker build -t $BUILD_NAME WildHamsterSec
docker run -it --rm -v $MISP_DB_LOCATION:/var/lib/mysql $BUILD_NAME /init-db
docker run --name wildhamstersec-misp -it -d -v $MISP_DB_LOCATION:/var/lib/mysql --net enisanet --ip 10.34.1.13 $BUILD_NAME

sleep 5

#load data
/usr/bin/python ./LoadDataToMISP.py wildhamstersec.enisa.ex ./EventData/WildHamsterSec/events.json 'WHSec.123!@#'
