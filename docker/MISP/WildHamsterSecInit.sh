#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MISP_DB_LOCATION=$DIR/data/misp-db-wildhamstersec
BUILD_NAME=wildhamstersec-misp

docker images | grep -q $BUILD_NAME
if [[ $? -eq 0 ]]; then
    echo "Docker Image: wildhamstersec-misp already exists"
else
    docker pull harvarditsecurity/misp:latest
    docker build -t $BUILD_NAME WildHamsterSec
fi


if [[ -d "$MISP_DB_LOCATION" ]]; then
    echo "WildHamsterSec database already exists @ $MISP_DB_LOCATION"
    echo "Exitting..."
else
    docker run -it --rm -v $MISP_DB_LOCATION:/var/lib/mysql $BUILD_NAME /init-db
fi

