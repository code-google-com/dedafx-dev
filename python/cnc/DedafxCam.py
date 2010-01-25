from GlView import *
from PreferencesDialog import *
from DataModels import *
from CreateDialogs import *

class GcodeGui(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.cnc = CncMachine()
        self.setWindowTitle("DedaFX CAM")
        self.resize(800,600)
        self.setCentralWidget(GlView(cnc=self.cnc))
        #self.statusBar()
        
        menubar = self.menuBar()
        f = menubar.addMenu('&File')
        nw = QtGui.QAction('&New', self)
        nw.setStatusTip('New file')
        self.connect(nw, QtCore.SIGNAL('triggered()'), self.fileNew)
        f.addAction(nw)
        opn = QtGui.QAction('&Open', self)
        opn.setStatusTip('Open a file')
        self.connect(opn, QtCore.SIGNAL('triggered()'), self.fileOpen)
        f.addAction(opn)
        f.addSeparator()
        sv = QtGui.QAction('&Save', self)
        sv.setStatusTip('Save the current file')
        self.connect(sv, QtCore.SIGNAL('triggered()'), self.fileSave)
        f.addAction(sv)
        
        e = menubar.addMenu('&Edit')        
        pref = QtGui.QAction('&Preferences', self)
        pref.setStatusTip('Set up cnc and workpiece preferences')
        self.connect(pref, QtCore.SIGNAL('triggered()'), self.prefs)
        e.addAction(pref)
        
        c = menubar.addMenu('&Create')
        ln = QtGui.QAction('&Line', self)
        ln.setStatusTip('Create a line segment to cut')
        self.connect(ln, QtCore.SIGNAL('triggered()'), self.createLine)
        c.addAction(ln)
        
        arc = QtGui.QAction('&Arc', self)
        arc.setStatusTip('Create an arc to cut')
        self.connect(arc, QtCore.SIGNAL('triggered()'), self.createArc)
        c.addAction(arc)     
        
        contour = QtGui.QAction('&Contour', self)
        contour.setStatusTip('Create a contour cut')
        self.connect(contour, QtCore.SIGNAL('triggered()'), self.createContour)
        c.addAction(contour) 
        
        v = menubar.addMenu('&View')
        top = QtGui.QAction('Top', self)
        top.setStatusTip('Top view of workpiece')
        self.connect(top, QtCore.SIGNAL('triggered()'), self.topView)
        v.addAction(top)
        front = QtGui.QAction('Front', self)
        front.setStatusTip('Front view of workpiece')
        self.connect(front, QtCore.SIGNAL('triggered()'), self.frontView)
        v.addAction(front)
        side = QtGui.QAction('Side', self)
        side.setStatusTip('Side view of workpiece')
        self.connect(side, QtCore.SIGNAL('triggered()'), self.sideView)
        v.addAction(side)
        persp = QtGui.QAction('Persp', self)
        persp.setStatusTip('Perspective view of workpiece')
        self.connect(persp, QtCore.SIGNAL('triggered()'), self.perspView)
        v.addAction(persp)
        
        h = menubar.addMenu('&Help')
        
        self.toolbar = self.addToolBar('create')
        self.toolbar.addAction(ln)
        self.toolbar.addAction(arc)
        self.toolbar.addAction(contour)
        
    def fileNew(self):
        pass
    
    def fileOpen(self):
        pass
    
    def fileSave(self):
        pass
        
    def prefs(self):
        pd = PreferencesDialog(self, self.cnc)
        pd.show()
        
    def createLine(self):
        d = LineDialog(self, self.cnc)
        d.show()
    
    def createArc(self):
        d = ArcDialog(self, self.cnc)
        d.show()
    
    def createContour(self):
        d = ContourDialog(self, self.cnc)
        d.show()
    
    def topView(self):
        pass
    
    def frontView(self):
        pass
    
    def sideView(self):
        pass
    
    def perspView(self):
        pass

def run():    
    app = QtGui.QApplication(sys.argv)    
    win=GcodeGui()
    win.show()
    app.connect(app, QtCore.SIGNAL("lastWindowClosed()")
                 , app
                 , QtCore.SLOT("quit()")
                 )
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    run()
    
