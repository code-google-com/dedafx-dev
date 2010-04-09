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
        traySignal = "activated(QSystemTrayIcon::ActivationReason)"        
        self.okayToClose = False
        self.trayIcon = TrayIcon(self)     
        self.trayIcon.show()
        QtCore.QObject.connect(self.trayIcon, QtCore.SIGNAL(traySignal), self.__icon_activated)
        
        if os.path.exists('grapes.png'):
            self.setWindowIcon(QtGui.QIcon('grapes.png'))
        elif os.path.exists('gui/grapes.png'):
            self.setWindowIcon(QtGui.QIcon('gui/grapes.png'))
        
        self.initMenuBar()
	self.initToolBar()
	self.initStatusBar()
	self.initDockWindows()
        
    def initMenuBar(self):
        menubar = self.menuBar()
        
	# System menu
        sys_config = QtGui.QAction('Configuration', self)
        sys_config.setShortcut('Ctrl+S')
        sys_config.setStatusTip('Modify the system configuration settings')
        self.connect(sys_config, QtCore.SIGNAL('triggered()'), self.configure)

        system = menubar.addMenu('&System')
        system.addAction(sys_config)
	
	# view menu
	self.viewmenu = menubar.addMenu('&View')
        
        # help menu
	helpmenu = menubar.addMenu('&Help')
	
	help = QtGui.QAction(self)
	help.setText("Help Contents")
        help.setShortcut('F1')
        help.setToolTip('View Help Documentation')
	help.setWhatsThis('View Help Documentation')
	help.setStatusTip('View Help Documentation')
        self.connect(help, QtCore.SIGNAL('clicked()'), self.OnHelp)
	
	updates = QtGui.QAction(self)
	updates.setText("Check for Updates")
        #updates.setShortcut('Ctrl+Q')
        updates.setToolTip('Check for software updates')
	updates.setWhatsThis('Check for software updates')
	updates.setStatusTip('Check for software updates')
        self.connect(updates, QtCore.SIGNAL('clicked()'), self.OnCheckUpdates)
	
	about = QtGui.QAction(self)
	about.setText("About")
        #updates.setShortcut('Ctrl+Q')
        about.setToolTip('About Vineyard')
	about.setWhatsThis('About Vineyard')
	about.setStatusTip('About Vineyard')
        self.connect(about, QtCore.SIGNAL('clicked()'), self.OnAbout)
	
	helpmenu.addAction(help)
	helpmenu.addSeparator()
	helpmenu.addAction(updates)
	helpmenu.addSeparator()
	helpmenu.addAction(about)
	
    def initToolBar(self):
	pass
    
    def initStatusBar(self):
	self.statusBar().showMessage("Ready")
    
    def initDockWindows(self):
	self.node_dock = QtGui.QDockWidget("Nodes", self)
        self.node_dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
	#self.node_dock.setWidget(self.node_view)
	self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.node_dock)
        self.viewMenu.addAction(self.node_dock.toggleViewAction())
	
	self.jobs_dock = QtGui.QDockWidget("Job Queue", self)
        self.jobs_dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
	#self.jobs_dock.setWidget(self.jobs_view)
	self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.jobs_dock)
        self.viewMenu.addAction(self.jobs_dock.toggleViewAction())
	
	self.logs_dock = QtGui.QDockWidget("Logs", self)
        self.logs_dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
	#self.node_dock.setWidget(self.node_view)
	self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.logs_dock)
        self.viewMenu.addAction(self.logs_dock.toggleViewAction())
	
	self.submit_dock = QtGui.QDockWidget("Submit", self)
        self.submit_dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
	#self.node_dock.setWidget(self.node_view)
	self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.submit_dock)
        self.viewMenu.addAction(self.submit_dock.toggleViewAction())
        

    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
        
    def configure(self):
        # launch the configuration dialog
        pass
    
    def closeEvent(self, event):
        if self.okayToClose: 
            #user asked for exit
            self.trayIcon.hide()
            event.accept()
        else:
            #"minimize"
            self.hide()
            self.trayIcon.show() 
            event.ignore()
    
    def __icon_activated(self, reason):
        if reason == QtGui.QSystemTrayIcon.DoubleClick:
            self.show()
    
def run(argv):
    app = QtGui.QApplication(argv)
    main_win = VineyardMainWindow()    
    main_win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':    
    run(sys.argv)
