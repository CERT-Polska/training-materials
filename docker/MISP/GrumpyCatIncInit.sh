#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MISP_DB_LOCATION=$DIR/data/misp-db-grumpycatinc
BUILD_NAME=grumpycatinc-misp

docker images | grep -q $BUILD_NAME
if [[ $? -eq 0 ]]; then
    echo "Docker Image: grumpycatinc-misp already exists"
else
    docker pull harvarditsecurity/misp:latest
    docker build -t $BUILD_NAME GrumpyCatInc
fi


if [[ -d "$MISP_DB_LOCATION" ]]; then
    echo "GrumpyCatInc database already exists @ $MISP_DB_LOCATION"
    echo "Exitting..."
else
    docker run -it --rm -v $MISP_DB_LOCATION:/var/lib/mysql $BUILD_NAME /init-db
fi

