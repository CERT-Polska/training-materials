from random import randint
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from os import listdir
from os.path import *
from smtplib import *
from time import sleep

import logging
from logging.handlers import RotatingFileHandler

CAMPAIGN_THRESHOLD = 93
ATTACHMENT_THRESHOLD = 75
SEND_THRESHOLD = 30

logger = logging.getLogger('mailgenerator')
logger.setLevel(logging.DEBUG)
rfh = RotatingFileHandler('/var/log/mailgenerator/mailgen.log', maxBytes=1024*1024,  backupCount=10)
rfh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s | %(levelname)-5s | %(message)s')
rfh.setFormatter(formatter)
logger.addHandler(rfh)

send = randint(0, 100)

if send < SEND_THRESHOLD:
    logger.info("Mail send threshold not exceeded, leaving...")
    exit()

sleep(randint(0,10))

MAIN_DIR = abspath(dirname(__file__))
DATA_DIR = join(MAIN_DIR, 'data')
ATTACHMENTS_DIR = join(MAIN_DIR, 'attachments')

malicious_attachment = 'Invoice_no_89685958466.pdf.exe'
campaign_email = False

with open(join(DATA_DIR, 'campaign_from'), 'r') as fp:
    campaign_from = [line[:-1] for line in fp]

with open(join(DATA_DIR, 'campaign_subjects'), 'r') as fp:
    campaign_subjects = [line[:-1] for line in fp]

with open(join(DATA_DIR, 'campaign_contents'), 'r') as fp:
    campaign_contents = []
    tmp = []

    for c in fp:
        if not c.startswith('----'):
            tmp.append(c[:-1])
            continue

        campaign_contents.append('\n'.join(tmp))
        tmp = []

with open(join(DATA_DIR, 'employees'), 'r') as fp:
    employees = [line[:-1] for line in fp]

with open(join(DATA_DIR, 'subjects'), 'r') as fp:
    subjects = [line[:-1] for line in fp]

with open(join(DATA_DIR, 'contents'), 'r') as fp:
    contents = []
    tmp = []

    for c in fp:
        if not c.startswith('----'):
            tmp.append(c[:-1])
            continue

        contents.append('\n'.join(tmp))
        tmp = []

attachments = []
for filename in listdir("%s" % ATTACHMENTS_DIR):
    if malicious_attachment in filename:
        continue

    attachments.append(filename)

logger.debug("Loaded data from files.")

campaign = randint(0, 100)
if campaign > CAMPAIGN_THRESHOLD:
    campaign_email = True

if not campaign_email:

    c = contents[randint(0, len(contents) - 1)]
    f = employees[randint(0, len(employees) - 1)]
    t = employees[randint(0, len(employees) - 1)]
    s = subjects[randint(0, len(subjects) - 1)]
    attachment = randint(0, 100)
    if attachment > ATTACHMENT_THRESHOLD:
        a = attachments[randint(0, len(attachments) - 1)]
    else:
        a = None

    if a is not None:
        logger.debug("Standard mail with attachment.")
        msg = MIMEMultipart()
        msg.attach(MIMEText(c))

        fn, ext = splitext(join(ATTACHMENTS_DIR, a))

        if '.zip' in ext:
            part = MIMEBase('application', 'zip')
            part.set_payload(open(join(ATTACHMENTS_DIR, a), "rb").read())
            encoders.encode_base64(part)

        elif '.pdf' in ext:
            part = MIMEApplication(open(join(ATTACHMENTS_DIR, a), "rb").read(), _subtype="pdf")

        elif '.xls' in ext:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(open(join(ATTACHMENTS_DIR, a), "rb").read())
            encoders.encode_base64(part)

        elif '.jpg' in ext:
            part = MIMEImage(open(join(ATTACHMENTS_DIR, a), 'rb').read(), name='%s' % a)

        elif '.exe' in ext or '.scr' in ext:
            part = MIMEBase('application', 'exe')
            part.set_payload(open(join(ATTACHMENTS_DIR, a), "rb").read())
            encoders.encode_base64(part)

        elif '.pif' in ext:
            part = MIMEBase('application', 'x-msdownload')
            part.set_payload(open(join(ATTACHMENTS_DIR, a), "rb").read())
            encoders.encode_base64(part)

        part.add_header('Content-Disposition', 'attachment', filename='%s' % a)
        msg.attach(part)

    else:
        logger.debug("Standard mail with no attachment.")
        msg = MIMEText(c)

    msg['Subject'] = '%s' % s
    msg['From'] = '%s' % f
    msg['To'] = '%s' % t

else:
    logger.debug("Campaign email.")
    c = campaign_contents[randint(0, len(campaign_contents) - 1)]
    f = campaign_from[randint(0, len(campaign_from) - 1)]
    t = employees[randint(0, len(employees) - 1)]
    s = campaign_subjects[randint(0, len(campaign_subjects) - 1)]

    msg = MIMEMultipart()
    msg.attach(MIMEText(c))
    msg['Subject'] = '%s' % s
    msg['From'] = '%s' % f
    msg['To'] = '%s' % t

    part = MIMEBase('application', 'exe')
    part.set_payload(open(join(ATTACHMENTS_DIR, malicious_attachment), "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename='%s' % malicious_attachment)
    msg.attach(part)

#print '%s' % msg.as_string()

try:
    logger.debug("Sending email")
    smtpObj = SMTP("localhost")
    smtpObj.sendmail(msg['From'], msg['To'], msg.as_string())
    smtpObj.close()
    logger.debug("Email successfully sent")

except SMTPException as e:
    logger.error("Exception while sending email, reason: %s" % str(e))
