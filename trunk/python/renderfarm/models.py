
class RenderTask(object):
    
    def __init__(self):
        self.parentJob = None
        self.name = ""
        self.engine = ""
        
        self.status = ""
        self.targetPool = ""
        self.progress = ""      
        self.owner = ""
        self.submittedTime = ""
        self.startTime = ""
        self.completedTime = ""
        
        
class RenderJob(object):

    def __init__(self):
        self.name = ""
        self._id = 0
        self.priority = 0
        
        self.tasks = []
        
        
class User(object):
    
    def __init__(self):
        self.username = ""
        self.password = ""
        self.groups = []
        
        
        