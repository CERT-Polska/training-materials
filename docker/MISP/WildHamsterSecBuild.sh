#!/bin/bash

MISP_DB_LOCATION=/tmp/misp-db-wildhamstersec
BUILD_NAME=wildhamstersec_misp

if [[ -d "$MISP_DB_LOCATION" ]]; then
	rm -rf $MISP_DB_LOCATION
fi

docker pull harvarditsecurity/misp:latest
docker build -t $BUILD_NAME WildHamsterSec
docker run -it --rm -v $MISP_DB_LOCATION:/var/lib/mysql $BUILD_NAME /init-db
docker run --name wildhamstersec-misp -it -d -p 20443:443 -p 20080:80 -p 20306:3306 -p 20666:6666 -v $MISP_DB_LOCATION:/var/lib/mysql $BUILD_NAME

sleep 5

#load data
/usr/bin/python ./LoadDataToMISP.py wildhamstersec.enisa.ex:20443 ./EventData/WildHamsterSec/events.json 'WHSec.123!@#'
