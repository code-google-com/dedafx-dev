# Copyright 2011, Ben Deda

__doc__ = """
The nodewidget module defines the basic type for node graphic items.
"""

from PyQt4 import QtGui, QtCore
import math, sys


class NodeWidget(QtGui.QGraphicsWidget):
    """
    The NodeWidget class provides the graphical widget drawing and controls used by all node widget types.
    """

    def __init__(self, title, graphview=None, userData=None, color=None, 
                 selectedColor=None, shadowColor=None, outlineColor=None):
        """Constructor"""
        super(NodeWidget, self).__init__()
        
        self.setTitle(title)
        self.setUserData(userData)
        
        self.cornerRadius = 5
        self.shadowOffset = QtCore.QPointF(5., 5.)
        
        self.graph = graphview
        
        self.setColor(color or QtGui.QColor(128, 128, 128, 255))
        self.setSelectedColor(selectedColor or QtGui.QColor(255, 255, 128, 255))
        self.setShadowColor(shadowColor or QtGui.QColor(0, 0, 0, 60))
        self.setOutlineColor(outlineColor or QtGui.QColor(0,0,0,255))
        
        # these are the actual line connection items in the graph view
        self.inputs = set()
        self.outputs = set()
        
        self.draggingConnection = None
            
        self.w = 120
        self.h = 25 
        self.resize(self.w, self.h)
        
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setZValue(1)
        
        self.font = QtGui.QFont("SansSerif", 11)
        self.font.setLetterSpacing(QtGui.QFont.AbsoluteSpacing, 0.8)
        
        
    def setColor(self, color):
        "Set the unselected color of the node."
        if not isinstance(color, QtGui.QColor):
            raise TypeError('color must be of type QColor')
        self._color = color
        
        
    def color(self):
        return self._color
        
        
    def setTitle(self, title):
        "Set the title of the node"
        if not isinstance(title, basestring):
            raise TypeError('title must be a string')
        self._title = title
        
        
    def title(self):
        if hasattr(self, '_title'):
            return self._title
        
        
    def setSelectedColor(self, color):
        if not isinstance(color, QtGui.QColor):
            raise TypeError('color must be a type or QColor')
        self._selectedColor = color
        
        
    def selectedColor(self):
        return self._selectedColor
    
    
    def setShadowColor(self, color):
        if not isinstance(color, QtGui.QColor):
            raise TypeError('color must be a type or QColor')
        self._shadowColor = color
        
        
    def shadowColor(self):
        return self._shadowColor
    
    
    def setOutlineColor(self, color):
        if not isinstance(color, QtGui.QColor):
            raise TypeError('color must be a type or QColor')
        self._outlineColor = color
        
        
    def outlineColor(self):
        return self._outlineColor
        
        
    def setGraphView(self, graphview):
        self.graph = graphview
    
    
    def setUserData(self, data):
        self._userData = data
        
        
    def getUserData(self):
        return self._userData
                
                
    def addInput(self, edge):
        self.inputs.add(edge)
            
            
    def removeInput(self, edge):
        self.inputs.remove(edge)
        
        
    def addOutput(self, edge):
        self.outputs.add(edge)
            
            
    def removeOutput(self, edge):
        self.outputs.remove(edge)
        
        
    def inputConnectionPoint(self):
        r = self.rect()
        cx = r.x() + 0.5 * r.width()
        return QtCore.QPointF(cx, r.y())
    
    
    def inputRect(self):
        p = self.inputConnectionPoint()
        return QtCore.QRectF(p.x()-5, p.y()-5, 10, 10)
    
    
    def outputConnectionPoint(self):
        r = self.rect()
        cx = r.x() + 0.5 * r.width()
        return QtCore.QPointF(cx, r.y() + r.height()) 
    
    
    def outputRect(self):
        p = self.outputConnectionPoint()
        return QtCore.QRectF(p.x()-5, p.y()-5, 10, 10)
        
        
    def paint(self, painter, option, widget=0):
        """paint this node"""
        super(NodeWidget, self).paint(painter, option, widget)
        
        painter.setFont(self.font)
        
        fm = painter.fontMetrics()
        br = fm.boundingRect(self.title())        
        
        x = self.rect().x()
        y = self.rect().y()
        w = max(self.w, br.width() + 20)
        h = self.rect().height()
        self.resize(w, h)
        
        px = (w - (br.width()))/2
        py = (h + br.height())/2 - 2
        
        # draw shadow
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(self.shadowColor()))
        painter.drawRoundedRect(x + self.shadowOffset.x(), y + self.shadowOffset.y(), w, h, self.cornerRadius, self.cornerRadius)
        
        # draw node
        painter.setPen(self.outlineColor())
        if self.isSelected():
            painter.setBrush(QtGui.QBrush(self.selectedColor()))
        else:
            painter.setBrush(QtGui.QBrush(self.color()))        
        painter.drawRoundedRect(x, y, w, h, self.cornerRadius, self.cornerRadius)
        
        # draw text
        painter.drawText(px, py, self.title())
        
                
    def boundingRect(self):
        return QtCore.QRectF(self.rect().x(), self.rect().y()-5, self.rect().width()+5, self.rect().height()+10)
    
    
    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionHasChanged:
            for edge in self.inputs:
                edge.Adjust()
            for edge in self.outputs:
                edge.Adjust()
                
        elif change == QtGui.QGraphicsItem.ItemSelectedHasChanged:
            if self.isSelected():
                pass

        return super(NodeWidget, self).itemChange(change, value)
    
    
    def mousePressEvent(self, event):
        self.update()
        super(NodeWidget, self).mousePressEvent(event)
        
        
    def mouseMoveEvent(self, event):
        if self.draggingConnection:
            self.draggingConnection.SetDestPoint(event.pos())
        self.update()
        super(NodeWidget, self).mouseMoveEvent(event)
        
        
    def mouseReleaseEvent(self, event):
        if self.draggingConnection:
            self.graph.scene().removeItem(self.draggingConnection)
            self.draggingConnection = None
        self.update()
        super(NodeWidget, self).mouseReleaseEvent(event)

        
    #def mouseDoubleClickEvent(self, event):
    #    if isinstance(self.node, Pipeline):
    #        noderegistry.Push(self.node.guid)
    #        event.accept()