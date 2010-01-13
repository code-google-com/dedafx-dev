import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Node(QGraphicsItem):
    """
    This is the simple base class of all nodes. This does nothing, and is essentially a null item, 
    but has properties which make it visible in the graphics scene in the gui.
    """    
    def __init__(self, name, parent=None, scene=None):
        QGraphicsItem.__init__(self, parent, scene)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.name = str(name)
        self.inputs = []
        self.outputs = [] # usually only one output, but made into an array for forward compatability
        
    def boundingRect(self):
        return QRectF(0,0,60,16)
    
    def paint(self, painter, style, widget):
        lg = QLinearGradient(30,0,30,16)
        lg.setColorAt(0,QColor(180,180,180))
        lg.setColorAt(1,QColor(100,100,100))
        brush = QBrush(lg)
        painter.setBrush(brush)
        if self.isSelected():
            pen = QPen(QColor(220,20,20))
            pen.setWidth(2)
            painter.setPen(pen)
        else:
            painter.setPen(QColor(20,20,20))
        painter.drawRect(0,0,60,16)
        painter.setPen(QColor(255,255,255))
        painter.drawText(self.boundingRect(), Qt.AlignCenter, self.name)
        
    def mousePressEvent(self, evt):
        if evt.buttons() == Qt.RightButton:
            print 'right button pressed on node'
        QGraphicsItem.mousePressEvent(self, evt)
        #evt.ignore()
        
        
class NodeView(QGraphicsView):
    
    def __init__(self, parent=None):
        QGraphicsView.__init__(self, parent)
        self.zooming = False
        self.initialPos = 0
        
        #self.view = QGraphicsView()
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        brush = QBrush(QColor(80,80,80))
        self.setBackgroundBrush(brush)
        #layout = QHBoxLayout()
        #layout.addWidget(self.view, 1)
        #self.setLayout(layout)
        
        self.createScene()
        
    def createScene(self):
        self.scene = QGraphicsScene()
        self.setScene(self.scene)      
        self.update()
        
    def addNode(self, node):
        self.scene.addItem(node)
        self.update()
        
    def removeNode(self, node):
        self.scene.removeNode(node)
        self.update()
        
    def mouseReleaseEvent(self, evt):
        self.zooming = False
        self.initialPos = 0
        QGraphicsView.mouseReleaseEvent(self, evt)
        
    def mousePressEvent(self, evt):
        if evt.buttons() == Qt.RightButton:
            self.zooming = True
            self.initialPos = evt.y()
        else:
            QGraphicsView.mousePressEvent(self, evt)
        
    def mouseMoveEvent(self, evt):
        if self.zooming:
            
            scale = self.initialPos - evt.y()
            
            if scale > 0:
                self.zoomIn()
            if scale < 0:
                self.zoomOut()
                
            self.initialPos = evt.y()
        QGraphicsView.mouseMoveEvent(self, evt)
        
    def zoomIn(self):
        self.scale(1.1,1.1)
        
    def zoomOut(self):
        self.scale(1.0/1.1,1.0/1.1)
        
def main():
    app = QApplication(sys.argv)
    window = NodeView()
    window.addNode(Node("node01"))
    window.addNode(Node("node02"))
    window.show()
    sys.exit(app.exec_())
        
if __name__ == "__main__":
    main()
    