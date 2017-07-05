import requests
import logging
import json
from sys import argv
from os import path
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

host = '%s' % argv[1]
filename = path.basename(argv[2])

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
logging.debug("test")

with open('%s' % argv[2], 'r') as data_file:
    data = json.load(data_file)

try:

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
        'data[User][password]': 'admin',
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

    res = requests.get('https://%s/users/change_pw' % host, cookies=cookies, verify=False)
    tmp = res.text.encode('utf-8')

    soup = BeautifulSoup(res.text.encode('utf-8'), "lxml")
    inputTag = soup.findAll(attrs={"name": "data[_Token][key]"})
    key = inputTag[0]['value']
    inputTag = soup.findAll(attrs={"name": "data[_Token][fields]"})
    fields = inputTag[0]['value']

    params = {
        '_method': 'PUT',
        'data[_Token][key]': '%s' % key,
        'data[User][password]': '%s' % argv[3],
        'data[User][confirm_password]': '%s' % argv[3],
        'data[_Token][fields]': '%s' % fields,
        'data[_Token][unlocked]': ''
    }

    res = requests.post('https://%s/users/change_pw' % host, data=params, cookies=cookies, verify=False)
    tmp = res.text.encode('utf-8')

    if len(res.history) > 0:
        cookies = res.history[0].cookies
    else:
        cookies = res.cookies

    logging.debug("changed admin password...")

    res = requests.get('https://%s/events/add_misp_export' % host, cookies=cookies, verify=False)
    tmp = res.text.encode('utf-8')

    logging.debug("got new token fields...")

    soup = BeautifulSoup(res.text.encode('utf-8'), "lxml")
    inputTag = soup.findAll(attrs={"name": "data[_Token][key]"})
    key = inputTag[0]['value']
    inputTag = soup.findAll(attrs={"name": "data[_Token][fields]"})
    fields = inputTag[0]['value']

    files = {'_method': (None, 'POST'),
             'data[_Token][key]': (None, '%s' % key),
             'data[Event][submittedfile]': ('%s' % filename, json.dumps(data), 'application/json'),
             'data[Event][publish]': (None, '0'),
             'data[_Token][fields]': (None, '%s' % fields),
             'data[_Token][unlocked]': (None, '')
    }

    headers = {'Upgrade-Insecure-Requests': '1'}

    res = requests.post('https://%s/events/add_misp_export' % host, cookies=cookies, files=files, headers=headers, verify=False)
    tmp = res.text.encode('utf-8')

    logging.debug("added MISP export...")

    res = requests.get('https://%s/users/logout' % host, cookies=cookies, verify=False)
    tmp = res.text.encode('utf-8')

    logging.debug("logged out...")

except requests.exceptions.Timeout:
    logging.error('Connection timeout!')
except requests.exceptions.ConnectionError as e:
    logging.error('Connection error, reason: %s', str(e))
