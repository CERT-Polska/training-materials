#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MISP_DB_LOCATION=$DIR/data/misp-db-grumpycatinc
BUILD_NAME=enisa2017/grumpycatinc-misp

docker images | grep -q $BUILD_NAME
if [[ $? -eq 0 ]]; then
    echo "Docker Image: grumpycatinc-misp already exists"
    echo "Building database ..."
    docker run -it --rm -v $MISP_DB_LOCATION:/var/lib/mysql $BUILD_NAME /init-db
else
    echo "Grumpycatinc-misp not exist: run docker-compose pull first!"

fi
