#!/bin/bash
#set -e
for ((i=1; i<=60; i+=1))
do
	nc -w 1 -z elasticsearch5.enisa.ex 9200
	if [[ $? -eq 0 ]]
	then
		echo "Uploading data..."
		curl -S -s -XPOST 'elasticsearch5.enisa.ex:9200/_bulk' --data-binary @events_from_hp.txt -o /dev/null
		if [[ $? -eq 0 ]]
		then
			echo "Data uploaded successfully"
		else
			echo "Error, restart Elasticsearch"
		fi
		exit
	fi
	sleep 1
	echo "Waiting for Elasticsearch. Trying...${i} of 60"
	if [[ ${i} -eq 60 ]]
	then
		echo "!!! ERROR !!!"
		echo "Elasticsearch not running"
	fi
done

