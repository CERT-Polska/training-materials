#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MISP_DB_LOCATION=$DIR/data/$1
BUILD_NAME=enisa2017/$2
#set -x
docker images | grep -q $BUILD_NAME
if [[ $? -eq 0 ]]; then
    echo "Docker Image: $2 already exists"
    echo "Building database ..."
    if [[ -d "$MISP_DB_LOCATION" ]]; then
        docker run -t --rm -v $MISP_DB_LOCATION:/var/lib/mysql $BUILD_NAME chmod -R o+rwX /var/lib/mysql
        rm -rf $MISP_DB_LOCATION
        mkdir -p $MISP_DB_LOCATION
    else
        mkdir -p $MISP_DB_LOCATION
    fi
    
    BACKUP_LOCATION=/tmp/$3

    if [[ -d "$BACKUP_LOCATION" ]]; then
        rm -rf $BACKUP_LOCATION
        mkdir $BACKUP_LOCATION
    fi

    tar -zxpvf "${3}.tar.gz" -C /tmp 
    mv -f $BACKUP_LOCATION/* $MISP_DB_LOCATION
    mv -f $BACKUP_LOCATION/.db_initialized $MISP_DB_LOCATION
    rm -rf $BACKUP_LOCATION

else
    echo "$2 does not exist: run docker-compose pull first!"

fi
