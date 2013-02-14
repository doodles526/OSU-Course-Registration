import json
import sys
import urllib
import urllib2
from cookielib import CookieJar

URL_ONLINE_SERVICES_LOGIN = "https://adminfo.ucsadm.oregonstate.edu/prod/twbkwbis.P_WWWLogin"
URL_ONLINE_SERVICES_LOGIN_ACTION = "https://adminfo.ucsadm.oregonstate.edu/prod/twbkwbis.P_ValLogin"
URL_ONLINE_SERVICES_REGISTER_ACTION = "https://adminfo.ucsadm.oregonstate.edu/prod/bwckcoms.P_Regs"
URL_ONLINE_SERVICES_SELECT_TERM_ACTION = "https://adminfo.ucsadm.oregonstate.edu/prod/bwskfreg.P_AltPin"

def login(config, cookies):
    headers = [
        # required; login form page
        ("Referer", URL_ONLINE_SERVICES_LOGIN),
        # not required; not really needed. just used to mask this program's python user agent
        ("User-agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.97 Safari/537.11"),
        # required; this shows it is sending form data
        ("Content-type", "application/x-www-form-urlencoded"),
        # required; this is how the system checks if you have cookies enabled.
        ("Cookie", "TESTID=set")
    ]

    data_enc = urllib.urlencode({'sid': config['credentials']['username'], 'PIN': config['credentials']['password']})
    response = post_data(URL_ONLINE_SERVICES_LOGIN_ACTION, data_enc, headers, cookies)

def select_term(config, cookies):
    """"""

def register(config, cookies):
    headers = [
        # required; login form page
        ("Referer", "https://adminfo.ucsadm.oregonstate.edu/prod/twbkwbis.P_WWWLogin"),
        # not required; not really needed. just used to mask this program's python user agent
        ("User-agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.97 Safari/537.11"),
        # required; this shows it is sending form data
        ("Content-type", "application/x-www-form-urlencoded")
    ]

    crns = []

    for crn in config['course_crns']:
        # I believe this specifies that it is a new course to register for, rather than "drop" or "re-register"
        #  --> I figured it out, it stands for Register Web
        crns.append("CSTS_IN=RW")
        
        # The course registration number for the course
        crns.append("CRN_IN=" + str(crn))

        # Term to register for. I believe format is: #year#quarternumber
        #     Where quarternumber is relative (starting at 1 for Fall) to the current quarter
        crns.append("assoc_term_in=" + str(config['term_in'])) 

        # Blank for who knows why. This really is not a well built system :\
        crns.append("start_date_in=")

        # Blank for who knows why. This really is not a well built system :\
        crns.append("end_date_in=")

    # Join all the elements into the query string.
    crns_enc = '&'.join(crns)
    print crns_enc

    response = post_data(URL_ONLINE_SERVICES_REGISTER_ACTION, crns_enc, headers, cookies)

    with open('output.html', 'w') as f:
        f.write(response.read())

def post_data(url, data, headers, cookies):
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))
    opener.addheaders = headers

    return opener.open(url, data)

def main(config):
    if len(config['credentials']['username']) == 0:
        raise Exception('username field in config.json is blank')
    elif len(config['credentials']['password']) == 0:
        raise Exception('password field in config.json is blank')
    
    cookies = CookieJar()

    print 'login'
    login(config, cookies)
    print 'register'
    register(config, cookies)

if __name__ == '__main__':
    try:
        with open('config.json') as f:
            config = json.loads(f.read())

        main(config)
    except urllib2.HTTPError, e:
        if e.code == 404:
            print "Page not found? Weird..."
        elif e.code == 403:
            print "Forbidden access to website. Check cookies are still intact: Referer, Content-type, Cookie"
        elif e.code in [500, 503, 504]:
            print "Website error. Probably too much traffic. (code: " + str(e.code) + ")"
        else:
            print e
    except Exception, e:
        raise e
