import csv
import sqlite3
import logging
import re

from logging.handlers import RotatingFileHandler
from random import randint


def generate_ip():
    result = randint(1,254)
    for i in range(0,3):
        result = "%s.%s" % (result, randint(0,255))
    return result


def get_last_fetched_id():
    with open('/opt/recon/last_fetched', 'r') as f:
        return f.read()


def set_last_fetched_id(id):
    with open('/opt/recon/last_fetched', 'w') as f:
        f.write("%s" % id)
        f.close()


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

last_fetched_id = get_last_fetched_id()

data = c.execute("SELECT * FROM events WHERE id > %s" % last_fetched_id)
rows = data.fetchall()

logger.debug("Writing output file, rows: %s..." % len(rows))

with open('/opt/shared/hp_output.csv', 'w') as f:

    writer = csv.writer(f)

    if len(rows) > 0:
        header = []

        for c in data.description:
            header.append(c[0])

        writer.writerow(header)

    last = 0

    for r in rows:

        ip = r[2].split(":")[0]
        last = r[0]

        attack = randint(0, 100)
        if attack < 15:
            inject = "/wp-json/wp/v2/posts/5/?id=3abc"
            ip = '58.218.199.147'
            req = re.sub('POST.+', 'POST %s HTTP/1.1' % inject, r[4])
            writer.writerow((r[0], r[1], ip, inject, req, inject[1:], r[6]))
        elif attack > 85:
            inject = "/wp-json/wp/v2/posts/"
            ip = '58.218.199.147'
            req = re.sub('POST.+', 'POST %s HTTP/1.1' % inject, r[4])
            writer.writerow((r[0], r[1], ip, inject, req, inject[1:], r[6]))
        elif 15 < attack < 25:
            inject = "option=com_contenthistory&view=history&list[select]=SELECT%20name%20FROM%20jml_users"
            ip = '58.218.199.147'
            req = "POST /index.php?option=com_contenthistory&view=history&list[select]=SELECT%20name%20FROM%20jml_users HTTP/1.1\n" \
                  "Accept: */*Accept-Encoding: gzip, deflate, compress\nContent-Length: 87\n" \
                  "Host: 58.218.199.147\nReferer: http://58.218.199.147:80\nUser-Agent: Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US)\n\n" \
                  "option=com_contenthistory&view=history&list[select]=SELECT%20name%20FROM%20jml_users"
            writer.writerow((r[0], r[1], ip, inject, req, inject, r[6]))
        elif 75 < attack < 85:
            inject = "action=invokeOpByName&name=jboss.deployer:service=BSHDeployer&methodName=createScriptDeployment&argType=java.lang.String&arg0=ls&argType=java.lang.String&arg1=fj189dse.bsh"
            ip = '58.218.199.147'
            req = "POST /jmx-console/HtmlAdaptor\n" \
                  "Accept: */*Accept-Encoding: gzip, deflate, compress\nContent-Length: 87\nContent-Type: application/x-www-form-urlencoded\n" \
                  "Host: 58.218.199.147\nReferer: http://58.218.199.147:80\nUser-Agent: Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US)\n\n" \
                  "action=invokeOpByName&name=jboss.deployer:service=BSHDeployer&methodName=createScriptDeployment&argType=java.lang.String&arg0=ls&argType=java.lang.String&arg1=fj189dse.bsh"
            writer.writerow((r[0], r[1], ip, inject, req, inject, r[6]))
        else:
            ip = generate_ip()
            writer.writerow((r[0], r[1], ip, r[3], r[4], r[5], r[6]))

    if last > 0:
        set_last_fetched_id(last)
    #writer.writerows(rows)

logger.debug("Successfully wrote output file.")
conn.close()
