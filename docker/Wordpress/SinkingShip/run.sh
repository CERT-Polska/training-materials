#!/bin/sh

docker build . -t sinking-ship
docker run --name sinking-ship --net enisanet --ip 10.34.1.5 sinking-ship
