import subprocess, os, sys, unittest, time
from vineyard.engines.BaseEngines import *

class AfterEffectsCS4Engine(RenderEngine):
    
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
        
        if os.name != 'nt' and os.name != 'mac':
            raise Exception, "After Effects engine currently only works on Windows!"
        if checkEnabled and not self.isEnabled():
            raise Exception, "After Effects CS4 not found on this machine!"
        
        RenderEngine.__init__(self, version="1.0", name="After Effects CS4 Engine")
        
    def run(self):
        self.buildCommand()
        self.process = subprocess.Popen(self.command, stdout=subprocess.PIPE)
        return self.process
    
    def buildCommand(self):
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
        self.command = self.app

        for key in kwargs:
            if key == 'project':
                if type(project) == str and project[-3:].lower() == 'aep':
                    self.command += " -project " + str(project)
                else:
                    self.command = ""
                    raise Exception, "project needs to be an After Effects project file."
        
        if comp:
            if type(comp) == str:
                self.command += " -comp " + str(comp)
            else:
                self.command = ""
                raise Exception, "comp needs to be a string."
            
        if start_frame:
            if type(start_frame) == int:
                self.command += " -s " + str(start_frame)
            else:
                self.command = ""
                raise Exception, "start_frame needs to be an int."
            
        if end_frame:
            if type(end_frame) == int:
                self.command += " -e " + str(end_frame)
            else:
                self.command = ""
                raise Exception, "end_frame needs to be an int."
            
        if increment:
            if type(increment) == int and increment > 0:
                self.command += " -i " + str(increment)
            else:
                self.command = ""
                raise Exception, "increment needs to be a positive int."
            
        if reuse != None:
            if type(reuse) == int or type(reuse) == bool:
                if reuse:
                    self.command += " -reuse"
            else:
                self.command = ""
                raise Exception, "reuse needs to be a bool or an int."
            
        if output_module_template:
            if type(output_module_template) == str:
                self.command += " -OMtemplate " + str(output_module_template)
            else:
                self.command = ""
                raise Exception, "output_module_template needs to be a str."
            
        if render_settings_template:
            if type(render_settings_template) == str:
                self.command += " -RStemplate " + str(render_settings_template)
            else:
                self.command = ""
                raise Exception, "render_settings_template needs to be a str."
            
        if output_path:
            if type(output_path) == str:
                self.command += " -output " + str(output_path)
            else:
                self.command = ""
                raise Exception, "output_path needs to be a str."
            
        if log_file_path:
            if type(log_file_path) == str:
                self.command += " -log " + str(log_file_path)
            else:
                self.command = ""
                raise Exception, "log_file_path needs to be a str."
            
        if close_flag:
            if type(close_flag) == str:
                self.command += " -close " + str(close_flag)
            else:
                self.command = ""
                raise Exception, "close_flag needs to be an int."
            
        if index_in_render_queue != None:
            if type(index_in_render_queue) == int:
                self.command += " -rqindex " + str(index_in_render_queue)
            else:
                self.command = ""
                raise Exception, "index_in_render_queue needs to be an int."
            
        if mp_enabled != None:
            if type(mp_enabled) == int and (mp_enabled == 0 or mp_enabled == 1):
                self.command += " -mp_enabled " + str(mp_enabled)
            else:
                self.command = ""
                raise Exception, "mp_enabled needs to be an int (0 or 1)."
            
        if continue_on_missing_footage:
            if type(continue_on_missing_footage) == int or type(continue_on_missing_footage) == bool:
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
                return True
            else:
                return False
        else:
            return False
        
    def kill(self):
        if self.process and self.process.returncode == None:
            self.process.kill()

        
if __name__ == '__main__':
    ae_cs4_engine = AfterEffectsCS4Engine()
    print EngineRegistry.getEngineNames()
        