FROM enisa2017/cortex:latest
USER root

RUN pip2 install elasticsearch
RUN pip3 install cortexutils

COPY hosts /hosts
RUN cat /hosts >> /etc/hosts

