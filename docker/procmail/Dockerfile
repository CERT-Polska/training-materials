FROM tozd/postfix:latest

RUN apt-get update -y && apt-get upgrade -y && apt-get autoremove -y

RUN apt-get install procmail

RUN mkdir /var/mail/examples

RUN chmod 777 /var/mail/examples

RUN mkdir /var/mail/phishings

RUN chmod 777 /var/mail/phishings
