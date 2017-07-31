FROM tozd/postfix:latest

RUN apt-get update -y && apt-get upgrade -y && apt-get autoremove -y

#procmail
RUN apt-get install procmail nano
RUN mkdir /opt/procmail
COPY ./examples/ /opt/procmail
RUN mkdir /opt/procmail/solutions
COPY ./solutions/ /opt/procmail/solutions
RUN mkdir /var/log/procmail
RUN chmod 777 /var/log/procmail

#create mail directories
RUN chmod 777 /var/mail

RUN mkdir /var/mail/examples
RUN chmod 777 /var/mail/examples

RUN mkdir /var/mail/inspect
RUN chmod 777 /var/mail/inspect

RUN mkdir /var/mail/employees
RUN mkdir /var/mail/employees_old
RUN chmod 777 /var/mail/employees
COPY ./mailboxes /var/mail/employees_old
RUN chown -R nobody:mail /var/mail/employees_old/*
#RUN find /var/mail/employees/* -type d -exec chmod 755 {} +
#RUN find /var/mail/employees/* -type d -exec chmod g+s {} +

#additional postfix configuration
ENV MAILNAME myorg.enisa.ex
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

#RUN /bin/bash -c "./GenerateMailboxes.sh"

#generate mail aliases
#COPY ./GenerateAliases.sh .
#RUN chmod +x GenerateAliases.sh
RUN /bin/bash -c "./GenerateAliases.sh /opt/mailgenerator/data/employees"
RUN postalias /etc/aliases
#RUN rm GenerateAliases.sh

#install cron job for mail generator
#COPY ./InstallCronJob.sh .
#RUN chmod +x InstallCronJob.sh
RUN /bin/bash -c "./InstallCronJob.sh"
#RUN rm InstallCronJob.sh

#RUN rm /tmp/*

RUN mkdir /etc/service/cron
RUN chmod 755 /etc/service/cron
COPY ./service/cron/ /etc/service/cron
RUN chmod +x /etc/service/cron/run

WORKDIR /opt/procmail

