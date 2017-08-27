#!/bin/bash

cd /var/www/html
if [ ! -f .initialized ]; then
    sudo -u www-data wp core config --dbname=wordpress --dbuser=root --dbpass=902rsdnhiv23qre --dbhost=mysql
    sudo -u www-data wp core install --url=http://company-wordpress.enisa.ex --title=WordPress --admin_user=admin --admin_password=123 --admin_email=admin@example.com
    sudo -u www-data wp rewrite structure '/%year%/%monthnum%/%postname%'

    chown www-data:www-data /tmp/posts -R
    find /tmp/posts -type f | xargs -i,, bash -c 'sudo -u www-data wp post create ,, --post_status=publish --post_title="$(head -n 1 ,,)"'
    rm /tmp/posts -rf

    rm /var/www/html/index.html
    touch .initialized
fi
apache2ctl -DFOREGROUND
