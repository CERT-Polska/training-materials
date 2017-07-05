FROM harvarditsecurity/misp:latest
WORKDIR /var/www/MISP/app/Config
COPY ./config.php .
RUN chmod 750 config.php
RUN chown www-data:www-data config.php
