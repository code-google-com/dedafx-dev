import sys
from vineyard import FarmConfig

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
		try:
		    if e.isEnabled():
			names.append(e.name)
		except: pass
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
	"""This function won't work properly when run as a windows service"""
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
    
    """This is the base engine class for all processing engines.
    
    To implement, derive a class from this class or a sub-class and override the buildCommand function. Most sub-classes will need to create their own isEnabled function that checks for the presence of the executable, and the buildGui function to enable users to submit a job to the Farm."""
    
    # empty command dictionary
    _cmdFormat = []
    __version = ''
    __cmd = ''
    __name = ''
    
    def __init__(self, version="1.0", cmd="", name="Base Engine", checkEnabled=True):
	self.enabled = None         
        if checkEnabled:
            if self.isEnabled():
                self.enabled = True
        self.__version = str(version)
        self.__cmd = str(cmd)
	self.__name = str(name)
	self.process = None
	EngineRegistry.register(self)
	FarmConfig.setEngineData(self.name, [("app",self.app), ("enabled",self.enabled)])
    
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
    
    def run(self, kwargs):
        """ This is a standard run process for an engine, just build the command and use Popen"""
        try:
            if self.isEnabled():
                self.buildCommand(kwargs)
                if self.command and self.command != '':
                    self.process = subprocess.Popen(self.command, stdout=subprocess.PIPE)
                    return self.process
	    else:
		return None
        except Exception, e:
            print "<ERROR>", e
	    return None
    
    def buildCommand(self, kwargs):
        """must be implemented in the derived classes"""
        raise NotImplementedError('must be implemented in the derived classes')
    
    def isEnabled(self, force_check=False):
        """should be implemented in the derived classes"""
        return True
    
    def kill(self):
        """may be implemented in the derived classes"""
        if self.isEnabled and self.process and self.process.returncode == None:
            self.process.kill()
	    
    def buildGui(self):
	"""should be implemented in the derived classes for the submit panel in the manager gui. This should return a top-level QWidget for use in the submit panel of the Manager gui."""
        return None
    
    
class RenderEngine(BaseEngine):
    """Base class of all render engines"""
    
    