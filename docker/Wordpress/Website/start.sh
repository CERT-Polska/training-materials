#!/bin/bash

cd /var/www/html
if [ ! -f .initialized ]; then
    mkdir /var/www/html -p
    chown www-data:www-data /var/www/html
    cp -r /var/www/template/* /var/www/html/
    cp -r /var/www/template/.* /var/www/html/

    until sudo -u www-data wp core config --dbname=wordpress --dbuser=root --dbpass=902rsdnhiv23qre --dbhost=company-db.enisa.ex --extra-php="define( 'AUTOMATIC_UPDATER_DISABLED', true );"
    do
        sleep 5
    done
    sudo -u www-data wp core install --url=http://company-wordpress.enisa.ex --title=WordPress --admin_user=admin --admin_password=123 --admin_email=admin@example.com
    sudo -u www-data wp rewrite structure '/%year%/%monthnum%/%postname%'

    chown www-data:www-data /etc/posts -R
    chown www-data:www-data /var/www/html -R
    find /etc/posts -type f | xargs -i,, bash -c 'sudo -u www-data wp post create ,, --post_status=publish --post_title="$(head -n 1 ,,)"'

    rm /var/www/html/index.html
    touch .initialized
fi

service apache2 stop
sleep 0.1
service apache2 stop
apache2ctl -DFOREGROUND
