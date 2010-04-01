#!/usr/bin/python

import sys
from PyQt4 import QtGui, QtCore

class VineyardMainWindow(QtGui.QMainWindow):
    
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.resize(600, 300)
        self.center()
        self.setWindowTitle('Vineyard Manager')
        self.setWindowIcon(QtGui.QIcon('icons/vineyardLogo.png'))
        
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
        print 'works'

if __name__ == '__main__':    
    app = QtGui.QApplication(sys.argv)
    main_win = VineyardMainWindow()    
    main_win.show()
    sys.exit(app.exec_())
