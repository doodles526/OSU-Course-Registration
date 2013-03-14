import argparse
import MySQLdb
import re
import sys
import urllib
import urllib2
from bs4 import BeautifulSoup

URL_OSU_CATALOG = 'http://catalog.oregonstate.edu/CourseDetail.aspx?SubjectCode=%s&CourseNumber=%s'

def num_to_str(i):
    return ('0%s' % i) if i < 100 else str(i)

def read_page(url):
    opener = urllib2.build_opener()
    opener.addheaders = [
        ("User-agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.97 Safari/537.11")
    ]

    return opener.open(url, None).read()

def find_all_course_basic():
    URL = 'http://catalog.oregonstate.edu/SOCSearcher.aspx?wks=&chr=abcder'
    content = read_page(URL)
    soup = BeautifulSoup(content)

    all_courses = soup.find(id="ctl00_ContentPlaceHolder1_gvResults")
    all_courses = all_courses.findAll('a', href=True)    
    formated_courses = set()
 ###Need to add a strip to get rid of term token in url   
    for course in all_courses:
        href =  "http://catalog.oregonstate.edu" + course['href']
        term_stripped_href = re.sub(r'&term=\d+', '', href)
        shortname = course.text.split('-')[0].strip().split()[0] + course.text.split('-')[0].strip().split()[1]
        fullname = course.text.split('-')[1].strip().split('[')[0]
        formated_courses.add((shortname, fullname, term_stripped_href))
    
    return formated_courses 

    


def parse_course_page(subject, level, url=None):
    info = {
        'short_name': '%s%i' % (subject, level),
        'level': level,
        'level_format': num_to_str(level),
        'subject': subject,
        'times': []
    }

    if url:
        content = read_page(url)
    else:
        content = read_page(URL_OSU_CATALOG % (subject, num_to_str(level)))
    soup = BeautifulSoup(content)

    if content.find('ctl00_ContentPlaceHolder1_lblError') > -1:
        raise Exception('This is not a course')

    img_course = soup.find(alt='Course')

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
            'available': 0 if cols[13].text.find('WL') > -1 else int(cols[13].text),
            'wl_cap': int(cols[14].text),
            'wl_current': int(cols[15].text),
            'wl_available': int(cols[16].text),
            'fees': cols[18].text.strip(),
            #'restrictions': cols[19].text.strip(),
            'notes': cols[20].text.strip()
        }

        if cols[6].text.find('TBA') < 0:
            time_data = cols[6].prettify()
            #used so we can split on <br/> as with text, the regex will not work for all situations
            raw_location_data = cols[7].prettify()
            meetings = list()
            
            #times = re.findall(r'[a-zA-Z]+\s\d+-\d+/\d+/\d+-\d+/\d+/\d+', time_data)
            #times += re.findall(r'[a-zA-Z]+\s\d+-\d+/\d+/\d+[^-]', time_data)#covers the possibilty of a class being on just one day
            
            #data now split.  will use regex in times loop to strip important details
            times = time_data.split('<br/>')

            for timep1 in times:
                timep2 = times.__iter__().next()
                print timep1
                time_instance = dict()
                time_instance['days'] = re.search(r'\w+', time).group()
                hours = re.findall(r'\d\d\d\d', time)
                
                time_instance['time_start'] = hours[0]
                time_instance['time_end'] = hours[1]
                date = re.sub(r'\w+\s\d+-\d\d\d\d', '', time)
                time_instance['start_date'] = date.split('-')[0]
                if date.split('-')[1]:
                    time_instance['end_date'] = date.split('-')[1]
                meetings.append(time_instance)
            
            split_location_data = raw_location_data.split('<br/>')
            locations = list()
            for location in split_location_data:
                locations.append(re.findall(r'[A-Z]+\s[0-9]+'))

            for i in xrange(len(meetings)):
                meeting[i]['location'] = locations[i]

        else:
            time['days'] = 'TBA'
            time['time_start'] = '0000'
            time['time_end'] = '0000'

        info['times'].append(time)

    return info

def cycle_courses(subject, level, upper):
    courses = []

    for i in range(level, upper):
        try:
            courses.append(parse_course_page(subject, i))
        except Exception, e:
            pass

    return courses

def update_course_times(db, courses, class_id):
    cursor = db.cursor()

    for course in courses:
        course['class_id'] = class_id

        cursor.execute("""SELECT COUNT(*), class_time_id
            FROM class_times
            WHERE class_id = %(class_id)s AND section = %(section)s AND
                crn = %(crn)s AND term = %(term)s
        """, course)

        (rows,id,) = cursor.fetchone()

        if rows == 0:
            course['restrictions'] = ''
            (course['midterm_start'], course['midterm_end'],
                course['final_start'], course['final_end']) = ('0000-00-00 00:00:00', '0000-00-00 00:00:00', 
                '0000-00-00 00:00:00', '0000-00-00 00:00:00')
            cursor.execute("""INSERT INTO class_times VALUES (
                NULL, %(class_id)s, %(term)s, %(crn)s, %(section)s, %(instructor)s,
                %(days)s, %(time_start)s, %(time_end)s, %(campus)s, %(type)s,
                %(cap)s, %(current)s, %(available)s, %(wl_cap)s, %(wl_current)s,
                %(wl_available)s, %(fees)s, %(restrictions)s, %(notes)s,
                %(midterm_start)s, %(midterm_end)s, %(final_start)s, %(final_end)s
            )""", course)
        else:
            course['id'] = id

            cursor.execute("""UPDATE class_times
                SET 
                    instructor = %(instructor)s, days = %(days)s,
                    time_start = %(time_start)s, time_end = %(time_end)s,
                    current = %(current)s, available = %(available)s,
                    wl_cap = %(wl_cap)s, wl_current = %(wl_current)s,
                    wl_available = %(wl_available)s, fees = %(fees)s,
                    notes = %(notes)s
                WHERE class_time_id = %(id)s
            """, course)

def store_courses(db, courses):
    cursor = db.cursor()

    for course in courses:
        course['lectures'] = None
        course['recitations'] = None

        cursor.execute("""SELECT COUNT(*), class_id
            FROM classes
            WHERE subject = %(subject)s AND level = %(level)s
        """, course)

        (rows,id,) = cursor.fetchone()

        if rows == 0:
            cursor.execute("""INSERT INTO classes VALUES (
                NULL, %(subject)s, %(level)s, %(level_format)s,
                %(short_name)s, %(full_name)s, %(description)s
            )""", course)

            cursor.execute("""SELECT class_id
                FROM classes
                WHERE subject = %(subject)s AND level = %(level)s
            """, course)

            (id,) = cursor.fetchone()

        update_course_times(db, course['times'], id)

    db.commit()


def main(args):
    if args.subject is None:
        return 'ERROR: Please specify a subject to index'

    print 'Scraping catalog for subject %s starting at %s' % (args.subject,
                                                              args.startlevel)

    db = MySQLdb.connect(host='127.0.0.1', user='root', passwd='', db='osu_classes')

    courses = cycle_courses(args.subject, args.startlevel, args.endlevel)
    store_courses(db, courses)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-s', '--subject')
    parser.add_argument('-l', '--startlevel', type=int, default=0)
    parser.add_argument('-e', '--endlevel', type=int, default=499)
    args = parser.parse_args()
    sys.exit(main(args))
