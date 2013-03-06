import argparse
import requests
import sys
from bs4 import BeautifulSoup as bs

URL_ONLINE_SERVICES = 'https://adminfo.ucsadm.oregonstate.edu/prod/'


def get_title(content):
    soup = bs(content)
    return soup.title.text


def bruteforce_pin(session):
    for i in range(0, 1000000):
        pin = str(i).rjust(6, '0')

        if session.try_pin(pin):
            print 'Got the PIN!'
            return True
        else:
            print 'PIN %s failed. Let\'s go again!' % pin
    else:
        print 'Never figured out PIN...'
        return False


class Course:
    def __init__(self, details=None):
        if details is None:
            return

        for k, v in details.items():
            if k in ['dropped', 'registered', 'waitlisted']:
                continue

            details[k] = v.strip()

        self.status = details['status']
        self.crn = int(details['crn'])
        self.subject = details['subject']
        self.section = details['section']
        self.credits = float(details['credits'])
        self.title = details['title']
        self.dropped = details['dropped']
        self.registered = details['registered']
        self.waitlisted = details['waitlisted']

    @staticmethod
    def get_waitlisted_courses(session):
        waitlisted = []
        courses = Course.get_all_courses(session)

        for course in courses:
            if course.waitlisted:
                waitlisted.append(course)

        return waitlisted

    @staticmethod
    def get_dropped_courses(session):
        dropped = []
        courses = Course.get_all_courses(session)

        for course in courses:
            if course.dropped:
                dropped.append(course)

        return dropped

    @staticmethod
    def get_current_courses(session):
        registered = []
        courses = Course.get_all_courses(session)

        for course in courses:
            if course.registered:
                registered.append(course)

        return registered

    @staticmethod
    def get_all_courses(session):
        session.set_referer(URL_ONLINE_SERVICES + 'bwcklibs.P_StoreTerm')
        url = URL_ONLINE_SERVICES + 'bwskfreg.P_AltPin'
        res = session.get(url)
        soup = bs(res.content)

        if soup.title.text != 'Add/Drop Classes: ':
            return []

        courses = []

        course_table = soup.find('table', {'class': 'datadisplaytable'})
        for tr in course_table.find_all('tr'):
            cols = tr.find_all('td')

            if len(cols) == 0:
                continue

            course = Course({'status': cols[0].text, 'crn': cols[2].text,
                             'subject': cols[3].text, 'section': cols[5].text,
                             'credits': cols[7].text, 'title': cols[9].text,
                             'dropped': cols[0].text.find('Drop') > -1,
                             'registered': cols[0].text.find('Registered') > -1,
                             'waitlisted': cols[0].text.find('Registered') > -1})

            courses.append(course)

        return courses


class Session:
    def __init__(self):
        self.req = requests.Session()
        self.req.headers = {'Accept': ('text/html,application/xhtml+xml,applic'
                                       'ation/xml;q=0.9,*/*;q=0.8'),
                            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64'
                                           ') AppleWebKit/537.22 (KHTML, like '
                                           'Gecko) Chrome/25.0.1364.97 Safari/'
                                           '537.22'),
                            'DNT': '1', 'Accept-Encoding': 'gzip,deflate,sdch',
                            'Accept-Language': 'en-US,en;q=0.8',
                            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3'}

    def get_session(self):
        return req

    def set_referer(self, referer):
        self.req.headers['Referer'] = referer

    def login(self, username, password):
        self.set_referer(URL_ONLINE_SERVICES + 'twbkwbis.P_WWWLogin')
        url = URL_ONLINE_SERVICES + 'twbkwbis.P_ValLogin'
        self.req.get(url)
        res = self.req.post(url, {'sid': username, 'PIN': password})

        return res.content.find('WELCOME') > 0 or get_title(res.content)

    def pin_required(self):
        self.set_referer(URL_ONLINE_SERVICES + 'bwcklibs.P_StoreTerm')
        url = URL_ONLINE_SERVICES + 'bwskfreg.P_AltPin'
        res = self.req.get(url)

        return get_title(res.content) == 'Registration PIN Verification'

    def switch_term(self, term):
        self.set_referer(URL_ONLINE_SERVICES + 'bwskflib.P_SelDefTerm')
        url = URL_ONLINE_SERVICES + 'bwcklibs.P_StoreTerm'
        res = self.req.post(url, {'term_in': term})
        soup = bs(res.content)

    def try_pin(self, pin):
        self.set_referer(URL_ONLINE_SERVICES + 'bwskfreg.P_AltPin')
        url = URL_ONLINE_SERVICES + 'bwskfreg.P_CheckAltPin'
        res = self.req.post(url, {'pin': pin})

        if get_title(res.content) != 'Registration PIN Verification':
            return True
        elif res.content.find('getaltpinc NOTFOUND') > -1:
            return False


def main(args):
    session = Session()

    if not session.login(args.username, args.password):
        return 'ERROR: Could not validate your login credentials'

    session.switch_term('201303')

    if session.pin_required():
        if not args.pin is None:
            if not session.try_pin(args.pin):
                return 'ERROR: Provided invalid registration pin'
        elif args.bruteforce:
            if not bruteforce_pin(session):
                return 'ERROR: Pin could not be retrieved'
        else:
            return 'ERROR: Pin is required or you must enable --bruteforce'


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('-u', '--username')
    arg_parser.add_argument('-p', '--password')
    arg_parser.add_argument('-b', '--bruteforce')
    arg_parser.add_argument('-n', '--pin')
    arg_parser.add_argument('-c', '--crns')
    args = arg_parser.parse_args()
    sys.exit(main(args))
