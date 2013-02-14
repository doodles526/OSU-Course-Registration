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
        'subject': subject
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

    lectures = []
    recitations = []

    for tr in course_table.find_all('tr'):
        cols = tr.find_all('td')

        if len(cols) == 0:
            continue

        time = {}
        time['term'] = cols[0].text
        time['crn'] = int(cols[1].text)
        time['section'] = int(cols[2].text)
        time['instructor'] = cols[5].text

        if cols[6].text.find('TBA') < 0:
            time_data = cols[6].text.strip().split(' ')
            time_hours = time_data[1][:4]
            time['days'] = time_data[0]
            time['time_start'] = time_data[1][:4]
            time['time_end'] = time_data[1][5:9]
        
        time['location'] = cols[7].text.strip()
        time['campus'] = cols[8].text.strip()
        time['type'] = cols[9].text.strip()

        time['cap'] = int(cols[11].text)
        time['current'] = int(cols[12].text)
        time['available'] = int(cols[13].text)
        time['wl_cap'] = int(cols[14].text)
        time['wl_current'] = int(cols[15].text)
        time['wl_available'] = int(cols[16].text)
        time['fees'] = cols[18].text.strip()
        #time['restrictions'] = cols[19].text.strip()
        time['notes'] = cols[20].text.strip()

        if cols[9].text == 'Lecture':
            lectures.append(time)
        elif cols[9].text == 'Recitation':
            recitations.append(time)

    print lectures

    return info

def cycle_courses(subject, level):
    for i in range(level, 500):
        try:
            parse_course_page(subject, i)
        except Exception, e:
            pass

def main():
    if len(sys.argv) < 3:
        return 'Please pass in a class to scrape followed by a starting index for the class level'

    subject = sys.argv[1].upper()
    level = int(sys.argv[2])

    print 'Scraping catalog for subject %s starting at %s' % (subject, level)
    print parse_course_page(subject, level)

    #cycle_courses(subject, level)

if __name__ == '__main__':
    sys.exit(main())
