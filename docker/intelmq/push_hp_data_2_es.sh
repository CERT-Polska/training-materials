#!/bin/bash

echo ""
echo "Uploading honeypot intelmq data..."
curl -v -XPOST '10.34.1.20:9200/_bulk' --data-binary @docker/intelmq/events_from_hp.txt -o /dev/null
