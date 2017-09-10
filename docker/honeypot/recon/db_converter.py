import csv
import sqlite3
import logging
import re

from logging.handlers import RotatingFileHandler
from random import randint

logger = logging.getLogger('service_recon')
logger.setLevel(logging.DEBUG)
rfh = RotatingFileHandler('/var/log/service_recon/db_converter.log', maxBytes=1024*1024,  backupCount=10)
rfh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s | %(levelname)-5s | %(message)s')
rfh.setFormatter(formatter)
logger.addHandler(rfh)

logger.debug("Connecting to db...")
conn=sqlite3.connect('/opt/myhoneypot/db/glastopf.db')
c=conn.cursor()

logger.debug("Connected...")

data = c.execute("SELECT * FROM events")
rows = data.fetchall()

logger.debug("Writing output file, rows: %s..." % len(rows))

with open('/opt/shared/output.csv', 'w') as f:

    writer = csv.writer(f)
    header = []

    for c in data.description:
        header.append(c[0])

    writer.writerow(header)

    for r in rows:

        ip = r[2].split(":")[0]

        attack = randint(0, 100)
        if attack < 25:
            dork = "/vp-json/wp/v2/posts/5/?id=3abc"
            ip = '10.34.1.7'
            req = re.sub('POST.+', 'POST %s HTTP/1.1' % dork, r[4])
            tmp = dork[1:]
            writer.writerow((r[0], r[1], ip, dork, req, dork[1:], r[6]))
        elif attack > 75:
            dork = "/vp-json/wp/v2/posts/"
            ip = '10.34.1.7'
            req = re.sub('POST.+', 'POST %s HTTP/1.1' % dork, r[4])
            tmp = dork[1:]
            writer.writerow((r[0], r[1], ip, dork, req, dork[1:], r[6]))
        else:
            writer.writerow((r[0], r[1], ip, r[3], r[4], r[5], r[6]))

    #writer.writerows(rows)

logger.debug("Successfully wrote output file.")
conn.close()