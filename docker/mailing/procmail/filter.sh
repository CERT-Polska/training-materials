#!/bin/bash

employees=`cat employees`
mboxes_dir=$1
script=$2

for e in ${employees[@]}
do

	echo -e "$e"
	messages=$mboxes_dir/$e/new/*

	for f in $messages
	do
		echo "    $f"
		`cat $f | /usr/bin/procmail -m $script $e`
	done
done
