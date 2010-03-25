
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Unicode, UnicodeText, Boolean, Float, create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///:memory:', echo=True)
Session = sessionmaker(bind=engine)

# this is the base class to use for all of our data model objects
BaseObject = declarative_base()

class RenderTask(BaseObject):
    
    __tablename__ = 'render_task_table'
    
    id = Column(Integer, primary_key=True)
    parentJob = Column(Integer)
    name = Column(String)
    engine = Column(String)
    status = Column(String)
    targetPool = Column(String)
    progress = Column(Float)      
    owner = Column(Integer)
    
    submittedTime = Column(DateTime)
    startTime = Column(DateTime)
    completedTime = Column(DateTime)
    
    # how long should a render task remain in the database? <0 means indefinite, 0 means remove when complete, >0 is the number of seconds to keep the task around in the database
    persistance = Column(Integer)
        
    def __init__(self):
        self.parentJob = 0
        self.name = ""
        self.engine = ""
        
        self.status = ""
        self.targetPool = ""
        self.progress = ""      
        self.owner = ""
        self.submittedTime = ""
        self.startTime = ""
        self.completedTime = ""
        self.persistance = 0
        
    def __repr__(self):
        return "<RenderTask ('%s','%s','%s')>" % (self.name, self.engine, self.progress)
        
        
class RenderJob(BaseObject):

    __tablename__ = 'render_job_table'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    priority = Column(Integer)
    
    def __init__(self):
        self.name = ""
        self.priority = 0
        
        self.tasks = []
        
    def __repr__(self):
        return "<RenderJob ('%s','%s')>" % (self.name, self.priority)
    
        
class WorkerNode(BaseObject):
    
    __tablename__ = 'worker_node_table'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    def __init__(self, name):
        self.name = str(name)
    
    def __repr__(self):
        return "<WorkerNode ('%s')>" % (self.name)
    
    
class WorkerPool(BaseObject):
    
    __tablename__ = 'worker_pool_table'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    def __init__(self, name):
        self.name = str(name)
    
    def __repr__(self):
        return "<WorkerPool ('%s')>" % (self.name)
    
        
###################################################################################################################################
##
##    User management data models
##
###################################################################################################################################
        
        
class User(BaseObject):
    
    __tablename__ = 'user_table'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    def __init__(self):
        self.name = ""
        self.password = ""
        self.groups = []
        
    def __repr__(self):
        return "<User ('%s')>" % (self.name)
    
        
class Permission(BaseObject):
    
    __tablename__ = 'permission_table'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    def __init__(self):
        self.name = 'administrator'
    
    def __repr__(self):
        return "<Permission ('%s')>" % (self.name)
    
    
class Group(BaseObject):
            
    __tablename__ = 'group_table'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    def __init__(self):
        self.name = 'administrator_group'
    
    def __repr__(self):
        return "<Group ('%s')>" % (self.name)
        
        
if __name__ == '__main__':    
    session = Session()
