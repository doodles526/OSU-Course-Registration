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
