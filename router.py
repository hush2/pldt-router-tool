import requests
from requests.exceptions import ConnectionError, Timeout
from collections import OrderedDict
from bs4 import BeautifulSoup
import sys

# Router defaults, set real value in gui.
ip = '192.168.1.1'
username = 'admin'
password = '1234'

data = {}


class RouterException(Exception):
    pass


def login():
    try:
        resp = requests.get('http://' + ip, timeout=2)
        if '/login.htm' not in resp.text:
            raise RouterException('Router not supported')
    except requests.exceptions.ConnectTimeout:
        raise RouterException('Connection timed out.')

    # Form data should be in order or else router will reject it
    login_data = OrderedDict()

    login_data['username'] = username
    login_data['password'] = password
    login_data['submit.htm?login.htm'] = 'Send'  # required

    resp = requests.post('http://' + ip + '/login.cgi', data=login_data, timeout=2)
    if 'username or password error' in resp.text.lower():
        raise RouterException('Wrong username or password.')


def fetch_info(loc):
    resp = requests.get('http://' + ip + '/index.', timeout=2)
    if '/login.htm' in resp.text:
        login()  # Not logged-in
    resp = requests.get('http://' + ip + loc, timeout=2)
    if '/login.htm' in resp.text:
        raise RouterException('Router not supported')
    parse_table(resp.text)


def fetch_data():
    try:
        fetch_info('/status.htm')
        fetch_info('/adslconfig.htm')
    except (ConnectionError, Timeout):
        raise RouterException('Connection error.')

    # Return only relevant items
    od = OrderedDict()
    # pprint(data)
    od['Name'] = data.get('Alias Name', '-')
    od['Line Staus'] = data.get('ADSL Line Status', '-')
    od['Mode'] = data.get('ADSL Mode', '-')
    od['Uptime'] = data.get('DSL Up Time', '-')
    od['Download Speed'] = data.get('Downstream Speed', '-')
    od['Upload Speed'] = data.get('Upstream Speed', '-')

    return od


def parse_table(html):
    soup = BeautifulSoup(html, 'html.parser')
    for tr in soup.find_all('tr'):
        th = tr.find('th')
        td = tr.find('td')
        if th and td:
            data[th.text.strip()] = td.text.strip()


if __name__ == '__main__':
    from pprint import pprint

    try:
        pprint(fetch_data())
    except Exception as e:
        print(e)
