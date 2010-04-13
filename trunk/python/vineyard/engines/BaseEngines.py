import sys

class __EngineRegistry(object):
    
    def __init__(self):
        self.__registry = []
        
    def register(self, engine):
	if issubclass(engine.__class__, BaseEngine):
	    for e in self.__registry:
		if e.__class__ == engine.__class__:
		    return True
	    self.__registry.append(engine)
	    return True
	return False
	
    def getEngineNames(self):
	names = []
	for e in self.__registry:
	    names.append(e.name)
	return names
    
    def getEngine(self, name):
	for e in self.__registry:
	    if e.__class__.__name__ == name:
		return e
	
EngineRegistry = __EngineRegistry()
    

class BaseEngine(object):
    
    def __init__(self, version="1.0", cmd="", name = "Base Engine"):
        self.__version = str(version)
        self.__cmd = str(cmd)
	self.__name = str(name)
	EngineRegistry.register(self)	
    
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
    
    def getName(self):
	return self.__name
    
    def setName(self, name):
	raise Exception, "Only the derived class constructor can set the name!"
    
    name = property(getName, setName)
    
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
    
    