# Copyright 2011, Ben Deda

__doc__ = """
The node connection module defines the basic type for node connections.
"""

from PyQt4 import QtGui, QtCore
import math, sys

class NodeConnection(QtGui.QGraphicsItem):
    """
    Class for drawing connections between node inputs and outputs
    """
    
    def __init__(self, srcNode, destNode):
        """Constructor
        
        A Node connection is a curved line between two nodes, the srcNode and the destNode.
        
        a destNode can be a proxy item that is invisible, but is following 
        """
        super(NodeConnection, self).__init__()
        
        self.setSrcNode(srcNode)
        self.setDestNode(destNode)
        
        self._srcPt = None
        self._destPt = None
        self.setArrowSize(10)
        
        self.Adjust()
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        
        
    def setDestPoint(self, point):
        if not isinstance(point, QtCore.QPointF):
            raise TypeError('point must be of type QPointF')
        self._destPt = point
        
        
    def destPt(self):
        return self._destPt
    

    def setSrcPoint(self, point):
        if not isinstance(point, QtCore.QPointF):
            raise TypeError('point must be of type QPointF')
        self._srcPt = point
    
    
    def srcPt(self):
        return self._srcPt
        
        
    def setDestNode(self, node):
        #if not isinstance(node, NodeWidget):
        #    raise TypeError('Must be an instance of NodeWidget')
        self._destNode = node
        self._destNode.addInput(self)
        
        
    def destNode(self):
        return self._destNode
        
        
    def setSrcNode(self, node):
        #if not isinstance(node, NodeWidget):
        #    raise TypeError('Must be an instance of NodeWidget')
        self._srcNode = node
        self._srcNode.addOutput(self)
        
        
    def srcNode(self):
        return self._srcNode
    
    
    def setArrowSize(self, size):
        self._arrowSize = int(size)
        
        
    def arrowSize(self):
        return self._arrowSize
        
        
    def Adjust(self):
        """
        Recalculate the src and dest positions used in painting this connection
        
        This will mutate the srcPt and destPt using the positions of the in and out connection points
        of the srcNode and destNode
        """
        if not self.srcNode() or not self.destNode():
            return   

        self.prepareGeometryChange()

        self.setSrcPoint(self.mapFromItem(self.srcNode(), self.srcNode().outputConnectionPoint()))
        self.setDestPoint(self.mapFromItem(self.destNode(), self.destNode().inputConnectionPoint()))
        
        
    def _getPointList(self):
        points = []
        points.append(self.srcPt())
        
        # center point
        dx = min(self.destPt().x(), self.srcPt().x()) + abs(self.destPt().x() - self.srcPt().x()) / 2 
        dy = min(self.destPt().y(), self.srcPt().y()) + abs(self.destPt().y() - self.srcPt().y()) / 2         
        
        ssy = self.srcPt().y() + self.srcNode().rect().height()
        ddy = self.destPt().y() - self.destNode().rect().height()
        
        deltax = (self.destPt().x() - self.srcPt().x()) / 4
        deltay = (ddy - ssy) / 4 
        
        points.append(QtCore.QPointF(self.srcPt().x(), ssy))
        if ssy > ddy:
            points.append(QtCore.QPointF(dx-deltax, ssy))
            points.append(QtCore.QPointF(dx, max(ssy, dy)))
        points.append(QtCore.QPointF(dx, dy))        
        if ssy > ddy:            
            points.append(QtCore.QPointF(dx, min(ddy, dy)))
            points.append(QtCore.QPointF(dx+deltax, ddy))
        points.append(QtCore.QPointF(self.destPt().x(), ddy))
        
        points.append(self.destPt())
        return points
    
    
    def _getPath(self):
        path = QtGui.QPainterPath()
        points = self._getPointList()
        if len(points) > 3:
            path.moveTo(points[0])
            for i in range(1, len(points)-1, 2):
                path.quadTo(points[i].x(), points[i].y(), points[i+1].x(), points[i+1].y())
        return path
    
    
    def _getArrow(self):
        points = self._getPointList()
        p1 = points[-3]
        p2 = points[-2]
        l = QtCore.QLineF(p1, p2)
        p3 = QtCore.QPointF(p1.x() + 0.92*l.dx(), p1.y() + 0.92*l.dy())
        line = QtCore.QLineF(p3, self.destPt())
        
        if QtCore.qFuzzyCompare(line.length(), 0.):
            return QtGui.QPolygonF()
        
        angle = math.acos(line.dx() / line.length())
        if (line.dy() >= 0):
            angle = (math.pi * 2) - angle
    
        destArrowP1 = self.destPt() + QtCore.QPointF(math.sin(angle - math.pi / 3) * self.arrowSize(),
                                              math.cos(angle - math.pi / 3) * self.arrowSize())
        destArrowP2 = self.destPt() + QtCore.QPointF(math.sin(angle - math.pi + math.pi / 3) * self.arrowSize(),
                                              math.cos(angle - math.pi + math.pi / 3) * self.arrowSize())
            
        p = QtGui.QPolygonF()
        p.append(self.destPt())
        p.append(destArrowP1)
        p.append(destArrowP2)
        return p
    
        
    def paint(self, painter, options, widget=0):
        if not self.srcNode() or not self.destNode():
            return

        line = QtCore.QLineF(self.srcPt(), self.destPt())
        if QtCore.qFuzzyCompare(line.length(), 0.):
            return # dont paint a connection that is roughly 0 units in length

        clr = QtCore.Qt.black
        if self.isSelected():
            clr = QtCore.Qt.yellow
        painter.setPen(QtGui.QPen(clr, 1, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.setBrush(QtCore.Qt.NoBrush)
        
        path = self._getPath()
        arrow = self._getArrow()
        
        painter.drawPath(path)
        painter.setBrush(clr)
        painter.drawPolygon(arrow)

        
    def boundingRect(self):
        points = self._getPointList()
        left = points[0].x()
        right = points[0].x()
        top = points[0].y()
        bottom = points[0].y()
        for pt in points[1:]:
            left = min(pt.x(), left)            
            right = max(pt.x(), right)
            top = min(pt.y(), top)
            bottom = max(pt.y(), bottom)
        return QtCore.QRectF(left, top, right-left, bottom-top)
    
    
    def mousePressEvent(self, event):
        rect = QtCore.QRectF(event.pos().x()-2, event.pos().y()-2, 5, 5)
        path = self._getPath()
        rectItem = QtGui.QGraphicsRectItem(rect)
        if rectItem.collidesWithPath(path):
            self.setSelected(not self.isSelected())
            event.accept()
        else:
            self.setSelected(False)
            event.ignore()
        
        
    def mouseReleaseEvent(self, event):
        rect = QtCore.QRectF(event.pos().x()-2, event.pos().y()-2, 5, 5)
        path = self._getPath()
        rectItem = QtGui.QGraphicsRectItem(rect)
        if rectItem.collidesWithPath(path):
            event.accept()
        else:
            event.ignore()
        
