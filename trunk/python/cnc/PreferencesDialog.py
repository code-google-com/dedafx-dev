from PyQt4 import QtCore, QtGui

class PreferencesDialog(QtGui.QDialog):
    def __init__(self, parent, cnc):
        QtGui.QDialog.__init__(self, parent)
        
        self.cnc = cnc
        
        self.setWindowTitle("DedaFX CAM Preferences")
        self.resize(300,350)
        self.setModal(True)
        
        vbox = QtGui.QVBoxLayout(self)
        mgrp = QtGui.QGroupBox("Machine Setup", self)
        gl = QtGui.QGridLayout()
        
        l1 = QtGui.QLabel("Units")
        self.units = QtGui.QComboBox(self)
        self.units.addItems(["in", "mm"])
        if cnc.units == 'mm':
            self.units.setCurrentIndex(1)
        else:
            self.units.setCurrentIndex(0)
        gl.addWidget(l1, 0, 0, QtCore.Qt.AlignRight)
        gl.addWidget(self.units, 0, 1)
        
        l2 = QtGui.QLabel("Feedrate")
        self.feedrate = QtGui.QDoubleSpinBox(self)
        self.feedrate.setDecimals(3)
        self.feedrate.setSingleStep(0.5)
        self.feedrate.setValue(cnc.feedrate)
        gl.addWidget(l2, 1, 0, QtCore.Qt.AlignRight)
        gl.addWidget(self.feedrate, 1, 1)
        
        l3 = QtGui.QLabel("Z Increment")
        self.z_inc = QtGui.QDoubleSpinBox(self)
        self.z_inc.setDecimals(3)
        self.z_inc.setSingleStep(0.05)
        self.z_inc.setValue(cnc.z_increment)
        gl.addWidget(l3, 2, 0, QtCore.Qt.AlignRight)
        gl.addWidget(self.z_inc, 2, 1)
        
        l4 = QtGui.QLabel("Save Z Travel Height")
        self.safe_z = QtGui.QDoubleSpinBox(self)
        self.safe_z.setDecimals(3)
        self.safe_z.setSingleStep(0.1)
        self.safe_z.setValue(cnc.safe_z)
        gl.addWidget(l4, 3, 0, QtCore.Qt.AlignRight)
        gl.addWidget(self.safe_z, 3, 1)
        
        l5 = QtGui.QLabel("Tool Diameter")
        self.tool_d = QtGui.QDoubleSpinBox(self)
        self.tool_d.setDecimals(3)
        self.tool_d.setSingleStep(0.005)
        self.tool_d.setValue(cnc.tool.radius * 2)
        gl.addWidget(l5, 4, 0, QtCore.Qt.AlignRight)
        gl.addWidget(self.tool_d, 4, 1)
        
        mgrp.setLayout(gl)
        
        wpgrp = QtGui.QGroupBox("Workpiece", self)
        g2 = QtGui.QGridLayout()
        
        l6 = QtGui.QLabel("Minimum")
        l7 = QtGui.QLabel("Maximum")
        g2.addWidget(l6, 0, 1, QtCore.Qt.AlignCenter)
        g2.addWidget(l7, 2, 1, QtCore.Qt.AlignCenter)
        
        self.minx = QtGui.QDoubleSpinBox(self)
        self.minx.setDecimals(3)
        self.minx.setSingleStep(0.005)
        self.minx.setMinimum(-20.0)
        self.minx.setValue(cnc.workpiece.min.x)
        g2.addWidget(self.minx, 1, 0)
        
        self.miny = QtGui.QDoubleSpinBox(self)
        self.miny.setDecimals(3)
        self.miny.setSingleStep(0.005)
        self.miny.setMinimum(-20.0)
        self.miny.setValue(cnc.workpiece.min.y)
        g2.addWidget(self.miny, 1, 1)
        
        self.minz = QtGui.QDoubleSpinBox(self)
        self.minz.setDecimals(3)
        self.minz.setSingleStep(0.005)
        self.minz.setMinimum(-20.0)
        self.minz.setValue(cnc.workpiece.min.z)
        g2.addWidget(self.minz, 1, 2)
        
        self.maxx = QtGui.QDoubleSpinBox(self)
        self.maxx.setDecimals(3)
        self.maxx.setSingleStep(0.005)
        self.maxx.setValue(cnc.workpiece.max.x)
        g2.addWidget(self.maxx, 3, 0)
        
        self.maxy = QtGui.QDoubleSpinBox(self)
        self.maxy.setDecimals(3)
        self.maxy.setSingleStep(0.005)
        self.maxy.setValue(cnc.workpiece.max.y)
        g2.addWidget(self.maxy, 3, 1)
        
        self.maxz = QtGui.QDoubleSpinBox(self)
        self.maxz.setDecimals(3)
        self.maxz.setSingleStep(0.005)
        self.maxz.setValue(cnc.workpiece.max.z)
        g2.addWidget(self.maxz, 3, 2)
        
        wpgrp.setLayout(g2)
        
        vbox.addWidget(mgrp)
        vbox.addWidget(wpgrp)
        
        btns = QtGui.QDialogButtonBox( QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        self.connect(btns, QtCore.SIGNAL("accepted()"), self.accept)
        self.connect(btns, QtCore.SIGNAL("rejected()"), self.reject)
        vbox.addWidget(btns)

        
    def accept(self):
        self.cnc.units = self.units.currentText()
        self.cnc.feedrate = self.feedrate.value()
        self.cnc.z_increment = self.z_inc.value()
        self.cnc.safe_z = self.safe_z.value()
        self.cnc.tool.radius = self.tool_d.value() / 2
        
        self.cnc.workpiece.min.x = self.minx.value()
        self.cnc.workpiece.min.y = self.miny.value()
        self.cnc.workpiece.min.z = self.minz.value()
        self.cnc.workpiece.max.x = self.maxx.value()
        self.cnc.workpiece.max.y = self.maxy.value()
        self.cnc.workpiece.max.z = self.maxz.value()
        
        QtGui.QDialog.accept(self)
