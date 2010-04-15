#!/usr/bin/python

import sys, os
from PyQt4 import QtGui, QtCore
# import all other gui
from vineyard.gui import SystemConfiguration, NodeView, Submit, JobView
# import all business logic
from vineyard import FarmManager, models

class VineyardMainWindow(QtGui.QMainWindow):
    
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

	self.nodecache = FarmManager.NodeCache()
	
        self.center()
        self.setWindowTitle('Vineyard Manager')
        traySignal = "activated(QSystemTrayIcon::ActivationReason)"        
        self.okayToClose = False        
        
        if os.path.exists('grapes.png'):
            icon = QtGui.QIcon('grapes.png')
        elif os.path.exists('gui/grapes.png'):
            icon = QtGui.QIcon('gui/grapes.png')
	    
	self.setWindowIcon(icon)
	    
	self.trayIcon = QtGui.QSystemTrayIcon(icon, self)  
	
	
	menu = QtGui.QMenu(self)
        exitAction = menu.addAction("Exit")
        self.trayIcon.setContextMenu(menu)
        self.trayIcon.show()
        self.connect(self.trayIcon, QtCore.SIGNAL(traySignal), self.__icon_activated)
	self.connect(exitAction, QtCore.SIGNAL("triggered()"), self.closeFromMenu)
        
        self.initMenuBar()
	self.initToolBar()
	self.initStatusBar()
	self.initDockWindows()
	
	#self.showMaximized()
	self.showBalloonMsg("Test", "this is only a test")
	
        
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
	
	help = QtGui.QAction("Help Contents", self)
        help.setShortcut('F1')
        help.setToolTip('View Help Documentation')
	help.setWhatsThis('View Help Documentation')
	help.setStatusTip('View Help Documentation')
        self.connect(help, QtCore.SIGNAL('triggered()'), self.OnHelp)
	
	updates = QtGui.QAction(self)
	updates.setText("Check for Updates")
        #updates.setShortcut('Ctrl+Q')
        updates.setToolTip('Check for software updates')
	updates.setWhatsThis('Check for software updates')
	updates.setStatusTip('Check for software updates')
        self.connect(updates, QtCore.SIGNAL('triggered()'), self.OnCheckUpdates)
	
	about = QtGui.QAction("About", self)
        about.setToolTip('About Vineyard')
	about.setWhatsThis('About Vineyard')
	about.setStatusTip('About Vineyard')
        self.connect(about, QtCore.SIGNAL('triggered()'), self.OnAbout)
	
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
	self.setCorner(QtCore.Qt.TopLeftCorner, QtCore.Qt.LeftDockWidgetArea)
	self.setCorner(QtCore.Qt.BottomLeftCorner, QtCore.Qt.LeftDockWidgetArea)
	self.setCorner(QtCore.Qt.TopRightCorner, QtCore.Qt.RightDockWidgetArea)
	self.setCorner(QtCore.Qt.BottomRightCorner, QtCore.Qt.RightDockWidgetArea)
	
	self.node_dock = QtGui.QDockWidget("Nodes", self)
        self.node_dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea | QtCore.Qt.TopDockWidgetArea | QtCore.Qt.BottomDockWidgetArea)
	nodeview = NodeView.NodeWidget(self.nodecache, self)
	self.node_dock.setWidget(nodeview)
	self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.node_dock)
        self.viewmenu.addAction(self.node_dock.toggleViewAction())
	
	# central widget
	#self.jobs_dock = QtGui.QDockWidget("Job Queue", self)
        #self.jobs_dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea | QtCore.Qt.TopDockWidgetArea | QtCore.Qt.BottomDockWidgetArea)
	self.jobs_view = JobView.JobWidget(self.nodecache, self)
	#self.jobs_dock.setWidget(self.jobs_view)
	#self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.jobs_dock)
        #self.viewmenu.addAction(self.jobs_dock.toggleViewAction())
	
	#tv = NodeView.NodeView(self)	
	#tv = QtGui.QTreeView(self)
	self.setCentralWidget(self.jobs_view)
	
	self.logs_dock = QtGui.QDockWidget("Logs", self)
        self.logs_dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea | QtCore.Qt.TopDockWidgetArea | QtCore.Qt.BottomDockWidgetArea)
	self.logs_dock.setWidget(QtGui.QTextEdit(self))
	self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.logs_dock)
        self.viewmenu.addAction(self.logs_dock.toggleViewAction())
	
	self.submit_dock = QtGui.QDockWidget("Submit", self)
        self.submit_dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea | QtCore.Qt.TopDockWidgetArea | QtCore.Qt.BottomDockWidgetArea)
	submit_view = Submit.SubmitWidget(self)
	self.submit_dock.setWidget(submit_view)
	self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.submit_dock)
        self.viewmenu.addAction(self.submit_dock.toggleViewAction())
        

    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
        
    def configure(self):
        # launch the configuration dialog
	dlg = SystemConfiguration.SystemConfigurationDialog()
        dlg.setModal(True)
	dlg.show()
	dlg.exec_()
    
    def closeFromMenu(self):
	self.okayToClose = True
	self.close()
    
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
	    
    def OnCheckUpdates(self):
	QtGui.QMessageBox.about(self, "Updates", "Update check has not been implemented yet.")
    
    def OnHelp(self):
	QtGui.QMessageBox.about(self, "Help", "Help has not been implemented yet.")
    
    def OnAbout(self):
	QtGui.QMessageBox.about(self, "About",
                "<h3><b>DedaFX Vineyard</b></h3><br>"
		"Render Management System for render farms and studio networks.<br><br>"
		"Copyright 2010, DedaFX")
	
    def showBalloonMsg(self, title, msg, iconType=QtGui.QSystemTrayIcon.Information):
	duration = 5 # seconds
	# icons:
	# 0 => no icon   == QtGui.QSystemTrayIcon.NoIcon
	# 1 => info icon == QtGui.QSystemTrayIcon.Information
	# 2 => Warning   == QtGui.QSystemTrayIcon.Warning
	# 3 => Critical  == QtGui.QSystemTrayIcon.Critical
	icon = QtGui.QSystemTrayIcon.MessageIcon(iconType)
	self.trayIcon.showMessage(title, msg, icon, duration)
    
def run(argv):
    app = QtGui.QApplication(argv)
    main_win = VineyardMainWindow() 
    for i in argv:
	if i.lower().find('show') > -1:
	    main_win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':    
    run(sys.argv[1:])
