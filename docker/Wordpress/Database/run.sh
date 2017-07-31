#!/bin/sh

docker build . -t company-db
docker run --name company-db -e MYSQL_ROOT_PASSWORD=902rsdnhiv23qre -e MYSQL_DATABASE=wordpress --net enisanet --ip 10.34.1.2 company-db

