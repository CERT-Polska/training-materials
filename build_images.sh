#!/bin/sh

docker build ./docker/Wordpress/Database -t company-db
docker build ./docker/Wordpress/JohnPC -t john-pc
docker build ./docker/Wordpress/SinkingShip -t sinking-ship
docker build ./docker/Wordpress/Website -t company-wordpress
docker build ./docker/Wordpress/WebsiteExploit -t fancy-bear
docker build ./docker/Malware/DeadlyUrsa -t deadly-ursa
docker build ./docker/moloch -t moloch


