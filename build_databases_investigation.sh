#!/bin/bash

(cd ./docker/MISP; ./RestoreMISPDb.sh "misp-db-grumpycatinc" "grumpycatinc-misp" "misp-db-backup-grumpy")
(cd ./docker/MISP; ./RestoreMISPDb.sh "misp-db-wildhamstersec" "wildhamstersec-misp" "misp-db-backup-wild")
