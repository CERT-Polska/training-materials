#!/bin/bash

BUILD_NAME=my_org_honeypot
SHARED_VOLUME=/tmp/honeypot_files

if [[ ! -d "SHARED_VOLUME" ]]; then
	mkdir $SHARED_VOLUME
	chmod 777 $SHARED_VOLUME
fi

docker build -t $BUILD_NAME .
docker run --name my-org-honeypot --hostname hunter -d -i -p 18080:80 -v $SHARED_VOLUME:/opt/shared $BUILD_NAME

