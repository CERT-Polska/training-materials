#!/bin/bash

BUILD_NAME=my_org_mailing

docker build -t $BUILD_NAME .
docker run --name my-org-mailing --hostname myorg.enisa.ex -it -d -p 12025:25 -p 12465:465 -p 12587:587 $BUILD_NAME
#-v /tmp/honeypot_files:/tmp $BUILD_NAME
