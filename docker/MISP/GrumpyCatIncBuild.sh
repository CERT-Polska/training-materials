#!/bin/bash

MISP_DB_LOCATION=/tmp/misp-db-grumpycatinc
BUILD_NAME=grumpycatinc-misp

if [[ -d "$MISP_DB_LOCATION" ]]; then
	rm -rf $MISP_DB_LOCATION
fi

docker pull harvarditsecurity/misp:latest
docker build -t $BUILD_NAME GrumpyCatInc
docker run -it --rm -v $MISP_DB_LOCATION:/var/lib/mysql $BUILD_NAME /init-db
docker run --name grumpycatinc-misp -it -d -v $MISP_DB_LOCATION:/var/lib/mysql --net enisanet --ip 10.34.1.12 --add-host wildhamstersec.enisa.ex:10.34.1.13 $BUILD_NAME
