#!/usr/bin/python

import sys, os
from PyQt4 import QtGui, QtCore
from vineyard.FarmManager import NodeCache
from vineyard.models import *

class JobView(QtGui.QWidget):
    """container class for placing table into a dock widget"""
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        layout = QtGui.QVBoxLayout()
        header = QtGui.QLabel("Jobs", self)
        layout.addWidget(header)
        table = JobTableView(self)
        layout.addWidget(table)
        layout.setMargin(2)
        self.setLayout(layout)
    
class JobTableView(QtGui.QTreeView):
    
    def __init__(self, *args):
        QtGui.QTableView.__init__(self, *args)