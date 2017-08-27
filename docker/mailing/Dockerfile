FROM tozd/postfix:latest

RUN apt-get update -y 
#&& apt-get upgrade -y && apt-get autoremove -y

#procmail
RUN apt-get install procmail nano
RUN mkdir /opt/procmail
COPY ./procmail/ /opt/procmail
RUN chmod +x /opt/procmail/filter.sh
RUN mkdir /opt/extras
COPY ./extras/ /opt/extras
RUN mkdir /var/log/procmail
RUN chmod 777 /var/log/procmail

#create mail directories
RUN chmod 777 /var/mail

RUN mkdir /var/mail/inspect
RUN chmod 777 /var/mail/inspect

RUN mkdir /var/mail/employees
RUN chmod 777 /var/mail/employees
COPY ./mailboxes /var/mail/employees
RUN chown -R nobody:mail /var/mail/employees/*
RUN find /var/mail/employees/* -type d -exec chmod 700 {} +
RUN find /var/mail/employees/* -type d -exec chmod g+s {} +
RUN find /var/mail/employees/* -type f -exec chmod 600 {} +

#additional postfix configuration
ENV MAILNAME mailing.enisa.ex
ENV ROOT_ALIAS /var/mail/root
COPY ./service/postfix/run.config /etc/service/postfix
RUN chmod +x /etc/service/postfix/run.config

#install mailgenerator script
RUN mkdir /var/log/mailgenerator
RUN mkdir /opt/mailgenerator
COPY ./mailgenerator/ /opt/mailgenerator

#maintenance scripts
WORKDIR /tmp
COPY ./maint-scripts .
RUN chmod +x *.sh

#generate mail aliases
RUN /bin/bash -c "./GenerateAliases.sh /opt/mailgenerator/data/employees"
RUN postalias /etc/aliases

#install cron job for mail generator
RUN /bin/bash -c "./InstallCronJob.sh"

RUN rm /tmp/*

RUN mkdir /etc/service/cron
RUN chmod 755 /etc/service/cron
COPY ./service/cron/ /etc/service/cron
RUN chmod +x /etc/service/cron/run

WORKDIR /opt/procmail
