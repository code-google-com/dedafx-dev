import os
from vineyard.engines.BaseEngines import *

class Maya2010Engine(RenderEngine):
       
    def __init__(self):
        RenderEngine.__init__(self, 
                              version="1.0", 
                              name="Maya 2010 Engine",
                              osNames=('nt'),# (TODO:) 'posix', 'mac'
                              validExecutables=("Render.exe")
                              )
        self.commandFormat = {'filename':'',
                              }     
        self.renderers = ()
   
    def buildCommand(self, kwargs):
        """Build the command-line command to execute in order to do the rendering"""
        self.command = ""
        try:
            if not self.isEnabled():
                return
        except Exception, e:
            print "<ERROR>", e
            return
        self.command = self.app
        
        
        
        # filename should be last in the command, so iterate again
        for key in kwargs:
            if key == 'filename':
                if type(kwargs[key]) == str:
                    f = kwargs[key]
                    if os.path.exists(f):
                        self.command += " " + str(f)
                    else:
                        self.command = ""
                        raise Exception, "File does not exist!"
                else:
                    self.command = ""
                    raise Exception, "File needs to be a string."
        
    def isEnabled(self, force_check=False):
        ret = RenderEngine.isEnabled(self, force_check)
        
        if ret == None:
            self.enabled = False
            self.app = ''
            if os.name == 'nt':                
                try:
                    aReg = ConnectRegistry(None,HKEY_LOCAL_MACHINE)
                    aKey = OpenKey(aReg, r"SOFTWARE\Autodesk\Maya\2010\Setup\InstallPath") 
                    for i in range(1024):
                        val = EnumValue(aKey, i)
                        pth = str(val[1])
                        if val[0] == 'MAYA_INSTALL_LOCATION' and os.path.isdir(pth):
                            pth = os.path.join(pth, 'bin')
                            if os.path.isdir(pth):
                                # it's installed, get the full app path and return True
                                for app in self.executables:
                                    a = os.path.join(pth, app)
                                    if os.path.exists(a):
                                        self.app = a
                                        self.enabled = True
                                        break
                except Exception, e:
                    self.enabled = False
                    
        # get the available renderers installed in this maya installation
        if self.enabled:
            self.renderers = ()
            import subprocess
            proc = subprocess.Popen([self.app, " -listRenderers"])
            print retcode
                    
        self.commitConfig()
        return self.enabled
        