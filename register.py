import argparse
import requests
import sys
from bs4 import BeautifulSoup as bs

req = requests.Session()
req.headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.97 Safari/537.22', 'DNT': '1', 'Accept-Encoding': 'gzip,deflate,sdch', 'Accept-Language': 'en-US,en;q=0.8', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3'}

URL_ONLINE_SERVICES = 'https://adminfo.ucsadm.oregonstate.edu/prod/'


def login(username, password):
    req.headers['Referer'] = URL_ONLINE_SERVICES + 'twbkwbis.P_WWWLogin'
    url = URL_ONLINE_SERVICES + 'twbkwbis.P_ValLogin'
    req.get(url)
    res = req.post(url, {'sid': username, 'PIN': password})

    return res.content.find('WELCOME') > 0 or bs(res.content).title.text


def pin_required():
    req.headers['Referer'] = URL_ONLINE_SERVICES + 'bwcklibs.P_StoreTerm'
    url = URL_ONLINE_SERVICES + 'bwskfreg.P_AltPin'
    res = req.get(url)
    title = bs(res.content).title.text

    return title == 'Registration PIN Verification'


def switch_term(term):
    req.headers['Referer'] = URL_ONLINE_SERVICES + 'bwskflib.P_SelDefTerm'
    url = URL_ONLINE_SERVICES + 'bwcklibs.P_StoreTerm'
    res = req.post(url, {'term_in': term})
    soup = bs(res.content)


def main(args):
    if not login(args.username, args.password):
        return 'ERROR: Could not validate your login credentials'

    switch_term('201303')

    if pin_required():
        return 'ERROR: Pin is required to be entered'


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('-u', '--username')
    arg_parser.add_argument('-p', '--password')
    arg_parser.add_argument('-c', '--crns')
    args = arg_parser.parse_args()
    sys.exit(main(args))
