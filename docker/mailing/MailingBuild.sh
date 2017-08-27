#!/bin/bash

BUILD_NAME=grumpycatinc-mailing

docker pull tozd/postfix
docker build -t $BUILD_NAME .
docker run --name grumpycatinc-mailing --hostname mailing.enisa.ex -it -d --net enisanet --ip 10.34.1.18 $BUILD_NAME
