import os
from vineyard.engines.BaseEngines import *
from PyQt4 import QtGui, QtCore
#if os.name == 'nt':
    #from _winreg import *

class AfterEffectsCS4Engine(RenderEngine):
         
    def __init__(self):
        RenderEngine.__init__(self, 
                              version="1.0", 
                              name="Real Flow 4 Engine",
                              osNames=('nt'),
                              validExecutables=("realflownode.exe"))  
        
        self.commandFormat = {'project':'',
                              'mesh': None,
                              'range':None, # two element tuple
                              'threads':None, 
                              'license':None,
                              'log':None, 
                              'script':None, # does not need a scene file to do this
                              'useCache':None
                              }
        
        self.commandToSend = {}
        
   
    def buildCommand(self, kwargs=None):
        """Build the command-line command to execute in order to do the simulating or mesh construction"""
        if kwargs == None:
            kwargs = self.commandFormat
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
            raise Exception, "project needs to be defined for the Real Flow Engine."

        for key in kwargs:
            if key == 'project':
                if type(kwargs['project']) == str and kwargs['project'][-3:].lower() == 'flw':
                    self.command += " -project " + str(kwargs['project'])
                else:
                    self.command = ""
                    raise Exception, "project needs to be a Real Flow project file."
        

        
    def isEnabled(self, force_check=False):
        ret = RenderEngine.isEnabled(self, force_check)
        
        if ret == None:
            self.enabled = False
            self.app = ''
            
            # this needs to be configured, or the drive needs to be scanned for the executable...
                    
        self.commitConfig()
        return self.enabled
    
    def buildGui(self):
        root = QtGui.QWidget()        
        vbox = QtGui.QVBoxLayout()
        
        # project file
        hbox = QtGui.QHBoxLayout()
        hbox.setMargin(0)
        label = QtGui.QLabel('Project')
        label.setAlignment(QtCore.Qt.AlignRight)
        hbox.addWidget(label)
        self.project_path = QtGui.QLineEdit(root)
        hbox.addWidget(self.project_path)
        fb = QtGui.QPushButton('...', root)
        fb.setMaximumSize(QtCore.QSize(22,22))
        def getFile():
            fname = QtGui.QFileDialog.getOpenFileName(root, 'Select File', '', '*.rfs|*.flw')
            self.project_path.setText(fname)
        root.connect(fb, QtCore.SIGNAL('clicked()'), getFile)
        hbox.addWidget(fb)
        cb = self.makeCbEnabled(self.project_path, True)
        fb.connect(cb, QtCore.SIGNAL("stateChanged(int)"), fb.setEnabled)
        hbox.addWidget(cb)
        vbox.addLayout(hbox)
        
        root.setLayout(vbox)        
        return root
    
    def getCmdDict(self):
        return {'name':self.name}

RealFlow4Engine()

        