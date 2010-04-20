import subprocess, os, sys, unittest, time
from vineyard.engines.BaseEngines import *
import vineyard.FarmConfig

class AfterEffectsCS4Engine(vineyard.engines.BaseEngines.RenderEngine):
    
    commandFormat = [{'Project':['project', 'str', 'required']},
                {'Composition':['comp', 'str','not-required', None]},
                {'Memory Usage':['mem_usage', 'str','not-required', None]},
                {'Start Frame':['start_frame','int','not-required', None]},
                {'End Frame':['end_frame', 'int','not-required', None]},
                {'Increment':['increment','int','not-required', None]},
                {'Reuse':['reuse', 'bool','not-required', None]},
                {'Output Module Template':['output_module_template', 'str','not-required', None]},
                {'Render Settings Template':['render_settings_template', 'str','not-required', None]},
                {'Output Path':['output_path', 'str','not-required', None]},
                {'Log File Path':['log_file_path', 'str','not-required', None]},
                {'Close Flag':['close_flag', 'str','not-required', [None, ""]]},
                {'Index in Render Queue':['index_in_render_queue', 'str','not-required', None]},
                {'MP Enabled':['mp_enabled', 'str','not-required', None]},
                {'Continue on Missing Footage':['continue_on_missing_footage', 'bool','not-required', None]}
                ]
    
    commandParams = ()
    
    def __init__(self, checkEnabled=True):
        self.enabled = False
        
        if os.name != 'nt' and os.name != 'mac':
            raise Exception, "After Effects engine currently only works on Windows!"
        if checkEnabled:
            if self.isEnabled():
                self.enabled = True
            #else:
            #    raise Exception, "After Effects CS4 disabled on this machine!"
        
        vineyard.engines.BaseEngines.RenderEngine.__init__(self, version="1.0", name="After Effects CS4 Engine", filename=__file__)
        
        vineyard.FarmConfig.setEngineData(self.name, [("app",self.app), ("enabled",self.enabled)])
        
    def run(self, kwargs):
        """ This is a standard run process for an engine, just build the command and use Popen"""
        try:
            if self.isEnabled():
                self.buildCommand(kwargs)
                if self.command and self.command != '':
                    self.process = subprocess.Popen(self.command, stdout=subprocess.PIPE)
                    return self.process
        except Exception, e:
            print "<ERROR>", e
    
    def buildCommand(self, kwargs):
                     #project, 
                     #comp=None, 
                     #mem_usage=None,
                     #start_frame=None, 
                     #end_frame = None, 
                     #increment=None, 
                     #reuse=None,
                     #output_module_template=None,
                     #render_settings_template=None,
                     #output_path=None,
                     #log_file_path=None,
                     #close_flag=None,
                     #index_in_render_queue=None,
                     #mp_enabled=None,
                     #continue_on_missing_footage=None
                     #):
        """Build the command-line command to execute in order to do the rendering"""
        self.command = ""
        try:
            if not self.isEnabled():
                return
        except Exception, e:
            print "<ERROR>", e
            return
        self.command = self.app
        
        try:
            if kwargs['project'] == None:
                raise Exception, "project needs to be defined."
        except KeyError, e:
            raise Exception, "project needs to be defined for the After Effects Engine."

        for key in kwargs:
            if key == 'project':
                if type(kwargs['project']) == str and kwargs['project'][-3:].lower() == 'aep':
                    self.command += " -project " + str(kwargs['project'])
                else:
                    self.command = ""
                    raise Exception, "project needs to be an After Effects project file."
        
            if key == 'comp':
                if type(kwargs['comp']) == str:
                    self.command += " -comp " + str(kwargs['comp'])
                else:
                    self.command = ""
                    raise Exception, "comp needs to be a string."
            
            if key == 'start_frame':
                if type(kwargs['start_frame']) == int:
                    self.command += " -s " + str(start_frame)
                else:
                    self.command = ""
                    raise Exception, "start_frame needs to be an int."
            
            if key == 'end_frame':
                if type(kwargs['end_frame']) == int:
                    self.command += " -e " + str(kwargs['end_frame'])
                else:
                    self.command = ""
                    raise Exception, "end_frame needs to be an int."
            
            if key == 'increment':
                if type(kwargs['increment']) == int and increment > 0:
                    self.command += " -i " + str(kwargs['increment'])
                else:
                    self.command = ""
                    raise Exception, "increment needs to be a positive int."
            
            if key == 'reuse' and kwargs[key] != None:
                if type(kwargs['reuse']) == int or type(kwargs['reuse']) == bool:
                    if reuse:
                        self.command += " -reuse"
                    else:
                        self.command = ""
                        raise Exception, "reuse needs to be a bool or an int."
            
            if key == 'output_module_template':
                if type(kwargs['output_module_template']) == str:
                    self.command += " -OMtemplate " + str(kwargs['output_module_template'])
                else:
                    self.command = ""
                    raise Exception, "output_module_template needs to be a str."
            
            if key == 'render_settings_template':
                if type(kwargs['render_settings_template']) == str:
                    self.command += " -RStemplate " + str(kwargs['render_settings_template'])
                else:
                    self.command = ""
                    raise Exception, "render_settings_template needs to be a str."
            
            if key == 'output_path':
                if type(kwargs['output_path']) == str:
                    self.command += " -output " + str(kwargs['output_path'])
                else:
                    self.command = ""
                    raise Exception, "output_path needs to be a str."
            
            if key == 'log_file_path':
                if type(kwargs['log_file_path']) == str:
                    self.command += " -log " + str(kwargs['log_file_path'])
                else:
                    self.command = ""
                    raise Exception, "log_file_path needs to be a str."
            
            if key == 'close_flag':
                if type(kwargs['close_flag']) == str:
                    self.command += " -close " + str(kwargs['close_flag'])
                else:
                    self.command = ""
                    raise Exception, "close_flag needs to be an int."
            
            if key == 'index_in_render_queue' and kwargs[key] != None:
                if type(kwargs['index_in_render_queue']) == int:
                    self.command += " -rqindex " + str(kwargs['index_in_render_queue'])
                else:
                    self.command = ""
                    raise Exception, "index_in_render_queue needs to be an int."
            
            if key == 'mp_enabled' and kwargs[key] != None:
                if type(kwargs['mp_enabled']) == int and (kwargs['mp_enabled'] == 0 or kwargs['mp_enabled'] == 1):
                    self.command += " -mp_enabled " + str(kwargs['mp_enabled'])
                else:
                    self.command = ""
                    raise Exception, "mp_enabled needs to be an int (0 or 1)."
            
            if key == 'continue_on_missing_footage':
                if type(kwargs['continue_on_missing_footage']) == int or type(kwargs['continue_on_missing_footage']) == bool:
                    if kwargs['continue_on_missing_footage']:
                        self.command += " -continue_on_missing_footage"
                else:
                    self.command = ""
                    raise Exception, "continue_on_missing_footage needs to be an int or bool."
        
    def isEnabled(self, force_check=False):
        try:
            if self.enabled != None and force_check:
                return self.enabled
        except:
            pass
        
        if os.name != 'nt' and os.name != 'mac':
            return False
        
        # check the config file first!
        _data = vineyard.FarmConfig.getEngineData(self.name)
        
        if len(_data) == 0:
            prog_dir = os.environ['ProgramFiles']
            if os.name == 'nt':
                for d in [ 'Adobe', 'Adobe After Effects CS4', 'Support Files' ]:
                    prog_dir = os.path.join(prog_dir, d)
            elif os.name == 'mac':
                prog_dir = os.path.join(proj_dir, 'Adobe After Effects CS4')
            if os.path.isdir(prog_dir):
                app = os.path.join(prog_dir, 'aerender.exe')
                if os.path.exists(app):
                    self.app = app
                    self.enabled = True
                    return True
                else:
                    return False
            else:
                return False
        else:
            # this engine is configured!
            # _data should be a list of (name, value) pairs
            bRet = False
            for (name, value) in _data:
                if name == 'app':
                    if os.path.exists(value):
                        if len(value) > 12 and value[-12:] == "aerender.exe":
                            self.app = value
                            self.enabled = True
                        else:
                            raise Exception, "App path of " + str(self.name) + " is invalid: " + str(value) + " needs to refer to aerender.exe!"
                    else:
                        raise Exception, "App path of " + str(self.name) + " does not exist: " + str(value)
                if name == 'enabled':
                    self.enabled = bool(value)
                    bRet = True
            if bRet:
                return self.enabled
        return False
        
    def kill(self):
        if self.isEnabled and self.process and self.process.returncode == None:
            self.process.kill()

try:
    AfterEffectsCS4Engine()
except Exception, e:
    print '<error>', e

#if __name__ == '__main__':
#    ae_cs4_engine = AfterEffectsCS4Engine()
#    print EngineRegistry.getEngineNames()
        