import os
from vineyard.engines.BaseEngines import *
if os.name == 'nt':
    from _winreg import *

class AfterEffectsCS4Engine(RenderEngine):
         
    def __init__(self):
        RenderEngine.__init__(self, 
                              version="1.0", 
                              name="After Effects CS4 Engine",
                              osNames=('nt'),
                              validExecutables=("aerender.exe"))  
        
        self.commandFormat = {'project':'',
                              'comp': None,
                              'mem_usage': None,
                              'start_frame': None,
                              'end_frame': None,
                              'increment': None,
                              'reuse': None,
                              'output_module_template': None,
                              'render_settings_template': None,
                              'output_path': None,
                              'log_file_path': None,
                              'close_flag': None,
                              'index_in_render_queue':None,
                              'mp_enabled':None,
                              'continue_on_missing_footage':None}
        
   
    def buildCommand(self, kwargs=self.commandFormat):
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
        ret = RenderEngine.isEnabled(self, force_check)
        
        if ret == None:
            self.enabled = False
            self.app = ''
            if os.name == 'nt':                
                try:
                    aReg = ConnectRegistry(None,HKEY_LOCAL_MACHINE)
                    aKey = OpenKey(aReg, r"SOFTWARE\Adobe\After Effects\9.0") 
                    for i in range(1024):
                        val = EnumValue(aKey, i)
                        pth = str(val[1])
                        if val[0] == 'InstallPath' and os.path.isdir(pth):
                            # it's installed, get the full app path and return True
                            for app in self.executables:
                                a = os.path.join(pth, app)
                                if os.path.exists(a):
                                    self.app = a
                                    self.enabled = True
                                    break
                except Exception, e:
                    self.enabled = False
                    
        self.commitConfig()
        return self.enabled
        

AfterEffectsCS4Engine()

        