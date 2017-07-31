import requests
import logging
import json
from sys import argv
from os import path, listdir
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

RELOGIN_AFTER = 4
logging.basicConfig(format='%(levelname)s | %(message)s', level=logging.DEBUG)

if len(argv) < 4:
    logging.debug("Usage: python BatchLoadDataToMISP.py <MISP hostname> <Events directory> <Admin password>")
    exit()

host = '%s' % argv[1]
event_files = []

for filename in listdir(argv[2]):
    if filename.endswith(".json") or filename.endswith(".xml"):
        event_files.append(path.join(argv[2], filename))

try:
    i = 0

    for f in event_files:

        if i % RELOGIN_AFTER == 0:

            res = requests.get('https://%s/users/login' % host, verify=False)
            cookies = res.cookies

            logging.debug("got cookie and token fields...")

            soup = BeautifulSoup(res.text.encode('utf-8'), "lxml")
            inputTag = soup.findAll(attrs={"name": "data[_Token][key]"})
            key = inputTag[0]['value']
            inputTag = soup.findAll(attrs={"name": "data[_Token][fields]"})
            fields = inputTag[0]['value']

            params = {
                '_method': 'POST',
                'data[_Token][key]': '%s' % key,
                'data[User][email]': 'admin@admin.test',
                'data[User][password]': '%s' % argv[3],
                'data[_Token][fields]': '%s' % fields,
                'data[_Token][unlocked]': ''
            }

            res = requests.post('https://%s/users/login' % host, data=params, cookies=cookies, verify=False)
            tmp = res.text.encode('utf-8')

            if len(res.history) > 0:
                cookies = res.history[0].cookies
            else:
                cookies = res.cookies

            logging.debug("logged in...")


        filename = path.basename(f)

        if filename.endswith('.json'):
            with open('%s' % f, 'r') as data_file:
                data = json.load(data_file)

            submittedFile = json.dumps(data)
            contentType = 'application/json'
        else:
            with open('%s' % f, 'r') as data_file:
                submittedFile = data_file.read()

            contentType = 'application/xml'

        res = requests.get('https://%s/events/add_misp_export' % host, cookies=cookies, verify=False)
        tmp = res.text.encode('utf-8')

        if len(res.history) > 0:
            cookies = res.history[0].cookies

        logging.debug("got new token fields...")

        soup = BeautifulSoup(res.text.encode('utf-8'), "lxml")
        inputTag = soup.findAll(attrs={"name": "data[_Token][key]"})
        key = inputTag[0]['value']
        inputTag = soup.findAll(attrs={"name": "data[_Token][fields]"})
        fields = inputTag[0]['value']

        files = {'_method': (None, 'POST'),
                 'data[_Token][key]': (None, '%s' % key),
                 'data[Event][submittedfile]': ('%s' % filename, submittedFile, contentType),
                 'data[Event][publish]': (None, '0'),
                 'data[_Token][fields]': (None, '%s' % fields),
                 'data[_Token][unlocked]': (None, '')
        }

        headers = {'Upgrade-Insecure-Requests': '1', 'Connection': 'close', 'Referer': 'https://%s/events/add_misp_export' % host}

        res = requests.post('https://%s/events/add_misp_export' % host, cookies=cookies, files=files, headers=headers, verify=False)
        tmp = res.text.encode('utf-8')

        if len(res.history) > 0:
            cookies = res.history[0].cookies

        i = i + 1
        logging.debug("added MISP export...(%s of %s)" % (i, len(event_files)))

        if i % RELOGIN_AFTER == 0:
            res = requests.get('https://%s/users/logout' % host, cookies=cookies, verify=False)
            tmp = res.text.encode('utf-8')

            logging.debug("logged out...")



    logging.debug("Total added MISP export file(s): %s" % len(event_files))

except requests.exceptions.Timeout:
    logging.error('Connection timeout!')
except requests.exceptions.ConnectionError as e:
    logging.error('Connection error, reason: %s', str(e))
