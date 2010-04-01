#!/usr/bin/python

import sys
from PyQt4 import QtGui, QtCore

class SystemConfigurationDialog(QtGui.QDialog):
    
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.resize(300, 500)
        self.center()
        self.setWindowTitle('Configuration')
        self.setWindowIcon(QtGui.QIcon('icons/vineyardLogo.png'))
        
        vbox = QtGui.QVBoxLayout()
        
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
        print 'changes applied'
        self.close()

if __name__ == '__main__':    
    app = QtGui.QApplication(sys.argv)
    win = SystemConfigurationDialog()    
    win.show()
    sys.exit(app.exec_())
