#!/usr/bin/python

import sys, operator
from PyQt4 import QtGui, QtCore
from renderfarm.WakeOnLan import wake_on_lan
from renderfarm.FarmManager import NodeCache
from renderfarm.models import WorkerNode

class NodeTableView(QtGui.QTableView):
    def __init__(self, *args):
        QtGui.QTableView.__init__(self, *args)
        
        self.nodeCache = NodeCache()
        
        # temp data, should query the local db cache
        #self._data = self.nodeCache.nodes
        self._data = [
            ['joe-renderer',10, '192.168.0.101','00abcdef3321','waiting','win64','','1.0.0','2','1',''],
            ['bob-renderer',10, '192.168.0.102','00abcdef3322','busy','linux64','','1.0.0','2','1',''],
            ['sam-renderer',10, '192.168.0.103','00abcdef3323','offline','linux32','','1.0.0','2','1',''],
            ['joe-renderer',10, '192.168.0.104','00abcdef3324','busy','win64','','1.0.0','2','1',''],
            ['bob-renderer',10, '192.168.0.105','00abcdef3325','offline','linux64','','1.0.0','2','1',''],
            ['sam-renderer',10, '192.168.0.106','00abcdef3326','offline','linux32','','1.0.0','2','1',''],
            ['joe-renderer',10, '192.168.0.107','00abcdef3327','waiting','win64','','1.0.0','2','1',''],
            ['bob-renderer',10, '192.168.0.108','00abcdef3328','busy','linux64','','1.0.0','2','1',''],
            ['sam-renderer',10, '192.168.0.109','00abcdef3329','offline','linux32','','1.0.0','2','1',''],
            ['joe-renderer',10, '192.168.0.110','00abcdef332a','waiting','win64','','1.0.0','2','1',''],
            ['bob-renderer',10, '192.168.0.111','00abcdef332b','waiting','linux64','','1.0.0','2','1',''],
            ['sam-renderer',10, '192.168.0.112','00abcdef332c','offline','linux32','','1.0.0','2','1',''],
            ['joe-renderer',10, '192.168.0.113','00abcdef332d','waiting','win64','','1.0.0','2','1',''],
            ['bob-renderer',10, '192.168.0.114','00abcdef332e','busy','linux64','','1.0.0','2','1',''],
            ['sam-renderer',10, '192.168.0.115','00abcdef332f','offline','linux32','','1.0.0','2','1',''],
            ['joe-renderer',10, '192.168.0.116','00abcdef3330','waiting','win64','','1.0.0','2','1',''],
            ['bob-renderer',10, '192.168.0.117','00abcdef3331','waiting','linux64','','1.0.0','2','1',''],
            ['sam-renderer',10, '192.168.0.118','00abcdef3332','offline','linux32','','1.0.0','2','1',''],
                 ]
        self._headers = ['name', 'id', 'ip address', 'mac address', 'status', 'platform', 'pools', 'version', 'cpus', 'priority', 'engines']
        #self._headers = []
        #for attr in dir(WorkerNode):
        #    if attr.find('_') != 0 and attr.find('metadata') != 0:
        #        self._headers.append(attr)            
        
        self.dataModel = NodeTableModel(self._data, self._headers, self)        
        self.setModel(self.dataModel)
        
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        vh = self.verticalHeader()
        vh.setVisible(False)        
        self.setMinimumSize(400, 300)
        self.setSortingEnabled(True)
        self.setShowGrid(True)
        self.setAlternatingRowColors(True)
        
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.connect(self, QtCore.SIGNAL("customContextMenuRequested(const QPoint &)"), self.showContextMenu) 
        
    def updateData(self):
        self._data
        
    def showContextMenu(self, pos):
        idx = self.indexAt(pos)
        if not idx.isValid():
            return

        idxs = self.selectedIndexes()
        print idxs
        
        mac_addresses = []
        machineIds = []
        
        for i in idxs:
            # to support multi-select starting, need to make this an array of all selected and offline machines
            mac_address = idx.sibling(i.row(), 3).data().toString()
            status = idx.sibling(i.row(), 4).data().toString()
            if status == 'offline':
                mac_addresses.append(mac_address)
        
        if len(mac_addresses) > 0:
            menu = QtGui.QMenu(self)
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
        pass

    def getCachedData(self):
        nodes = []
        
        return nodes

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
            if index.column() == 4:
                stat_data = index.sibling(index.row(), 4).data()
                stat_val = stat_data.toString() 
            
                if stat_val == 'waiting':
                    return QtCore.QVariant(QtGui.QBrush(QtCore.Qt.yellow)) 
                elif stat_val == 'busy':
                    return QtCore.QVariant(QtGui.QBrush(QtCore.Qt.green))
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
    w = NodeTableView() 
    w.setWindowTitle('Vinyard :: Node View')
    w.setWindowIcon(QtGui.QIcon('grapes.png'))
    w.show() 
    sys.exit(app.exec_()) 
