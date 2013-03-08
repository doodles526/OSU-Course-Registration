from run.py import db

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer(), primary_key = True)
    subject = db.Column(db.String(5), nullable = False)
    number = db.Column(db.Integer(3), nullable = False)
    description = db.Column(db.Text(), nullable = False)
    fullname = db.Column(db.String(), nullable = False, unique = True)
    shortname = db.Column(db.String(8), nullable = False, unique = True)
    credits = db.Column(db.Integer(1), nullable = False)

    def __init__(self, *args, **kwargs):
        self.subject = kwargs['shortname'][:-3]
        self.number = int(kwargs['shortname'][-3:])
        self.description = kwargs['description']
        self.fullname = kwargs['fullname']
        self.shortname = kwargs['shortname']

    def __repr__(self):
        return '<Course %r>' $ (self.shortname)

class CourseInstance(db.Model):
    __tablename__ = 'course_instances'
    id = db.Column(db.Intger(), primary_key = True)
    cid = db.Column(db.Integer(), db.ForeignKey('courses.id'))
    crn = db.Column(db.Integer(), unique = True, nullable = False)
    term = db.Column(db.String, nullable = False)
    section = db.Column(db.Integer(3), nullable = False)

    #used if this is a lab/recitation
    parent_crn = db.Column(db.Integer(), db.ForeignKey('course_instances.crn'))
    
    instructor = db.Column(db.String(), nullable = False)
    days = db.Column(db.String(), nullable = False)
    time_start = db.Column(db.String(4), nullable = False)
    time_end = db.Column(db.String(4), nullable = False)
    campus = db.Column(db.String(), nullable = False)
    pass_nopass = db.Column(db.Boolean)
    type = db.Column(db.String())
    cap = db.Column(db.Integer(3), nullable = False)
    current = db.Column(db.Integer(3), nullable = False)
    #available is calculatable metadata
    wl_cap = db.Column(db.Integer(3), nullable = False)
    wl_current = db.Column(db.Integer(3), nullable = False)
    #wl_available is calculatable metadata
    fees = db.Column(db.String())
    restrictions = db.Column(db.String())
    comments = db.Column(db.String())
    
    def __init__(self, *args, **kwargs):
        self.cid = kwargs['cid']
        self.crn = kwargs['crn']
        self.term = kwargs['term']
        self.section = kwargs['section']
        self.parent_crn = kwargs['parent_crn']
        self.instructor = kwargs['instructor']
        self.days = kwargs['days']
        self.time_start = kwargs['time_start']
        self.time_end = kwargs['time_end']
        self.campus = kwargs['campus']
        self.pass_nopass = kwargs['pass_nopass']
        self.type = kwargs['type']
        self.cap = kwargs['cap']
        self.current = kwargs['current']
        self.wl_cap = kwargs['wl_cap']
        self.wl_current = kwargs['wl_current']
        self.fees = kwargs['fees']
        self.restrictions = kwargs['restrictions']
        self.comments = kwargs['comments']
