FROM honeynet/glastopf

RUN apt-get update -y 
#&& apt-get upgrade -y && apt-get autoremove -y

RUN apt-get install -y sqlite nano runit openssh-server

COPY ./glastopf.cfg /opt/myhoneypot
COPY ./sshd_config /etc/ssh/sshd_config

RUN mkdir /var/log/service_recon
RUN chmod 777 /var/log/service_recon

RUN mkdir /opt/shared

#copy recon script
RUN mkdir -p /opt/recon/injection_codes
COPY ./recon/injection_codes /opt/recon/injection_codes
COPY ./recon/service_recon.py /opt/recon
COPY ./recon/db_converter.py /opt/recon
COPY ./recon/last_fetched /opt/recon

#install cron job for mail generator
WORKDIR /tmp
COPY ./InstallCronJob.sh .
RUN chmod +x InstallCronJob.sh
RUN /bin/bash -c "./InstallCronJob.sh"
RUN rm InstallCronJob.sh

WORKDIR /opt/myhoneypot

RUN mkdir /var/run/sshd
RUN chmod 0755 /var/run/sshd
RUN echo "root:Password826" | chpasswd

CMD /usr/sbin/cron && /usr/sbin/sshd && glastopf-runner
