#!/usr/bin/python

import sys, os
from PyQt4 import QtGui, QtCore
# import all other gui
from vineyard.gui import SystemConfiguration, NodeView
# import all business logic
from vineyard import FarmManager, models

class VineyardMainWindow(QtGui.QMainWindow):
    
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.resize(600, 300)
        self.center()
        self.setWindowTitle('Vineyard Manager')
        
        if os.path.exists('grapes.png'):
            self.setWindowIcon(QtGui.QIcon('grapes.png'))
        elif os.path.exists('gui/grapes.png'):
            self.setWindowIcon(QtGui.QIcon('gui/grapes.png'))
        
        self.initMenuBar()
        
    def initMenuBar(self):
        menubar = self.menuBar()
        
        sys_config = QtGui.QAction('Configuration', self)
        sys_config.setShortcut('Ctrl+S')
        sys_config.setStatusTip('Modify the system configuration settings')
        self.connect(sys_config, QtCore.SIGNAL('triggered()'), self.configure)

        system = menubar.addMenu('&System')
        system.addAction(sys_config)

    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
        
    def configure(self):
        # launch the configuration dialog
        pass
    
def run(argv):
    app = QtGui.QApplication(argv)
    main_win = VineyardMainWindow()    
    main_win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':    
    run(sys.argv)
