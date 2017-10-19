FROM ubuntu:16.04
COPY ./sshd_config /etc/ssh/sshd_config
ADD bootstrap.sh /root/bootstrap.sh
RUN bash -c "/root/bootstrap.sh"
ADD 000-default.conf /etc/apache2/sites-enabled/000-default.conf
ADD template /var/www/template
ADD Loki /Loki
ADD access.log /var/log/apache2/access.log
ADD start.sh /root/start.sh
ADD posts /etc/posts
CMD /usr/sbin/sshd && /root/start.sh
