import sys
try:
    from hashlib import sha1
except ImportError:
    sys.exit('ImportError: no module named hashlib\nIf you are on python2.4 this library is not part of python. Please install it. Example: easy_install hashlib')
    import sha, md5
import os
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Unicode, UnicodeText, Boolean, Float, create_engine
from sqlalchemy.orm import sessionmaker, relation, backref, synonym
import datetime

if os.name == 'nt':
    import win32api
    import win32con
    import win32security
    import win32net
    import win32netcon
    
# this should refer to a centralized database for a large farm, configured at install time
user_path = os.path.expanduser('~')
default_db_dir = user_path + '/DedaFX/Vinyard'
if not os.path.exists(default_db_dir):
    os.makedirs(default_db_dir)
    
engine = create_engine('sqlite:///'+default_db_dir+'/vineyard.db', echo=False)


Session = sessionmaker(bind=engine)

# this is the base class to use for all of our data model objects
BaseObject = declarative_base()

# base metadata
metadata = BaseObject.metadata


# node status definitions
NS_INITIALIZING = 0
NS_OFFLINE = 1
NS_READY = 2
NS_BUSY = 3
NS_PAUSED = 4

# task/job status definitions
TS_QUEUED = 0
TS_BUSY = 1
TS_FAILED = 2
TS_COMPLETED = 3

class Task(BaseObject):
    
    __tablename__ = 'task_table'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    parentJob = Column(Integer)
    name = Column(String)
    engine = Column(String)
    status = Column(String)
    targetPool = Column(String)
    progress = Column(Float)      
    owner = Column(Integer)
    
    submittedTime = Column(DateTime, default=datetime.datetime.now)
    startTime = Column(DateTime)
    completedTime = Column(DateTime)
    
    # how long should a render task remain in the database? <0 means indefinite, 0 means remove when complete, >0 is the number of seconds to keep the task around in the database
    persistance = Column(Integer)
    
    # list of other task ids that need to complete successfully before this can run 
    depends = Column(String)

    # is vital for success of parent job
    vital = Column(Boolean, nullable=False, default=False)
        
    def __repr__(self):
        return "<Task ('%s','%s','%s')>" % (self.name, self.engine, self.progress)
        
# This is the association table for the many-to-many relationship between
# job and tasks - this is, the memberships.
job_tasks_table = Table('job_tasks', metadata,
    Column('job_id', Integer, ForeignKey('job_table.id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('task_id', Integer, ForeignKey('task_table.id',
        onupdate="CASCADE", ondelete="CASCADE"))
)

class Job(BaseObject):

    __tablename__ = 'job_table'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(255), unique=True, nullable=False)
    priority = Column(Integer)
    owner = Column(String)
    
    submitted = Column(DateTime, default=datetime.datetime.now)
    starttime = Column(DateTime)
    finishtime = Column(DateTime)
    
    origin = Column(String)
    progress = Column(String)
    
    status = Column(String)
    tasks = relation('Task', secondary=job_tasks_table, single_parent=True, backref='job', cascade="all, delete, delete-orphan")
    pool = Column(String)
    engine = Column(String)
    
    def __repr__(self):
        return "<Job ('%s','%s')>" % (self.name, self.priority)
    
    def run(self):
        """ run all of the sub-tasks, alert user """
        pass
    

class WorkerNode(BaseObject):
    
    __tablename__ = 'worker_node_table'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(255), unique=True, nullable=False)
    mac_address = Column(String(15), nullable=False)
    ip_address = Column(String(16), unique=True, nullable=False)
    status = Column(String)
    platform = Column(String)
    pools = Column(String)
    version = Column(String)
    cpus = Column(Integer)
    priority = Column(Integer)
    engines = Column(String)
       
    def __repr__(self):
        return "<WorkerNode ('%s')>" % (self.name)
    
    def __unicode__(self):
        return self.name
    
    
class WorkerPool(BaseObject):
    
    __tablename__ = 'worker_pool_table'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(255), unique=True, nullable=False)
    
    def __repr__(self):
        return "<WorkerPool ('%s')>" % (self.name)
    
    def __unicode__(self):
        return self.name
    
        
###################################################################################################################################
##
##    User management data models
##
###################################################################################################################################
      
# This is the association table for the many-to-many relationship between
# groups and permissions.
group_permission_table = Table('group_permission', metadata,
    Column('group_id', Integer, ForeignKey('group_table.group_id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('permission_id', Integer, ForeignKey('permission_table.permission_id',
        onupdate="CASCADE", ondelete="CASCADE"))
)

# This is the association table for the many-to-many relationship between
# groups and members - this is, the memberships.
user_group_table = Table('user_group', metadata,
    Column('user_id', Integer, ForeignKey('user_table.user_id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('group_id', Integer, ForeignKey('group_table.group_id',
        onupdate="CASCADE", ondelete="CASCADE"))
)
        
class User(BaseObject):
    
    __tablename__ = 'user_table'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(Unicode(32), unique=True, nullable=False)
    created = Column(DateTime, default=datetime.datetime.now)
    email_address = Column(Unicode(255), unique=True, nullable=False, info={'rum': {'field':'Email'}})
    display_name = Column(Unicode(255))
    _password = Column('password', Unicode(80), info={'rum': {'field':'Password'}})
    created = Column(DateTime, default=datetime.datetime.now)
    
    def __repr__(self):
        return '<User: email="%s", display name="%s">' % (self.email_address, self.display_name)

    def __unicode__(self):
        return self.display_name or self.user_name
    
    def alert(self):
        """send an alert based on this users preferences for messages"""
        pass
    
        
class Permission(BaseObject):
    
    __tablename__ = 'permission_table'
    
    permission_id = Column(Integer, autoincrement=True, primary_key=True)
    permission_name = Column(Unicode(32), unique=True, nullable=False)
    description = Column(Unicode(255))
    groups = relation('Group', secondary=group_permission_table, backref='permissions')

    def __repr__(self):
        return '<Permission: name=%s>' % self.permission_name
    
    def __unicode__(self):
        return self.permission_name
    
    
class Group(BaseObject):
            
    __tablename__ = 'group_table'

    group_id = Column(Integer, autoincrement=True, primary_key=True)
    group_name = Column(Unicode(16), unique=True, nullable=False)
    display_name = Column(Unicode(255))
    created = Column(DateTime, default=datetime.datetime.now)
    users = relation('User', secondary=user_group_table, backref='groups')
    
    def __repr__(self):
        return '<Group: name=%s>' % self.group_name

    def __unicode__(self):
        return self.group_name

    
######################################################################################################################
##
##    command line usage functions
##
#######################################################################################################################
def usage():
    print """
python models.py
    
    -i, --install install the database to the local machine
    -t --test     perform unit tests, if any
    """
    
def test(args):
    print "No tests defined."
    
def install(args):
    print "installing the database..."
    session = Session()
    metadata.create_all(engine)
    if args == 'WorkerNodes':
        print "\tinstalling WorkerNodes"
        
        _data = [
            [u'joe-renderer',10, '192.168.0.101','00abcdef3321','waiting','win64','','1.0.0','2','1',''],
            [u'bob-renderer',11, '192.168.0.102','00abcdef3322','busy','linux64','','1.0.0','2','1',''],
            [u'sam-renderer',12, '192.168.0.103','00abcdef3323','offline','linux32','','1.0.0','2','1',''],
            [u'joe-renderer2',13, '192.168.0.104','00abcdef3324','busy','win64','','1.0.0','2','1',''],
            [u'bob-renderer2',14, '192.168.0.105','00abcdef3325','offline','linux64','','1.0.0','2','1',''],
            [u'sam-renderer2',15, '192.168.0.106','00abcdef3326','offline','linux32','','1.0.0','2','1',''],
            [u'joe-renderer3',16, '192.168.0.107','00abcdef3327','waiting','win64','','1.0.0','2','1',''],
            [u'bob-renderer3',17, '192.168.0.108','00abcdef3328','busy','linux64','','1.0.0','2','1',''],
            [u'sam-renderer3',18, '192.168.0.109','00abcdef3329','offline','linux32','','1.0.0','2','1',''],
            [u'joe-renderer4',19, '192.168.0.110','00abcdef332a','waiting','win64','','1.0.0','2','1',''],
            [u'bob-renderer4',20, '192.168.0.111','00abcdef332b','waiting','linux64','','1.0.0','2','1',''],
            [u'sam-renderer4',21, '192.168.0.112','00abcdef332c','offline','linux32','','1.0.0','2','1',''],
            [u'joe-renderer5',22, '192.168.0.113','00abcdef332d','waiting','win64','','1.0.0','2','1',''],
            [u'bob-renderer5',23, '192.168.0.114','00abcdef332e','busy','linux64','','1.0.0','2','1',''],
            [u'sam-renderer5',24, '192.168.0.115','00abcdef332f','offline','linux32','','1.0.0','2','1',''],
            [u'joe-renderer6',25, '192.168.0.116','00abcdef3330','waiting','win64','','1.0.0','2','1',''],
            [u'bob-renderer6',26, '192.168.0.117','00abcdef3331','waiting','linux64','','1.0.0','2','1',''],
            [u'sam-renderer6',27, '192.168.0.118','00abcdef3332','offline','linux32','','1.0.0','2','1',''],
                 ]
        
        for n in _data:
            node = WorkerNode(id = n[1],
                              name = n[0],
                              mac_address = n[3],
                              ip_address = n[2],
                              status = n[4],
                              platform = n[5],
                              pools = n[6],
                              version = n[7],
                              cpus = n[8],
                              priority = n[9],
                              engines = n[10] )
            session.add(node)

         
    session.commit()
        
    
if __name__ == '__main__':    
    import getopt, sys
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "t:i:", ["test", "install"])
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(2)
        
    for o,a in opts:
        if o in ('-i', '--install'):
            install(a)
        elif o in ('-t', '--test'):
            test(a)
        else:
            assert False, "unhandled option!"

    #install("WorkerNodes")
    
    
    # create the permissions
    # create default groups
    # create administrator user
    # users can change their password, admin can reset password for user
    # need emergency admin password reset just in case!
