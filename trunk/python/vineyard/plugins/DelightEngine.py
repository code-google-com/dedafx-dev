import subprocess, os, sys, unittest, time
from vineyard.engines.BaseEngines import *

class DelightEngine(RenderEngine):
    
    def __init__(self, checkEnabled=True):
       
        if os.name != 'nt' and os.name != 'mac':
            raise Exception, "3Delight engine currently only works on Windows!"
        if checkEnabled and not self.isEnabled():
            raise Exception, "3Delight not found on this machine!"
        
        RenderEngine.__init__(self, version="1.0", name="3Delight Engine")
        
    def run(self):
        self.process = subprocess.Popen(self.command, stdout=subprocess.PIPE)
        return self.process
    
    def buildCommand(self, 
                     ribs, 
                     frames=None, 
                     crop=None, 
                     resolution=None,
                     threads=0,
                     procs=0):
        """Build the command-line command to execute in order to do the rendering"""
        self.command = self.app

        # dont display anything, even if the RIB says to do so
        self.command += " -nd"
        
        if frames:
            if type(frames) == tuple:
                (sf,ef,) = frames
                if type(sf) == int and type(ef) == int:
                    self.command += " -frames " + str(sf) + " " + str(ef)
                else:
                    self.command = ""
                    raise Exception, "frames needs to be a 2-element tuple (startFrame, endFrame). start and end frame numbers should be ints"
            else:
                self.command = ""
                raise Exception, "frames needs to be a 2-element tuple (startFrame, endFrame)."
            
        if crop:
            if type(crop) == tuple:
                (l,r,t,b,) = crop
                if type(t) == int and type(l) == int and type(b) == int and type(r) == int:
                    self.command += " -crop " + str(l) + " " + str(r) + " " + str(t) + " " + str(b)
                else:
                    self.command = ""
                    raise Exception, "crop needs to be a 4-element tuple (left, right, top, bottom). all numbers should be ints"
            else:
                self.command = ""
                raise Exception, "crop needs to be a 4-element tuple (left, right, top, bottom)."
            
        if resolution:
            if type(resolution) == tuple:
                (x, y,) = resolution
                if type(x) == int and type(y) == int:
                    self.command += " -res " + str(x) + " " + str(y)
                else:
                    self.command = ""
                    raise Exception, "resolution needs to be a 2-element tuple (x, y). Both numbers should be ints"
            else:
                self.command = ""
                raise Exception, "resolution needs to be a 2-element tuple (x, y)."

        if type(ribs) == list:
            for r in ribs:
                if type(r) == str:
                    self.command += " " + str(r)
        elif type(ribs) == str:
            self.command += " " + str(ribs)
        else:
            self.command = ""
            raise Exception, "ribs argument needs to be a filename string or a list of filename strings"
        
            
        
    def isEnabled(self, setApp=False):
        try:
            prog_dir = os.environ['DELIGHT']
            prog_dir = os.path.join(prog_dir,'bin')
            if os.path.isdir(prog_dir):
                app = os.path.join(prog_dir, 'renderdl.exe')
                if os.path.exists(app):
                    self.app = app
                    return True
                else:
                    return False
            else:
                return False
        except:
            return False
            
        
    def kill(self):
        if self.process and self.process.returncode == None:
            self.process.kill()

        
if __name__ == '__main__':
    #delight_engine = DelightEngine()
    print EngineRegistry.getEngineNames()

        