#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MISP_DB_LOCATION=$DIR/data/misp-db-wildhamstersec
BUILD_NAME=enisa2017/wildhamstersec-misp

docker images | grep -q $BUILD_NAME
if [[ $? -eq 0 ]]; then
    echo "Docker Image: wildhamstersec-misp already exists"
    echo "Building database ..."
    mkdir $MISP_DB_LOCATION

    BACKUP_LOCATION=/tmp/misp-db-backup-wild

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

