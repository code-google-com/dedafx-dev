#!/usr/bin/python

import sys, operator
from PyQt4 import QtGui, QtCore

class NodeTableView(QtGui.QTableView):
    def __init__(self, *args):
        QtGui.QTableView.__init__(self, *args)
        
        self._data = [
            ['joe-renderer',10, '192.168.0.101','00abcdef3322','waiting','win64','','1.0.0','2','1',''],
            ['bob-renderer',10, '192.168.0.102','00abcdef3323','busy','linux64','','1.0.0','2','1',''],
            ['sam-renderer',10, '192.168.0.103','00abcdef3324','offline','linux32','','1.0.0','2','1',''],
            ['joe-renderer',10, '192.168.0.101','00abcdef3322','busy','win64','','1.0.0','2','1',''],
            ['bob-renderer',10, '192.168.0.102','00abcdef3323','offline','linux64','','1.0.0','2','1',''],
            ['sam-renderer',10, '192.168.0.103','00abcdef3324','offline','linux32','','1.0.0','2','1',''],
            ['joe-renderer',10, '192.168.0.101','00abcdef3322','waiting','win64','','1.0.0','2','1',''],
            ['bob-renderer',10, '192.168.0.102','00abcdef3323','busy','linux64','','1.0.0','2','1',''],
            ['sam-renderer',10, '192.168.0.103','00abcdef3324','offline','linux32','','1.0.0','2','1',''],
            ['joe-renderer',10, '192.168.0.101','00abcdef3322','waiting','win64','','1.0.0','2','1',''],
            ['bob-renderer',10, '192.168.0.102','00abcdef3323','waiting','linux64','','1.0.0','2','1',''],
            ['sam-renderer',10, '192.168.0.103','00abcdef3324','offline','linux32','','1.0.0','2','1',''],
            ['joe-renderer',10, '192.168.0.101','00abcdef3322','waiting','win64','','1.0.0','2','1',''],
            ['bob-renderer',10, '192.168.0.102','00abcdef3323','busy','linux64','','1.0.0','2','1',''],
            ['sam-renderer',10, '192.168.0.103','00abcdef3324','offline','linux32','','1.0.0','2','1',''],
            ['joe-renderer',10, '192.168.0.101','00abcdef3322','waiting','win64','','1.0.0','2','1',''],
            ['bob-renderer',10, '192.168.0.102','00abcdef3323','waiting','linux64','','1.0.0','2','1',''],
            ['sam-renderer',10, '192.168.0.103','00abcdef3324','offline','linux32','','1.0.0','2','1',''],
                 ]
        self._headers = ['name', 'id', 'ip address', 'mac address', 'status', 'platform', 'pools', 'version', 'cpus', 'priority', 'engines']
        
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

        item = self.itemAt(idx)
        name = item.text(0)

        menu = QtGui.QMenu(self)

        menu.addAction('start machine')

        menu.popup(QtGui.QCursor.pos()) 

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
        return len(self.arraydata[0]) 
 
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
    w.show() 
    sys.exit(app.exec_()) 
