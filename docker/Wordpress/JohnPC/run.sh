#!/bin/sh

docker build . -t john-pc
docker run --name john-pc --net enisanet --ip 10.34.1.8 --add-host company-wordpress.enisa.ex:10.34.1.3 john-pc
