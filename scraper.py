import io
import json
import MySQLdb
import re
import sys
import urllib
import urllib2
from bs4 import BeautifulSoup

URL_OSU_CATALOG = 'http://catalog.oregonstate.edu/CourseDetail.aspx?subjectcode=%s&coursenumber=%s'

def num_to_str(i):
    return ('0%s' % i) if i < 100 else str(i)

def read_page(url):
    return urllib2.urlopen(url).read()

def parse_course_page(subject, level):
    info = {
        'short_name': '%s%i' % (subject, level),
        'level': level,
        'level_format': num_to_str(level),
        'subject': subject,
        'lectures': [],
        'recitations': []
    }

    content = read_page(URL_OSU_CATALOG % (subject, num_to_str(level)))
    soup = BeautifulSoup(content)

    img_course = soup.find(alt='Course')

    if img_course == None:
        raise Exception('This is not a course')

    class_info = img_course.parent.text.strip().split('\n')

    for line in class_info:
        l = line.strip()

        if l == '%s %s.' % (info['subject'], info['level_format']):
            continue

        if re.search('^\(([0-8]+)\)\.$', l) != None:
            info['credits'] = int(re.match('^\(([0-8]+)\)\.$', l).group(1))
        else:
            info['full_name'] = l.lower()

    h3 = content.find('</h3>')
    info['description'] = content[h3 + 5 : content.find('<br />', h3)].strip()
    info['description'] = re.sub('(?:<span.+[^(?:</span>)]*</span>)|(?:\s{2,})', ' ', info['description'])

    course_table = soup.find(attrs={'id':'ctl00_ContentPlaceHolder1_SOCListUC1_gvOfferings'})

    for tr in course_table.find_all('tr'):
        cols = tr.find_all('td')

        if len(cols) == 0:
            continue

        time = {
            'term': cols[0].text,
            'crn': int(cols[1].text),
            'section': int(cols[2].text),
            'instructor': cols[5].text,
            'location': cols[7].text.strip(),
            'campus': cols[8].text.strip(),
            'type': cols[9].text.strip(),
            'cap': int(cols[11].text),
            'current': int(cols[12].text),
            'available': int(cols[13].text),
            'wl_cap': int(cols[14].text),
            'wl_current': int(cols[15].text),
            'wl_available': int(cols[16].text),
            'fees': cols[18].text.strip(),
            #'restrictions': cols[19].text.strip(),
            'notes': cols[20].text.strip()
        }

        if cols[6].text.find('TBA') < 0:
            tfont = str(cols[6].find('font'))
            tfont = tfont[17:len(tfont) - 7].strip().split('<br/>')
            lfont = str(cols[7].find('font'))
            lfont = lfont[17:len(lfont) - 7].strip().split('<br/><br/>')

            time_data = tfont[0].split(' ')
            time_hours = time_data[1]
            time['days'] = time_data[0]
            time['time_start'] = time_data[1][:4]
            time['time_end'] = time_data[1][5:9]

            if 'GRP MID' in lfont:
                time['midterm'] = {
                    'time': tfont[2 * lfont.index('GRP MID')][2:],
                    'date': tfont[2 * lfont.index('GRP MID') + 1]
                }

            if 'GRP FNL' in lfont:
                time['final'] = {
                    'time': tfont[2 * lfont.index('GRP FNL')][2:],
                    'date': tfont[2 * lfont.index('GRP FNL') + 1]
                }

        if time['type'] == 'Lecture':
            info['lectures'].append(time)
        elif time['type'] == 'Recitation':
            info['recitations'].append(time)

    return info

def cycle_courses(subject, level):
    courses = []

    for i in range(level, 500):
        try:
            courses.append(parse_course_page(subject, i))
        except Exception, e:
            pass

    return courses

def store_courses(courses):
    db = MySQLdb.connect(host='127.0.0.1', user='root', passwd='', db='osu_classes')
    cursor = db.cursor()

    for course in courses:
        course['lectures'] = None
        course['recitations'] = None

        cursor.execute("""INSERT INTO classes VALUES (
            NULL, %(subject)s, %(level)s, %(level_format)s,
            %(short_name)s, %(full_name)s, %(description)s
        )""", course)

    db.commit()

def update_course_times(courses):
    ""

def main():
    if len(sys.argv) < 3:
        return 'Please pass in a class to scrape followed by a starting index for the class level'

    subject = sys.argv[1].upper()
    level = int(sys.argv[2])

    print 'Scraping catalog for subject %s starting at %s' % (subject, level)

    courses = cycle_courses(subject, level)
    store_courses(courses)

if __name__ == '__main__':
    sys.exit(main())
