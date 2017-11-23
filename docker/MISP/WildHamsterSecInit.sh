#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MISP_DB_LOCATION=$DIR/data/misp-db-wildhamstersec
BUILD_NAME=enisa2017/wildhamstersec-misp
BACKUP_LOCATION=/tmp/misp-db-backup-wild

docker images | grep -q $BUILD_NAME
if [[ $? -eq 0 ]]; then
    echo "Docker Image: wildhamstersec-misp already exists"
    echo "Building database ..."
    if [[ -d "$MISP_DB_LOCATION" ]]; then
        docker run -t --rm -v $MISP_DB_LOCATION:/var/lib/mysql $BUILD_NAME chmod -R o+rwX /var/lib/mysql
        rm -rf $MISP_DB_LOCATION
        mkdir -p $MISP_DB_LOCATION
    else
        mkdir -p $MISP_DB_LOCATION
    fi

    if [[ -d "BACKUP_LOCATION" ]]; then
        rm -rf $BACKUP_LOCATION
        mkdir $BACKUP_LOCATION
    fi

    tar -zxpvf "misp-db-backup-wild-1st-day.tar.gz" -C /tmp 
    mv $BACKUP_LOCATION/* $MISP_DB_LOCATION
    mv $BACKUP_LOCATION/.db_initialized $MISP_DB_LOCATION
    rm -rf $BACKUP_LOCATION

else
    echo "wildhamstersec-misp not exist: run docker-compose pull first!"
fi

