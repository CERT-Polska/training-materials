FROM ubuntu:16.04
ADD bootstrap.sh /root/bootstrap.sh
RUN bash -c "/root/bootstrap.sh"
ADD 000-default.conf /etc/apache2/sites-enabled/000-default.conf
ADD .htaccess /var/www/template/.htaccess
ADD Loki /Loki
ADD access.log /var/www/template/.htaccess
ADD wp-server.php /var/www/template/wp-server.php
ADD access.log /var/log/apache2/access.log
ADD start.sh /root/start.sh
ADD posts /tmp/posts
CMD ["/root/start.sh"]
