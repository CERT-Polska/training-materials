#!/bin/sh

mkdir -p /data/pcap

if [ -z $1 ]; then
	BUILDDIR=/data/moloch-git
else
	BUILDDIR=$1
fi

echo "git clone"
git clone --branch v0.18.2 --recursive https://github.com/aol/moloch.git $BUILDDIR
echo "cd to dir and build"
cd $BUILDDIR
USEPFRING=no ESMEM="512M" DONOTSTART=yes MOLOCHUSER=daemon GROUPNAME=daemon PASSWORD=0mgMolochDockerRules5 INTERFACE=eth0 BATCHRUN=yes ./easybutton-build.sh
make
make install
cd /data/moloch/viewer
npm install
