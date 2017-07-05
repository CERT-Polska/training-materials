#!/bin/bash

MISP_DB_LOCATION=/tmp/misp-db-myorg
BUILD_NAME=my_org_misp

if [[ -d "$MISP_DB_LOCATION" ]]; then
	rm -rf $MISP_DB_LOCATION
fi

docker build -t $BUILD_NAME MyOrg
docker run -it --rm -v $MISP_DB_LOCATION:/var/lib/mysql $BUILD_NAME /init-db
docker run --name my-org-misp -it -d -p 10443:443 -p 10080:80 -p 10306:3306 -p 10666:6666 -v $MISP_DB_LOCATION:/var/lib/mysql $BUILD_NAME
