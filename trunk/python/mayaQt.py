import sys

try:
    import maya.standalone
    maya.standalone.initialize( name='python' ) 
    
except:
    #sys.stderr.write( "Not in standalone application\n" )
    
    import PyQt4
    from PyQt4 import QtGui, QtCore
    import pumpThread as pt

    app = None
    win = None

    def main():
        global app
        global win

        pt.initializePumpThread()
        app = PyQt4.QtGui.QApplication(sys.argv)
        win = PyQt4.QtGui.QLabel("Hello world!",None) 
        win.show() 
        app.connect(app, QtCore.SIGNAL("lastWindowClosed()"), app, QtCore.SLOT("quit()"))

    main()