import requests
import logging

from sys import argv
from logging.handlers import RotatingFileHandler
from random import randint
from os.path import *
from time import sleep

SCANNING_THRESHOLD = 0
host = '%s' % argv[1]

logger = logging.getLogger('service_recon')
logger.setLevel(logging.DEBUG)
rfh = RotatingFileHandler('/var/log/service_recon/recon.log', maxBytes=1024*1024,  backupCount=10)
rfh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s | %(levelname)-5s | %(message)s')
rfh.setFormatter(formatter)
logger.addHandler(rfh)

scan = randint(0, 100)

if scan < SCANNING_THRESHOLD:
    logger.info("Scanning threshold not exceeded, leaving...")
    exit()

sleep(randint(0,5))

MAIN_DIR = abspath(dirname(__file__))
DATA_DIR = join(MAIN_DIR, 'dorks')

# load dorks
with open(join(DATA_DIR, 'comment'), 'r') as fp:
    comments = [line[:-1] for line in fp]

with open(join(DATA_DIR, 'login'), 'r') as fp:
    logins = [line[:-1] for line in fp]

with open(join(DATA_DIR, 'password'), 'r') as fp:
    passwords = [line[:-1] for line in fp]

headers = {'Referer': 'http://%s' % host}

datatype = randint(0, 1)
if datatype > 0:            #login/password form
    login = logins[randint(0, len(logins) - 1)]
    password = passwords[randint(0, len(passwords) - 1)]
    logger.debug("Chose %s / %s" % (login, password))

    params = {
        'login': '%s' % login,
        'password': '%s' % password,
        'submit': 'Submit',
    }

    res = requests.post('http://%s/index' % host, data=params, headers=headers)
    tmp = res.text.encode('utf-8')

    logger.debug("Successfully sent creds request - response code %s." % res.status_code)
    exit()

#comment form
comment = comments[randint(0, len(comments) - 1)]
logger.debug("Chose %s" % comment)

params = {
    'comment': '%s' % comment,
    'submit': 'Submit',
}

res = requests.post('http://%s/comments' % host, data=params, headers=headers)
tmp = res.text.encode('utf-8')

logger.debug("Successfully sent comment request - response code %s." % res.status_code)