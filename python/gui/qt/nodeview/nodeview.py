# Copyright 2011, Ben Deda

__doc__ = """
The nodeview module defines the basic types for nodes, connections, and their containing scene/view.
"""

from PyQt4 import QtGui, QtCore
import math, sys
from nodewidget import NodeWidget
from nodeconnection import NodeConnection
    
    
class NodeScene(QtGui.QGraphicsScene):
    """The node scene that contains all the graphical node widgets and their connections for all or part of a node graph."""
    
    # modes
    class Mode:
        Normal = 0
        Connect = 1
        Drag = 2
        Pan = 3
        Zoom = 4
        All = (Normal, Connect, Drag, Pan, Zoom)
    
    
    def __init__(self, view, menu=None, bgColor=QtGui.QColor(64, 64, 64), gridColor=QtGui.QColor(255, 255, 255, 40), gridSize=20):
        """Constructor"""
        super(NodeScene, self).__init__(view)     
        
        self.setGridColor(gridColor)
        self.setBackgroundBrush(bgColor)
        self.setGridSize(gridSize)
        self._showGrid = True
        self.line = None
        self.setModeContext(self.Mode.Normal)
        self.setSceneRect(-500, -500, 1000, 1000)        
        self.setContextMenu(menu)
        
        
    def setContextMenu(self, menu):
        if menu and isinstance(menu, QtGui.QMenu):
            self._contextMenu = menu
        else:
            self._contextMenu = None
            
            
    def contextMenu(self):
        return self._contextMenu
        
        
    def setModeContext(self, ctx):
        """
        Set the mode context and emit a signal.
        """
        if ctx not in self.Mode.All:
            raise ValueError('Invalid context for mode, must be in Mode.All')
        self._modeCtx = ctx
        self.emit(QtCore.SIGNAL('modeChanged(int)'), self._modeCtx)
        
    def modeContext(self):
        return self._modeCtx
                  
    def setGridColor(self, color):
        "Set the grid color for the scene."
        if not isinstance(color, QtGui.QColor):
            raise TypeError('color must be a QColor type!')
        self._gridColor = color
        
    def gridColor(self):
        return self._gridColor
    
    def setGridSize(self, size):
        "Set the grid size."
        size = int(size)
        self._gridSize = size
        
    def gridSize(self):
        return self._gridSize
    
    def showGrid(self, val):
        if val:
            self._showGrid = True
        else:
            self.hideGrid()
        
    def hideGrid(self):
        self._showGrid = False
        
    def drawBackground(self, painter, rect):
        super(NodeScene, self).drawBackground(painter, rect)
        
        realLeft = int(rect.left())
        realRight = int(rect.right())
        realTop = int(rect.top())
        realBottom = int(rect.bottom())
        
        firstLeft = realLeft - (realLeft % self.gridSize())
        firstTop = realTop - (realTop % self.gridSize())
        
        # draw the grid lines
        if self._showGrid:
            lines = []
            for x in range(firstLeft, realRight, self.gridSize()):
                lines.append(QtCore.QLine(x, realTop, x, realBottom))
            for y in range(firstTop, realBottom, self.gridSize()):
                lines.append(QtCore.QLine(realLeft, y, realRight, y))
        
            gridpen = QtGui.QPen(self.gridColor())
            painter.setPen(gridpen)
            painter.drawLines(lines)
        
    def mousePressEvent(self, event):
        """handle the mouse press events"""
        if self.modeContext() == self.Mode.Connect:
            self.line = QtGui.QGraphicsLineItem(QtCore.QLineF(event.scenePos(),
                                                              event.scenePos()))
            self.line.setPen(QtGui.QPen(QtCore.Qt.black, 1))
            self.addItem(self.line)

            for item in self.items():
                item.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
            # start a connection from this node output point to the mouse position
        else:
            for item in self.items():
                item.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
        super(NodeScene, self).mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        """Handle the mouse move events"""
        if self.modeContext() == self.Mode.Connect and self.line:
            newLine = QtCore.QLineF(self.line.line().p1(), event.scenePos())
            self.line.setLine(newLine)
        super(NodeScene, self).mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        """handle the mouse release events"""
        if self.modeContext() == self.Mode.Connect and self.line:
            startItems = self.items(self.line.line().p1())
            if len(startItems) and startItems[0] == self.line:
                startItems.pop(0)
            endItems = self.items(self.line.line().p2())
            if len(endItems) and endItems[0] == self.line:
                endItems.pop(0)

            self.removeItem(self.line)
            #self.line = None

            if len(startItems) and len(endItems) and \
                    isinstance(startItems[0], NodeWidget) and \
                    isinstance(endItems[0], NodeWidget) and \
                    startItems[0] != endItems[0]:
                startItem = startItems[0]
                endItem = endItems[0]
                
                #if noderegistry.ConnectNodes(startItem.node, endItem.node):
                conn = NodeConnection(startItem, endItem)
                self.addItem(conn)
                conn.update()
                #else:
                #    self.update(self.sceneRect())

        self.line = None
        super(NodeScene, self).mouseReleaseEvent(event)
        
    #def mouseDoubleClickEvent(self, event):
        #cp = noderegistry.GetCurrentPipeline()
        #super(NodeScene, self).mouseDoubleClickEvent(event)
        #items = self.items(event.scenePos())
        #if len(items) < 1:
            #noderegistry.Pop()
            
        #currentPipe = noderegistry.GetCurrentPipeline()
        #if cp != currentPipe:
            ## clear the scene and load the noderegistry.CurrentPipeline
            ##self.clear() # this deleted the c++ pointer to the widgets, so don't do this.
            #for item in list(self.items()):
                #self.removeItem(item)
            #parent = self.parent()
            #parent.LoadGraph()
                
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Control:
            self.setModeContext(self.Mode.Connect)

            
    def keyReleaseEvent(self, event):
        
        if event.key() == QtCore.Qt.Key_Control:
            self.setModeContext(self.Mode.Normal)
            
        elif event.key() == QtCore.Qt.Key_Delete:
            for item in self.selectedItems():
                if isinstance(item, NodeWidget):
                    for conn in item.inputs:
                        conn.GetSrcNode().removeOutput(item)
                        self.removeItem(conn)
                    for conn in item.outputs:
                        conn.GetDestNode().removeInput(item)
                        self.removeItem(conn)
                elif isinstance(item, NodeConnection):
                    src = item.GetSrcNode()
                    dest = item.GetDestNode()
                    if src and dest:
                        src.removeOutput(item)
                        dest.removeInput(item)
                        
                self.removeItem(item)
                   
                   
    def contextMenuEvent(self, event):
        pos = event.screenPos()            
        if self.contextMenu():
            lastItems = list(self.items())
            ret = self.contextMenu().exec_(pos)
            try:
                pos = event.scenePos()
                for item in self.items():
                    if item not in lastItems:
                        item.setPos(pos.x(), pos.y())
                        return
            except AttributeError, IndexError:
                pass
            
            
    def selectionCenter(self):
        maxpos = None
        minpos = None
        for item in self.selectedItems():
            ipos = item.pos()
            if maxpos == None:
                maxpos = (ipos.x(), ipos.y())
            else:
                maxpos = (max(ipos.x(), maxpos[0]), max(ipos.y(), maxpos[1]))
                    
            if minpos == None:
                minpos = (ipos.x(), ipos.y())
            else:
                minpos = (min(ipos.x(), minpos[0]), min(ipos.y(), minpos[1]))
        if minpos and maxpos:
            return ((maxpos[0]-minpos[0])/2, (maxpos[1]-minpos[1])/2)
        
        
class NodeView(QtGui.QGraphicsView):
    """
    A graphics view container for Node graphs
    """
    
    # used to propogate the selection item back up to main window to show the properties
    #selectionChanged = QtCore.Signal(str)
    
    def __init__(self, parent=None, menu=None):
        """Initialize and configure the look of the graphics view containing the node graphs"""
        super(NodeView, self).__init__(parent)
        
        self.setWindowTitle('Node Graph')
        self.setObjectName('NodeView')

        scene = NodeScene(self, menu)
        self.setScene(scene)
        #self.connect(scene, QtCore.SIGNAL('selectionChanged()'), self.selChanged)
        
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.setViewportUpdateMode(QtGui.QGraphicsView.BoundingRectViewportUpdate);
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.scale(0.8, 0.8)
        #self.setMinimumSize(1300, 400)
        self.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        self.resize(1200, 1200)
        
        self.setRubberBandSelectionMode(QtCore.Qt.ContainsItemShape)
        self.setDragMode(self.RubberBandDrag)
        
        
    def sizeHint(self):
        return QtCore.QSize(2000, 2000)
    
    
    def minimumSizeHint(self):
        return QtCore.QSize(400, 400)
        
        
    def loadGraph(self, graph):
        """replace the items in the scene with the graph items"""
        
        for node in graph:
            pos = node.position()
            self.AddNode(node, pos)
            
        for node in graph:
            for outputNode in node.outputs:
                # see if there is already a NodeConnection...if not, create one
                conn = None
                for inp in outputNode.inputs:
                    if inp in node.outputs:
                        conn = inp
                        break
                    
                conn = conn or NodeConnection(node, out)
                self.scene().addItem(conn)   
        self.viewport().update()
        
        
    def addNode(self, node, position=(0,0)):
        """Add a node to the scene. Create the widget if it does not already exist."""
        if not isinstance(node, NodeWidget):
            raise TypeError('node must be an instance of a NodeWidget type')
        self.scene().addItem(node)
        node.setGraphView(self)
        node.setPos(float(position[0]),float(position[1]))
        
        
    def groupSelected(self, pos=None):
        """
        Group the selected nodes into a Pipeline node. Position the pipeline node at position, if not none.
        """
        if len(self.scene().selectedItems()) <= 0:
            return
        
        if not pos:
            # try to use the selection center
            pos = self.scene().selectionCenter()
            
        if not pos:
            # otherwise use the scene center
            pos = (self.sceneRect().center().x(), self.sceneRect().center().x())
            
        ## create a pipeline node
        ## these are all the children nodes being put into the pipeline container node
        #children = [n.node for n in self.scene().selectedItems() if isinstance(n, NodeWidget)] 
        #parent = noderegistry.GetCurrentPipeline()
        ## todo: handle parent...still need to set parent in stage instances when they are added to the graph
        ## __instances__ needs to be the top level pipeline, but there should also be a pointer to the current pipeline context
        #curPipe = noderegistry.GetCurrentPipeline()
        #for child in children:
            #curPipe.RemoveChild(child)
        #pipeline = Pipeline(parent=parent, children=children)
        #noderegistry.AddInst(pipeline)
        #self.AddNode(pipeline, pos)
        #for child in children:
            #w = child.widget
            #for inp in w.inputs:
                #srcNode = inp.GetSrcNode()
                #if srcNode.node not in children:
                    #inp.SetDestNode(pipeline.widget)
                    #pipeline.widget.addInput(inp)
                    #inp.Adjust()
                #else:
                    #self.scene().removeItem(inp)
            #for out in w.outputs:
                #destNode = out.GetDestNode()
                #if destNode.node not in children:
                    #out.SetSrcNode(pipeline.widget)
                    #pipeline.widget.addOutput(out)
                    #out.Adjust()
                #else:
                    #self.scene().removeItem(out) # connections under the pipeline now
            #self.scene().removeItem(w)
            
            # remove any node connections from the scene that were between nodes that are now part of the pipeline group
            # any nodes that have connections with nodes in the group, but are outside of the group need to have their connections remapped
                
    
    def ungroupSelected(self):
        pass
        
    def scaleView(self, scaleFactor):
        """Set the scale factor of the scene"""
        factor = self.transform().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width();
        if (factor < 0.07 or factor > 100):
            return

        self.scale(scaleFactor, scaleFactor)
        
    def zoomIn(self):
        self.scaleView(1.2)

    def zoomOut(self):
        self.scaleView(1.0 / 1.2)

    def keyPressEvent(self, event):
        """handle the key press events"""
        if type(event) == QtGui.QKeyEvent:
            if event.key() == QtCore.Qt.Key_Space and not event.isAutoRepeat():
                self.setDragMode(self.ScrollHandDrag)
            elif event.key() == QtCore.Qt.Key_Control and not event.isAutoRepeat():
                self.scene().keyPressEvent(event)
            elif event.key() == QtCore.Qt.Key_Delete and not event.isAutoRepeat():
                self.scene().keyPressEvent(event)
            elif event.key() == QtCore.Qt.Key_Plus:
                self.ZoomIn()
            elif event.key() == QtCore.Qt.Key_Minus:
                self.ZoomOut()
            event.accept()
        else:
            event.ignore()
       
        
    def keyReleaseEvent(self, event):
        """handle the key release events"""
        if type(event) == QtGui.QKeyEvent:
            if event.key() == QtCore.Qt.Key_Space and not event.isAutoRepeat():
                self.setDragMode(self.NoDrag)
            elif event.key() == QtCore.Qt.Key_Control and not event.isAutoRepeat():
                self.scene().keyReleaseEvent(event)
            elif event.key() == QtCore.Qt.Key_Delete and not event.isAutoRepeat():
                self.scene().keyReleaseEvent(event)
            event.accept()
        else:
            event.ignore()
        
        
    def selectedItems(self):
        return self.scene().selectedItems()
        
                
    def leaveEvent(self, event):
        self.scene().setModeContext(NodeScene.Mode.Normal)
        
        
    def removeAllItems(self):
        for item in list(self.scene().items()):
            self.scene().removeItem(item)
            
            
class NodeViewWidget(QtGui.QWidget):
    
    def __init__(self, parent=None, menu=None):
        super(NodeViewWidget, self).__init__(parent)
        
        self.setObjectName('NodeViewWidget')
        
        vbox = QtGui.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        self.view = NodeView(self, menu)
        vbox.addWidget(self.view)
        self.setLayout(vbox)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.connect(self.view.scene(), QtCore.SIGNAL('selectionChanged()'), lambda: self.emit(QtCore.SIGNAL('selectionChanged()')))
        self._nextNodeIndex = 0
        
    def selectedNodes(self):
        "Return a list of the selected nodes in the scene."
        ret = []
        for node in self.view.scene().selectedItems():
            if isinstance(node, NodeWidget):
                ret.append(node)
        return ret
    
    def nodes(self):
        "Return a list of the nodes in the scene."
        ret = []
        for node in self.view.scene().items():
            if isinstance(node, NodeWidget):
                ret.append(node)
        return ret
        
    def sizeHint(self):
        return QtCore.QSize(2000, 2000)
    
    def addNode(self, node):
        self.view.addNode(node)
        self._nextNodeIndex += 1
        
    def nextNodeIndex(self):
        return self._nextNodeIndex
        
    def connectNodes(self, node1, node2):
        pass
        
    def groupSelected(self):
        self.view.groupSelected()
    
    def ungroupSelected(self):
        self.view.ungroupSelected()
        
    def loadGraph(self, graph):
        self.view.loadGraph(graph)
        
    def removeAllItems(self):
        self.view.removeAllItems()
        
    def setContextMenu(self, menu):
        if not isinstance(menu, QtGui.QMenu):
            raise TypeError('menu must be a QMenu instance')
    
    
if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)    
    w = NodeViewWidget()    
    w.setWindowTitle('Node scene test')
    
    def selectionChanged():
        for node in w.selectedNodes():
            print node.title()
    w.connect(w, QtCore.SIGNAL('selectionChanged()'), selectionChanged)
            
    def addNodetoScene():
        node = NodeWidget('test_%i' % w.nextNodeIndex())
        w.addNode(node)
    
    for i in range(10):
        addNodetoScene()
    
    w.show()
    
    sys.exit(app.exec_())