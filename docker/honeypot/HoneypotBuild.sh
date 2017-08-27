#!/bin/bash

BUILD_NAME=grumpycatinc-honeypot
SHARED_VOLUME=/tmp/honeypot_files

if [[ ! -d "SHARED_VOLUME" ]]; then
	mkdir $SHARED_VOLUME
	chmod 777 $SHARED_VOLUME
fi

docker pull honeynet/glastopf
docker build -t $BUILD_NAME .
docker run --name grumpycatinc-honeypot --hostname hunter.enisa.ex -d -i -v $SHARED_VOLUME:/opt/shared --net enisanet --ip 10.34.1.19 $BUILD_NAME

