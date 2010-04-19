#!/usr/bin/python

import sys, os
from PyQt4 import QtGui, QtCore
from vineyard import FarmConfig
import vineyard
from vineyard.FarmManager import NodeCache
from vineyard import FarmConfig

class SystemConfigurationDialog(QtGui.QDialog):
    
    def __init__(self, nodecache=None):
        QtGui.QMainWindow.__init__(self)
        self.nodecache = nodecache
        
        self.resize(300, 500)
        self.center()
        self.setWindowTitle('Configuration')
        if os.path.exists('grapes.png'):
            self.setWindowIcon(QtGui.QIcon('grapes.png'))
        elif os.path.exists('gui/grapes.png'):
            self.setWindowIcon(QtGui.QIcon('gui/grapes.png'))
        
        
        vbox = QtGui.QVBoxLayout()
        
        self.cb = QtGui.QCheckBox("Autodiscovery", self)
        vbox.addWidget(self.cb)
        self.cb.setChecked(vineyard.AUTODISCOVERY_ON)
        
        hbox = QtGui.QHBoxLayout()
        lbl = QtGui.QLabel("Status Update Period", self)
        self.spin1 = QtGui.QSpinBox(self)
        self.spin1.setMinimum(1)
        self.spin1.setMaximum(1000)
        self.spin1.setValue(vineyard.STATUS_UPDATE_PERIOD)
        hbox.addWidget(lbl)
        hbox.addWidget(self.spin1)
        vbox.addLayout(hbox)
        
        hbox = QtGui.QHBoxLayout()
        lbl = QtGui.QLabel("Autodiscovery Port", self)
        self.spin2 = QtGui.QSpinBox(self)
        self.spin2.setMinimum(1024)
        self.spin2.setMaximum(65535)
        self.spin2.setValue(vineyard.AUTODISCOVERY_PORT)
        hbox.addWidget(lbl)
        hbox.addWidget(self.spin2)
        vbox.addLayout(hbox)
        
        hbox = QtGui.QHBoxLayout()
        lbl = QtGui.QLabel("Status Port", self)
        self.spin3 = QtGui.QSpinBox(self)
        self.spin3.setMinimum(1024)
        self.spin3.setMaximum(65535)
        self.spin3.setValue(vineyard.STATUS_PORT)
        hbox.addWidget(lbl)
        hbox.addWidget(self.spin3)
        vbox.addLayout(hbox)
        
        okCancel = QtGui.QDialogButtonBox(self)
        okCancel.setOrientation(QtCore.Qt.Horizontal)
        okCancel.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        
        vbox.addStretch(1)
        vbox.addWidget(okCancel)
        
        self.setLayout(vbox)
        
        self.connect(okCancel,  QtCore.SIGNAL('accepted()'), self.applyChanges )
        self.connect(okCancel,  QtCore.SIGNAL('rejected()'), self, QtCore.SLOT('close()') )
        
    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
        
    def applyChanges(self):
        vineyard.AUTODISCOVERY_ON = self.cb.isChecked()
        vineyard.STATUS_UPDATE_PERIOD = self.spin1.value()
        vineyard.AUTODISCOVERY_PORT = self.spin2.value()
        vineyard.STATUS_PORT = self.spin3.value()
        
        # save the data to the config file
        FarmConfig.create()
        # restart the node cache threads
        self.nodecache.restart()       
        self.close()

if __name__ == '__main__':    
    app = QtGui.QApplication(sys.argv)
    win = SystemConfigurationDialog()    
    win.show()
    sys.exit(app.exec_())
