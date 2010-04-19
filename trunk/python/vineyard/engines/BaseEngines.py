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
	
    def getEngineNames(self, enabled_only=False):
	names = []
	for e in self.__registry:
	    if enabled_only:
		if e.isEnabled():
		    names.append(e.name)
	    else:
		names.append(e.name)
	return names
    
    def getEngineByName(self, nme):
	for e in self.__registry:
	    if e.name == nme:
		return e
    
    def getEngine(self, name):
	for e in self.__registry:
	    if e.__class__.__name__ == name:
		return e
	    
    def getRegistry(self):
	return self.__registry
    
    def getLocalEngineDef(self, engine_name):
	eng = self.getEngineByName(engine_name)
	if eng:
	    if os.path.exists("plugins"):
		for plugin in os.listdir("./plugins"):
		    if plugin[-2:].lower() == 'py':
			fn = os.path.join(os.path.abspath("./plugins"), plugin)
			#exec(open(fn, 'r'))
			if fn == eng.filename:
			    return fn
	
EngineRegistry = __EngineRegistry()
    

class BaseEngine(object):
    
    # empty command dictionary
    _cmdFormat = []
    
    def __init__(self, version="1.0", cmd="", name = "Base Engine", filename=None):
        self.__version = str(version)
        self.__cmd = str(cmd)
	self.__name = str(name)
	self.__filename == filename
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
    
    def getFilename(self):
        return self.__filename
    
    def setFilename(self, fname):
        self.__filename = str(fname)
    
    filename = property(getFilename, setFilename)
    
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
    
    def getCmdFormat(self):
	return self._cmdFormat
    
    def setCmdFormat(self, cmdFormat):
	if issubclass(self.__class__, BaseEngine):
            self._cmdFormat = str(cmdFormat)
        else:
            raise Exception, "Only derived classes can set the command dictionary for the engine!"
	
    commandFormat = property(getCmdFormat, setCmdFormat)
    
    def run(self):
        """must be implemented in the derived classes"""
        raise NotImplementedError('must be implemented in the derived classes')
    
    def buildCommandFromDict(self, cmdDict={}):
	"""cmdDict: only the arguments for the command, not including the main executable"""
	execstr = "self.buildCommand("
	n = 0
	for arg in cmdDict:
	    execstr += str(arg) + "=" + str(cmdDict[arg]) 
	    n += 1
	    if n < len(cmdDict):
		execstr += ','
	execstr += ")"
	exec(execstr)
	
    
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
    
    