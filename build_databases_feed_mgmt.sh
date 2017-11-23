#!/bin/bash

(cd ./docker/MISP; ./WildHamsterSecInit.sh)
(cd ./docker/MISP; ./GrumpyCatIncInit.sh)

docker-compose -f docker/moloch/docker-compose.yml up -d
sleep 10
MOLOCH=$(docker ps -q -f name=moloch)
while [[ -n $MOLOCH ]]; do
    MOLOCH=$(docker ps -q -f name=moloch)
    echo "Filling elasticsearch Moloch pcap, this can take long time ..."
    sleep 1
done

echo "================================================"
echo "Filling ES with intelmq hp data"
./docker/intelmq/push_hp_data_2_es.sh
sleep 2

docker-compose -f docker/moloch/docker-compose.yml down
