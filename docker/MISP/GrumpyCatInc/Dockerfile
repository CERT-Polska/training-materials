FROM harvarditsecurity/misp:latest

RUN apt-get update -y && apt-get upgrade -y && apt-get autoremove -y

RUN apt-get install -y vim nano
RUN sed -i -- 's/Require all granted/AllowOverride all/g' /etc/apache2/sites-available/default-ssl.conf

WORKDIR /etc/ssl/private
COPY ./certs/misp.crt .
COPY ./certs/misp.key .

WORKDIR /var/www/MISP/app/webroot/img
COPY ./misp-logo.png .
RUN chmod 750 misp-logo.png
RUN chown www-data:www-data misp-logo.png

WORKDIR /var/www/MISP/app/Config
COPY ./config.php .
RUN chmod 750 config.php
RUN chown www-data:www-data config.php
