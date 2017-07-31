#!/bin/sh

docker build . -t company-wordpress
docker run --name company-wordpress --link company-db:mysql --net enisanet --ip 10.34.1.3 company-wordpress
