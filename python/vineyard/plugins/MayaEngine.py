import subprocess, os, sys, unittest, time
from vineyard.engines.BaseEngines import *

class Maya2010Engine(RenderEngine):
       
    def __init__(self):
        RenderEngine.__init__(self, version="1.0", name="Maya 2010 Engine")          
   
    def buildCommand(self, kwargs):
        self.command = ""
        
    def isEnabled(self, force_check=False):
        if self.enabled != None and not force_check:
            return self.enabled
        
        if os.name not in ('nt','mac','posix'):
            return False
        
        # check the config file first!
        _data = FarmConfig.getEngineData(self.name)
        
        if len(_data) == 0:
            pass
        else:
            bRet = False
            for (name, value) in _data:
                if name == 'app':
                    pass
                    #if os.path.exists(value):
                        #if len(value) > 12 and value[-10:] == "render.exe":
                            #self.app = value
                            #self.enabled = True
                        #else:
                            #raise Exception, "App path of " + str(self.name) + " is invalid: " + str(value) 
                    #else:
                        #raise Exception, "App path of " + str(self.name) + " does not exist: " + str(value)
                if name == 'enabled':
                    self.enabled = bool(value)
                    bRet = True
            if bRet:
                return self.enabled
        
        return False
        