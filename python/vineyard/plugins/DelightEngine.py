import subprocess, os, sys, unittest, time
from vineyard.engines.BaseEngines import *

class DelightEngine(RenderEngine):
    
    def __init__(self):   
        RenderEngine.__init__(self, version="1.0", name="3Delight Engine")
    
    def buildCommand(self, kwargs):
                     #ribs, 
                     #frames=None, 
                     #crop=None, 
                     #resolution=None,
                     #threads=0,
                     #procs=0):
        """Build the command-line command to execute in order to do the rendering"""
        self.command = ""
        try:
            if not self.isEnabled():
                return
        except Exception, e:
            print "<ERROR>", e
            return
        self.command = self.app

        # dont display anything, even if the RIB says to do so
        self.command += " -nd"
        
        try:
            if kwargs['ribs'] == None:
                raise Exception, "ribs needs to be defined."
        except KeyError, e:
            raise Exception, "ribs needs to be defined for the 3Delight Engine."
        
        for key in kwargs:
            if key == 'frames':
                if type(kwargs[key]) == tuple:
                    (sf,ef,) = kwargs[key]
                    if type(sf) == int and type(ef) == int:
                        self.command += " -frames " + str(sf) + " " + str(ef)
                    else:
                        self.command = ""
                        raise Exception, "frames needs to be a 2-element tuple (startFrame, endFrame). start and end frame numbers should be ints"
                else:
                    self.command = ""
                    raise Exception, "frames needs to be a 2-element tuple (startFrame, endFrame)."
            
            if key == 'crop':
                if type(kwargs[key]) == tuple:
                    (l,r,t,b,) = kwargs[key]
                    if type(t) == int and type(l) == int and type(b) == int and type(r) == int:
                        self.command += " -crop " + str(l) + " " + str(r) + " " + str(t) + " " + str(b)
                    else:
                        self.command = ""
                        raise Exception, "crop needs to be a 4-element tuple (left, right, top, bottom). all numbers should be ints"
                else:
                    self.command = ""
                    raise Exception, "crop needs to be a 4-element tuple (left, right, top, bottom)."
            
            if key == 'resolution':
                if type(kwargs[key]) == tuple:
                    (x, y,) = resolution
                    if type(x) == int and type(y) == int:
                        self.command += " -res " + str(x) + " " + str(y)
                    else:
                        self.command = ""
                        raise Exception, "resolution needs to be a 2-element tuple (x, y). Both numbers should be ints"
                else:
                    self.command = ""
                    raise Exception, "resolution needs to be a 2-element tuple (x, y)."

            if key == 'ribs':
                if type(kwargs[key]) == list:
                    for r in kwargs[key]:
                        if type(r) == str:
                            self.command += " " + str(r)
                elif type(kwargs[key]) == str:
                    self.command += " " + str(ribs)
                else:
                    self.command = ""
                    raise Exception, "ribs argument needs to be a filename string or a list of filename strings"
        
            
        
    def isEnabled(self, setApp=False):
        if os.name != 'nt' and os.name != 'posix' and os.name != 'mac':
            return False
        try:
            prog_dir = os.environ['DELIGHT']
            prog_dir = os.path.join(prog_dir,'bin')
            if os.path.isdir(prog_dir):
                app = os.path.join(prog_dir, 'renderdl.exe')
                if os.path.exists(app):
                    self.app = app
                    return True
        except: pass
        return False
            
        
    def kill(self):
        if self.process and self.process.returncode == None:
            self.process.kill()

DelightEngine()      
#if __name__ == '__main__':
    #delight_engine = DelightEngine()
    #print EngineRegistry.getEngineNames()

        