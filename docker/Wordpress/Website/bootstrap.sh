#!/bin/bash

apt-get update && apt-get install -y curl php7.0 less sudo mysql-client php7.0-mysql apache2 libapache2-mod-php python-pip vim
pip install yara-python psutil netaddr pylzma colorama

unzip Loki.zip

curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
chmod +x wp-cli.phar
mv wp-cli.phar /usr/local/bin/wp

a2enmod rewrite

mkdir /var/www/html -p
chown www-data:www-data /var/www/html

