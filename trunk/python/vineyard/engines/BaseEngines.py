

class BaseEngine(object):
    
    def __init__(self, version="1.0", cmd=""):
        self.__version = str(version)
        self.__cmd = str(cmd)
    
    def getVersion(self):
        return self.__version
    
    def setVersion(self, version):
        self.__version = str(version)
        
    version = property(getVersion, setVersion)
    
    def getCmd(self):
        return self.__cmd
    
    def setCmd(self, cmd):
        self.__cmd = str(cmd)
    
    command = property(getCmd, setCmd)
    
    def getApp(self):
        return self.__app
    
    def setApp(self, app):
        if issubclass(self.__class__, BaseEngine):
            self.__app = str(app)
        else:
            raise Exception, "Only derived classes can set the application for the engine!"
    
    app = property(getApp, setApp)
    
    def run(self):
        """must be implemented in the derived classes"""
        raise NotImplementedError('must be implemented in the derived classes')
    
    def buildCommand(self, *args):
        """must be implemented in the derived classes"""
        raise NotImplementedError('must be implemented in the derived classes')
    
    def isEnabled(self):
        """must be implemented in the derived classes"""
        raise NotImplementedError('must be implemented in the derived classes')
    
    def kill(self):
        """must be implemented in the derived classes"""
        raise NotImplementedError('must be implemented in the derived classes')
    
    
class RenderEngine(BaseEngine):
    """Base class of all render engines"""
    
    