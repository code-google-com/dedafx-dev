from PyQt4 import QtCore, QtGui

class LineDialog(QtGui.QDialog):
    def __init__(self, parent, cnc):
        QtGui.QDialog.__init__(self, parent)
        
        self.cnc = cnc
        
        self.setWindowTitle("Line Creator")
        self.resize(300,350)
        self.setModal(True)
        self.setFixedSize(300,350)
        
        btns = QtGui.QDialogButtonBox( QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        self.connect(btns, QtCore.SIGNAL("accepted()"), self.accept)
        self.connect(btns, QtCore.SIGNAL("rejected()"), self.reject)
        
        vbox = QtGui.QVBoxLayout(self)
        vbox.addStretch(1)
        vbox.addWidget(btns)

        
    def accept(self):        
        QtGui.QDialog.accept(self)
        
class ArcDialog(QtGui.QDialog):
    def __init__(self, parent, cnc):
        QtGui.QDialog.__init__(self, parent)
        
        self.cnc = cnc
        
        self.setWindowTitle("Arc Creator")
        self.resize(300,350)
        self.setModal(True)
        self.setFixedSize(300,350)
        
        btns = QtGui.QDialogButtonBox( QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        self.connect(btns, QtCore.SIGNAL("accepted()"), self.accept)
        self.connect(btns, QtCore.SIGNAL("rejected()"), self.reject)
        
        vbox = QtGui.QVBoxLayout(self)
        vbox.addStretch(1)
        vbox.addWidget(btns)
        
    def accept(self):        
        QtGui.QDialog.accept(self)
        
class ContourDialog(QtGui.QDialog):
    def __init__(self, parent, cnc):
        QtGui.QDialog.__init__(self, parent)
        
        self.cnc = cnc
        
        self.setWindowTitle("Contour Creator")
        self.resize(300,350)
        self.setModal(True)
        self.setFixedSize(300,350)
        
        btns = QtGui.QDialogButtonBox( QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        self.connect(btns, QtCore.SIGNAL("accepted()"), self.accept)
        self.connect(btns, QtCore.SIGNAL("rejected()"), self.reject)
        
        vbox = QtGui.QVBoxLayout(self)
        vbox.addStretch(1)
        vbox.addWidget(btns)
        
    def accept(self):        
        QtGui.QDialog.accept(self)
        