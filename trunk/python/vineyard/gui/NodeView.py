#!/usr/bin/python

import sys, operator, os
from PyQt4 import QtGui, QtCore
from vineyard.WakeOnLan import wake_on_lan
from vineyard.FarmManager import NodeCache
from vineyard.models import WorkerNode
#from renderfarm.gui.Validators import IPAddressValidator, MACAddressValidator

class AddNodeDialog(QtGui.QDialog):
    def __init__(self, *args):
        QtGui.QDialog.__init__(self, *args)
        
        vbox = QtGui.QVBoxLayout(self)
        self.center()
        self.setWindowTitle('Add Node')
        if os.path.exists('grapes.png'):
            self.setWindowIcon(QtGui.QIcon('grapes.png'))
        elif os.path.exists('gui/grapes.png'):
            self.setWindowIcon(QtGui.QIcon('gui/grapes.png'))
        
        
        grid = QtGui.QGridLayout()
        nameLabel = QtGui.QLabel("Name", self)
        nameField = QtGui.QLineEdit(self)
        grid.addWidget(nameLabel, 0, 0, QtCore.Qt.AlignRight)
        grid.addWidget(nameField, 0, 1)
        
        ipregex = QtCore.QRegExp("\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")
        ipvalidator = QtGui.QRegExpValidator(ipregex, self)

        ipLabel = QtGui.QLabel("IP Address", self)
        ipField = QtGui.QLineEdit(self)
        grid.addWidget(ipLabel, 1, 0, QtCore.Qt.AlignRight)
        grid.addWidget(ipField, 1, 1)
        
        macregex = QtCore.QRegExp("[0-9a-f]{2}[:-][0-9a-f]{2}[:-][0-9a-f]{2}[:-][0-9a-f]{2}[:-][0-9a-f]{2}[:-][0-9a-f]{2}")
        macvalidator = QtGui.QRegExpValidator(macregex, self)
        
        macLabel = QtGui.QLabel("MAC Address", self)
        macField = QtGui.QLineEdit(self)
        grid.addWidget(macLabel, 2, 0, QtCore.Qt.AlignRight)
        grid.addWidget(macField, 2, 1)
        vbox.addLayout(grid)
        
        okCancel = QtGui.QDialogButtonBox(self)
        okCancel.setOrientation(QtCore.Qt.Horizontal)
        okCancel.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        
        okbtn = okCancel.button(QtGui.QDialogButtonBox.Ok)
        okbtn.setDisabled(True)
        
        vbox.addStretch(1)
        vbox.addWidget(okCancel)
        
        self.setLayout(vbox)
        
        self.connect(okCancel,  QtCore.SIGNAL('accepted()'), self.addNode )
        self.connect(okCancel,  QtCore.SIGNAL('rejected()'), self, QtCore.SLOT('close()') )
        
    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
        
    def addNode(self):
        print 'changes applied'
        self.close()
        

class NodeView(QtGui.QWidget):
    """container class for placing table into a dock widget"""
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        layout = QtGui.QVBoxLayout()
        table = NodeTableView(self)
        layout.addWidget(table)
        layout.setMargin(2)
        self.setLayout(layout)

class NodeTableView(QtGui.QTableView):
    
    def __init__(self, *args):
        QtGui.QTableView.__init__(self, *args)
        
        self.nodeCache = NodeCache()
        
        #self.nodeCache.onUpdate = self.updateView
        
        self._headers = ['name', 'mac address', 'ip address', 'status', 'platform', 'pools', 'version', 'cpus', 'priority', 'engines']          

        #print 'in NodeTableView, nodes len=', len(self.nodeCache.nodes)
        
        self.dataModel = NodeTableModel(self.nodeCache.nodes, self._headers, self)        
        self.setModel(self.dataModel)
        
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        vh = self.verticalHeader()
        vh.setVisible(False)        
        #self.setMinimumSize(400, 300)
        #self.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
        #self.horizontalStretch(True)
        self.setSortingEnabled(True)
        self.setShowGrid(True)
        self.setAlternatingRowColors(True)
        #print self.sizeHint()
        
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.connect(self, QtCore.SIGNAL("customContextMenuRequested(const QPoint &)"), self.showContextMenu) 
        
        self.timer = QtCore.QTimer()
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.onUpdate)
        self.timer.start(1000)
  
       
    def showContextMenu(self, pos):
        idx = self.indexAt(pos)
        if not idx.isValid():
            return

        idxs = self.selectedIndexes()
        
        mac_addresses = []
        machineIds = []
        
        for i in idxs:
            # to support multi-select starting, need to make this an array of all selected and offline machines
            ma = 2 # this might get changed, find the real value...
            for j in range(len(self._headers)):
                if self._headers[j] == 'mac address':
                    ma = j
                    break
            sa = 4
            for k in range(len(self._headers)):
                if self._headers[k] == 'status':
                    sa = k
                    break
            mac_address = idx.sibling(i.row(), ma).data().toString()
            status = idx.sibling(i.row(), sa).data().toString()
            #if status == 'offline':
            mac_addresses.append(mac_address)
        
        menu = QtGui.QMenu(self)
        add_machine = QtGui.QAction("Add Node", self)
        menu.addAction(add_machine)            
        self.connect(add_machine, QtCore.SIGNAL('triggered()'), self.addNode)
            
        if len(mac_addresses) > 0:
            
            lbl = 'Start Machine'
            lbl2 = "Remove Machine"
            if len(mac_addresses) > 1:
                lbl += 's'
                lbl2 += 's'
                
            start_machine = QtGui.QAction(lbl, self)
            menu.addAction(start_machine)            
            startMach = lambda: self.startMachines(mac_addresses)            
            self.connect(start_machine, QtCore.SIGNAL('triggered()'), startMach)      
            
            remove_machine = QtGui.QAction(lbl2, self)
            menu.addAction(remove_machine)            
            removeMach = lambda: self.removeMachines(mac_addresses)
            self.connect(remove_machine, QtCore.SIGNAL('triggered()'), removeMach)
            
        menu.popup(QtGui.QCursor.pos()) 
            
    def startMachines(self, macAddresses):
        for machine in macAddresses:
            print 'starting machine', str(machine)
            wake_on_lan(str(machine))
            
    def removeMachines(self, macAddresses):
        for ma in macAddresses:
            self.nodeCache.removeMachine(str(ma))
            
        # update the data model
        self.dataModel = NodeTableModel(self.nodeCache.nodes, self._headers, self)        
        self.setModel(self.dataModel)
        
    def addNode(self):
        ad = AddNodeDialog()
        ad.setModal(True)
        ad.exec_()
        
    def onUpdate(self):
        # update the data model
        self.nodeCache.update()
        
        self.dataModel = NodeTableModel(self.nodeCache.nodes, self._headers, self)        
        self.setModel(self.dataModel)
        

class NodeTableModel(QtCore.QAbstractTableModel):
    def __init__(self, datain, headerdata, parent=None, *args): 
        """ datain: a list of lists
            headerdata: a list of strings
        """
        QtCore.QAbstractTableModel.__init__(self, parent, *args) 
        self.arraydata = datain
        self.headerdata = headerdata
 
    def rowCount(self, parent): 
        return len(self.arraydata) 
 
    def columnCount(self, parent): 
        if self.arraydata and len(self.arraydata) > 0:
            return len(self.arraydata[0]) 
        else:
            return 0
 
    def data(self, index, role): 
        if not index.isValid(): 
            return QtCore.QVariant() 
         

        elif role == QtCore.Qt.BackgroundRole:
            if index.column() == 3:
                stat_data = index.sibling(index.row(), 3).data()
                stat_val = stat_data.toString() 
            
                if stat_val == 'waiting':
                    return QtCore.QVariant(QtGui.QBrush(QtCore.Qt.green)) 
                elif stat_val == 'busy':
                    return QtCore.QVariant(QtGui.QBrush(QtCore.Qt.yellow))
                elif stat_val == 'initializing':
                    return QtCore.QVariant(QtGui.QBrush(QtCore.Qt.white))
                else:
                    return QtCore.QVariant(QtGui.QBrush(QtCore.Qt.red))
                
        elif role == QtCore.Qt.ForegroundRole:
            if index.column() == 4:
                stat_data = index.sibling(index.row(), 4).data()
                stat_val = stat_data.toString()
                
                if stat_val == 'waiting':
                    return QtCore.QVariant(QtGui.QBrush(QtCore.Qt.black))
                else:
                    return QtCore.QVariant(QtGui.QBrush(QtCore.Qt.black))
                
        elif role != QtCore.Qt.DisplayRole: 
            return QtCore.QVariant()
        
        return QtCore.QVariant(self.arraydata[index.row()][index.column()]) 

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.headerdata[col])
        return QtCore.QVariant()

    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self.arraydata = sorted(self.arraydata, key=operator.itemgetter(Ncol))        
        if order == QtCore.Qt.DescendingOrder:
            self.arraydata.reverse()
        self.emit(QtCore.SIGNAL("layoutChanged()"))
        
###########################################################################################
##
##    view delegates
##
###########################################################################################
        
class StatusDelegate(QtGui.QStyledItemDelegate):
    
    def __init__(self, *args):
        QtGui.QStyledItemDelegate.__init__(self, *args)
        
    def paint(self, painter, option, index):
        model = index.model()
        record = model.record(index.row())
        value= record.value(2).toPyObject()
        if value:
            painter.save()

            if option.state & QtGui.QStyle.State_Selected:
                painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
                painter.setBrush(QtGui.QApplication.palette().highlight())
                painter.drawRect(option.rect)
                painter.restore()
                painter.save()
                font = painter.font
                pen = painter.pen()
                pen.setColor(QtGui.QApplication.palette().color(QtGui.QPalette.HighlightedText))
                painter.setPen(pen)
            else:
                painter.setPen(QtGui.QPen(QtCore.Qt.black))

            # set text bold
            font = painter.font()
            font.setWeight(QtCore.QFont.Bold)
            painter.setFont(font)
            text = record.value(1).toPyObject()
            painter.drawText(option.rect, QtCore.Qt.AlignLeft, text)

            
            painter.restore()
        else:
            QtGui.QStyledItemDelegate.paint(self, painter, option, index)
            
    #def sizeHint(self, option, mi):
    #    dg = self.delegateForIndex(mi)
    #    return dg.sizeHint(option, mi)



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv) 
    w = NodeView() 
    w.setWindowTitle('Vineyard :: Node View')
    if os.path.exists('grapes.png'):
        w.setWindowIcon(QtGui.QIcon('grapes.png'))
    elif os.path.exists('gui/grapes.png'):
        w.setWindowIcon(QtGui.QIcon('gui/grapes.png'))
        
    w.show() 
    sys.exit(app.exec_()) 
