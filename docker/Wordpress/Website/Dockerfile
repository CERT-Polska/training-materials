FROM ubuntu:16.04
ADD bootstrap.sh /root/bootstrap.sh
RUN bash -c "/root/bootstrap.sh"
ADD 000-default.conf /etc/apache2/sites-enabled/000-default.conf
ADD .htaccess /var/www/html/.htaccess
ADD start.sh /root/start.sh
ADD posts /tmp/posts
CMD ["/root/start.sh"]
