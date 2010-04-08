# validator classes for IP and MAC address input fields

from PyQt4 import QtGui, QtCore

class IPAddressValidator(QtGui.QValidator):
    def __init__(self, *args):
        QtGui.QValidator.__init__(self, *args)
        
class MACAddressValidator(QtGui.QValidator):
    def __init__(self, *args):
        QtGui.QValidator.__init__(self, *args)
