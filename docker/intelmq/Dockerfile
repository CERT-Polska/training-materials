FROM ubuntu:16.04

USER root

RUN apt-get update -y && \
    apt-get upgrade -y
RUN	apt-get install -y python3-pip python3-dnspython python3-psutil python3-redis python3-requests python3-termstyle python3-tz apt-utils git apache2 php libapache2-mod-php7.0
RUN apt-get install -y sudo build-essential libcurl4-gnutls-dev libgnutls28-dev python3-dev
RUN apt-get install -y nano vim

RUN git clone https://github.com/certtools/intelmq.git /tmp/intelmq
WORKDIR /tmp/intelmq
RUN git checkout tags/1.0.0.rc1

RUN pip3 install .
RUN pip3 install elasticsearch

RUN cp /opt/intelmq/etc/examples/harmonization.conf /opt/intelmq/etc/
#RUN cp /opt/intelmq/etc/examples/BOTS /opt/intelmq/etc/
#COPY config/* /opt/intelmq/etc/

RUN useradd -d /opt/intelmq -U -s /bin/bash intelmq && \
    chmod -R 0777 /opt/intelmq && \
    chown -R intelmq:intelmq /opt/intelmq


RUN git clone https://github.com/certtools/intelmq-manager.git /tmp/intelmq-manager
RUN cp -R /tmp/intelmq-manager/intelmq-manager/* /var/www/html/
RUN chown -R www-data:www-data /var/www/html/
RUN usermod -a -G intelmq www-data
RUN chgrp www-data /opt/intelmq/etc/*.conf
RUN chmod g+w /opt/intelmq/etc/*.conf
RUN echo "www-data ALL=(intelmq) NOPASSWD: /usr/local/bin/intelmqctl" >> /etc/sudoers
RUN mkdir /tmp/honeypot
ENV APACHE_PID_FILE=/var/run/apache2/apache2.pid
COPY ./run.sh /

WORKDIR /opt/intelmq

#USER intelmq
RUN chmod +x /run.sh
CMD ["/run.sh"]

#CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]
