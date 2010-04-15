#!/usr/bin/python

import sys, os
from PyQt4 import QtGui, QtCore
from vineyard.FarmManager import NodeCache
from vineyard.models import *

class JobWidget(QtGui.QWidget):
    """container class for placing table into a dock widget"""
    def __init__(self, nodecache, *args):
        QtGui.QWidget.__init__(self, *args)
        layout = QtGui.QVBoxLayout()
        header = QtGui.QLabel("Jobs", self)
        layout.addWidget(header)
        table = JobTreeView(nodecache, self)
        layout.addWidget(table)
        layout.setMargin(2)
        self.setLayout(layout)
    
class JobTreeView(QtGui.QTreeView):
    
    def __init__(self, nodecache, *args):
        QtGui.QTableView.__init__(self, *args)
       
        self.job_list = []    
        
        #self.getJobs()
        
        model = JobDataModel(nodecache)
        self.setModel(model)
        #self.expandAll()
        #self.nodecache = nodecache
        
    def getJobs(self):
        for i in range(10):
            job = ("test render " + str(i), 
                1, 
                "bdeda", 
                "back then", 
                "before", 
                "later", 
                "bdeda-rd", 
                "10%", 
                "in-progress", 
                "all", 
                "3Delight Engine"
               )
            ji = JobItem(job)
            task1 = ("sub-render 1", 
                4, 
                "no one", 
                "back then", 
                "before", 
                "later", 
                "bdeda-rd", 
                "16%", 
                "in-progress", 
                "all", 
                "3Delight Engine"
               )
            task2 = ("sub-render 2", 
                4, 
                "no one", 
                "back then", 
                "before", 
                "later", 
                "bdeda-rd", 
                "16%", 
                "in-progress", 
                "all", 
                "3Delight Engine"
               )
            task3 = ("sub-render 3", 
                4, 
                "no one", 
                "back then", 
                "before", 
                "later", 
                "bdeda-rd", 
                "16%", 
                "in-progress", 
                "all", 
                "3Delight Engine"
               )
            ti1 = TaskItem(task1, ji)
            ti2 = TaskItem(task2, ji)
            ti3 = TaskItem(task3, ji)
            ji.appendChild(ti1)
            ji.appendChild(ti2)
            ji.appendChild(ti3)
            self.job_list.append(ji)
        
class TreeItem(QtGui.QTreeWidgetItem):
    def __init__(self,data,parent=None):
        QtGui.QTreeWidgetItem.__init__(self, parent)
        self.parentItem = parent
        if parent != None and issubclass(parent.__class__, TreeItem):
            parent.appendChild(self)
        self.itemData = data
        self.childItems = []
        
    #def __repr__(self):
    #    return "<TreeItem parent:%s children:%s >" % (self.parentItem, len(self.childItems))

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self,row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.itemData)
 
    def data(self,column):
        #print self.itemData
        return self.itemData[column]

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem is not None:
            return self.parentItem.childItems.index(self)
        return 0

class JobItem(TreeItem):
    "Job Item"
    
class TaskItem(TreeItem):
    "Task Item"
        
# http://www.opensubscriber.com/message/pyqt@riverbankcomputing.com/11937592.html -- example
class JobDataModel(QtCore.QAbstractItemModel):
    
    headers = ("name", "priority", "owner", "submitted", "starttime", "finishtime", 
               "origin", "progress", "status", "pool", "engine")
    
    def __init__(self, nodecache, parent=None, *args):
        QtCore.QAbstractItemModel.__init__(self, parent, *args)
        #self.arraydata = detain
        self.nodecache = nodecache
        self.rootItem = TreeItem(self.headers)
        #self.rootItem.childItems = self.arraydata
        self.setupModelData(nodecache, self.rootItem)
        #for i in self.arraydata:
        #    i.parentItem = self.rootItem
        #    self.rootItem.appendChild(i)
            
        
    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None

        if role != QtCore.Qt.DisplayRole:
            return None

        item = index.internalPointer()
        #print item, index.column(), item.data
        return item.data(index.column())

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.rootItem.data(section)

        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()
    
    def setupModelData(self, nodecache, parent):
        pass
    
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv) 
    w = JobWidget(NodeCache()) 
    w.setWindowTitle('Vineyard :: Job Widget')
    if os.path.exists('grapes.png'):
        w.setWindowIcon(QtGui.QIcon('grapes.png'))
    elif os.path.exists('gui/grapes.png'):
        w.setWindowIcon(QtGui.QIcon('gui/grapes.png'))
        
    w.show() 
    sys.exit(app.exec_()) 