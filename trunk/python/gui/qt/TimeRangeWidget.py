from PyQt4 import QtGui, QtCore

class RangeSliderButton(QtGui.QWidget):
    def __init__(self, parent=None, width=18, bSizer=True):
        QtGui.QWidget.__init__(self, parent)
        self.__width = width
        # this value is updated for the bar, where the two ends have been slid to change this value
        #self.rangePercent =  100.0
        self.bSizer = bSizer
        if bSizer:
            self.setMinimumSize(width,7)
            self.setMaximumSize(width,7)
            self.setFixedSize(width, 7)
            self.setSizePolicy(0, 0)
        
            self.setCursor(QtCore.Qt.SizeHorCursor)
        
    def paintEvent(self, evt):
        if not self.bSizer:
            print 'RangeSliderButton paintEvent()', self.pos()
        painter = QtGui.QPainter()
        painter.begin(self)
        self.__width = self.width()
        clr = 120
        for i in range(7):
            painter.setBrush(QtGui.QColor(clr,clr,clr))
            painter.setPen(QtGui.QColor(clr,clr,clr))
            painter.drawRect(0,i,self.__width-1,1)
            clr -= 5
        clr = 0
        painter.setBrush(QtGui.QColor(clr,clr,clr))
        painter.setPen(QtGui.QColor(clr,clr,clr))
        if self.__width > 8:
            painter.drawRect((self.__width/2)-3,3,0,0)
            painter.drawRect((self.__width/2)-4,4,1,0)
            
            painter.drawRect((self.__width/2)+3,3,0,0)
            painter.drawRect((self.__width/2)+2,4,1,0)
            
            clr = 120
            painter.setBrush(QtGui.QColor(clr,clr,clr))
            painter.setPen(QtGui.QColor(clr,clr,clr))
            painter.drawRect((self.__width/2)-4,3,0,0)
            painter.drawRect((self.__width/2)+2,3,0,0)
            
        clr = 0
        painter.setBrush(QtGui.QColor(clr,clr,clr))
        painter.setPen(QtGui.QColor(clr,clr,clr))
        if self.width > 2:
            painter.drawRect((self.__width/2),3,0,0)
            painter.drawRect((self.__width/2)-1,4,1,0)
            
            clr = 120
            painter.setBrush(QtGui.QColor(clr,clr,clr))
            painter.setPen(QtGui.QColor(clr,clr,clr))
            painter.drawRect((self.__width/2)-1,3,0,0)
            
        painter.end()
        #print '  RangeSliderButton paintEvent()', self.pos()
        
    def resizeEvent(self, evt):
        if not self.bSizer:
            self.__width = evt.size().width()
            print 'self.__width', self.__width, evt.oldSize().width()
            
    def mousePressEvent(self, evt):
        self.emit(QtCore.SIGNAL('clicked()'))
        evt.ignore()
        
class RangeSliderWidget(QtGui.QWidget):
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.minRange = RangeSliderButton(self)
        self.minRange.move(1,0)
        self.allRange = RangeSliderButton(self, width=self.width()-40, bSizer=False)
        self.allRange.move(20,0)
        self.maxRange = RangeSliderButton(self)
        self.maxRange.move(20,0)
        
        self.frameRangeExtents = (0,100)
        self.frameSubrange = (0,100)
        
        self.startPos = 0
        self.itemPos = 0
        self.barWidth = self.allRange.width()
        
        self.bMinSizing = False
        self.bMaxSizing = False
        self.bMovingRange = False

        #vbox = QtGui.QVBoxLayout()
        ##self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        #vbox.setSpacing(1)
        #vbox.setMargin(1)
        #self.hbox = QtGui.QHBoxLayout()
        #self.hbox.setSpacing(1)
        #self.hbox.setMargin(0)
        #self.hbox.addWidget(self.minRange)
        #self.hbox.addWidget(self.allRange)
        #self.hbox.addWidget(self.maxRange)
        #vbox.addLayout(self.hbox)
        #vbox.addStretch(1)
        #self.setLayout(vbox)
        
        QtCore.QObject.connect(self.minRange, QtCore.SIGNAL("clicked()"), self.minClicked)
        QtCore.QObject.connect(self.maxRange, QtCore.SIGNAL("clicked()"), self.maxClicked)
        QtCore.QObject.connect(self.allRange, QtCore.SIGNAL("clicked()"), self.allClicked)
        
    def getRangeData(self):
        poffset = float(float(self.minRange.pos().x()) - 1.0) / float(self.width()-2)
        pcoverage = (float(18.0 + self.maxRange.pos().x()) - (self.minRange.pos().x() - 1) ) / float(self.width()-2)
        return ( poffset, pcoverage )
        
    def paintEvent(self, evt):
        #print 'RangeSliderWidget paintEvent()'
        painter = QtGui.QPainter()
        painter.begin(self)
        clr = 60
        painter.setBrush(QtGui.QColor(clr,clr,clr))
        painter.setPen(QtGui.QColor(clr,clr,clr))
        painter.drawRect(0,0,self.width(),9)
        painter.end()
        
    def minClicked(self):
        self.bMinSizing = True
        self.itemPos = self.minRange.pos().x()
    
    def maxClicked(self):
        self.bMaxSizing = True
        self.itemPos = self.maxRange.pos().x()
    
    def allClicked(self):
        self.bMovingRange = True
        self.itemPos = self.minRange.pos().x()
        self.barWidth = self.allRange.width()
        
    def mouseReleaseEvent(self, evt):
        self.bMinSizing = False
        self.bMaxSizing = False
        self.bMovingRange = False
        
    def mousePressEvent(self, evt):
        self.startPos = evt.pos().x()

    def mouseMoveEvent(self, evt):
        offset = self.itemPos + (evt.pos().x() - self.startPos)
        if self.bMinSizing:            
            if offset > 0 and offset < self.maxRange.pos().x() - 19:
                self.minRange.setGeometry(offset, 1, 18, 7)
                self.allRange.setGeometry(offset+19, 1, self.maxRange.pos().x()-offset-20, 7)
                self.maxRange.setGeometry(self.maxRange.pos().x(), 1, 18, 7)
                self.emit(QtCore.SIGNAL('rangeChanged()'))
        elif self.bMaxSizing:
            if offset > (self.minRange.pos().x() + 19) and offset < self.width()-18:
                self.minRange.setGeometry(self.minRange.pos().x(), 1, 18, 7)
                self.allRange.setGeometry(self.minRange.pos().x()+19, 1, offset-self.minRange.pos().x()-20, 7)
                self.maxRange.setGeometry(offset, 1, 18, 7)
                self.emit(QtCore.SIGNAL('rangeChanged()'))
        elif self.bMovingRange:
            if offset > 0 and offset+38+self.barWidth < self.width():
                self.minRange.setGeometry(offset, 1, 18, 7)
                self.allRange.setGeometry(offset+19, 1, self.barWidth, 7)
                self.maxRange.setGeometry(offset+20+self.barWidth, 1, 18, 7)
                self.emit(QtCore.SIGNAL('rangeChanged()'))
                
    def resizeEvent(self, evt):
        if evt.oldSize().width() != evt.size().width():
            (a,b) = self.getRangeData()
            offset = int(self.width()*a)
            if offset < 1:
                offset = 1
            if b > 1:
                b = 1.0;
            self.barWidth = b * self.width() - 40
            print 'range slider resized.', a, b, offset, self.width()
            self.minRange.setGeometry(offset, 1, 18, 7)
            self.allRange.setGeometry(offset+19, 1, self.barWidth, 7)
            self.maxRange.setGeometry(offset+20+self.barWidth, 1, 18, 7)
                
class TimelineWidget(QtGui.QWidget):
    def __init__(self, parent=None, rangeWidget=None):
        QtGui.QWidget.__init__(self, parent)
        self.framerange = (0,100)
        self.visiblerange = (0,100)
        
        self.setMinimumSize(20,31)
        self.setMaximumHeight(31)
        self.setSizePolicy(1, 0)
        
        if rangeWidget:
            self.rangeWidget = rangeWidget
            QtCore.QObject.connect(self.rangeWidget, QtCore.SIGNAL("rangeChanged()"), self.rangeChanged)
        
    def rangeChanged(self):
        if self.rangeWidget:
            (a,b) = self.rangeWidget.getRangeData()
            print a, b
        
    def paintEvent(self, evt):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter = QtGui.QPainter()
        painter.begin(self)
        clr = 60
        painter.setBrush(QtGui.QColor(clr,clr,clr))
        painter.setPen(QtGui.QColor(clr,clr,clr))
        painter.drawRect(0,0,self.width(),30)
        clr = 100
        painter.setBrush(QtGui.QColor(clr,clr,clr))
        painter.setPen(QtGui.QColor(clr,clr,clr))
        painter.drawRect(1,1,self.width()-3,29)
        clr = 180
        painter.setPen(QtGui.QColor(clr,clr,clr))
        painter.drawLine(1,15,self.width()-2,15)
        (b,e) = self.visiblerange
        numframes = e-b
        pd = float(self.width()-4) / float(numframes)
        n = 0
        clr = 240
        painter.setPen(QtGui.QColor(clr,clr,clr))
        painter.drawLine(1,12,1,18)
        painter.drawText(0,9,str(b))
        for i in range(numframes):
            n += 1
            px = pd * n + 2
            if n % 10 == 0:
                clr = 240
                painter.setPen(QtGui.QColor(clr,clr,clr))
                painter.drawLine(px,10,px,20)
                painter.drawText(px,9,str(n))
            else:
                clr = 180
                painter.setPen(QtGui.QColor(clr,clr,clr))
                painter.drawLine(px,12,px,18)
        painter.end()
    
class TimeRangeWidget(QtGui.QWidget):
    """This is a timeline range widget simmilar to the one in the Houdini interface.    
    Use this class, as it contains all of the parts of the timeline as a whole."""
        
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setMinimumHeight(42)
        vbox = QtGui.QVBoxLayout()
        vbox.setMargin(0)
        vbox.setSpacing(0)
        
        self.r = RangeSliderWidget(self)
        self.t = TimelineWidget(self, self.r)

        vbox.addWidget(self.t)
        vbox.addWidget(self.r)
        self.setLayout(vbox)
        
class ColorSwatchWidget(QtGui.QWidget):
        
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.color = QtGui.QColor(128,128,128)
        self.setMinimumHeight(16)
        self.setMinimumWidth(20)
        self.setGeometry(0,0,20,16)

    def paintEvent(self, evt):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setBrush(self.color)
        painter.setPen(self.color)
        painter.drawRect(0,0,20,16)
        
        painter.end()
        
    def setColor(self, r, g, b):
        self.color = QtGui.QColor(r,g,b)
        self.update()
        
class ImageInfoWidget(QtGui.QWidget):
        
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setMaximumHeight(30)
        self.setMinimumHeight(30)
        hbox = QtGui.QHBoxLayout()
        hbox.setMargin(1)
        hbox.setSpacing(0)
        
        self._w = 100
        self._h = 100
        self.resolution = QtGui.QLabel(str(self._w)+"x"+str(self._h), self)
        self.resolution.setText("<font style='color: white;background: black;'>"+str(self._w)+"x"+str(self._h)+"</font>")
        
        self._xpos = 100
        self.xpos = QtGui.QLabel("x=", self)
        self.xpos.setText("<font style='color: white;background: black;'>x="+str(self._xpos)+"</font>")
        self._ypos = 100
        self.ypos = QtGui.QLabel("y=", self)
        self.ypos.setText("<font style='color: white;background: black;'>y="+str(self._ypos)+"</font>")
        
        self.swatch = ColorSwatchWidget(self)
        
        self.r = QtGui.QLabel("0.00000", self)
        self.r.setText("<font style='color: red;background: black;'>0.00000</font>")
        self.g = QtGui.QLabel("0.00000", self)
        self.g.setText("<font style='color: green;background: black;'>0.00000</font>")
        self.b = QtGui.QLabel("0.00000", self)
        self.b.setText("<font style='color: blue;background: black;'>0.00000</font>")
        self.a = QtGui.QLabel("0.00000", self)
        self.a.setText("<font style='color: white;background: black;'>0.00000</font>")
        
        self.h = QtGui.QLabel("H=0", self)
        self.h.setText("<font style='color: white;background: black;'>H=0</font>")
        self.s = QtGui.QLabel("S=0.00", self)
        self.s.setText("<font style='color: white;background: black;'>S=0.00</font>")
        self.v = QtGui.QLabel("V=0.00", self)
        self.v.setText("<font style='color: white;background: black;'>V=0.00</font>")
        self.l = QtGui.QLabel("L=0.00000", self)
        self.l.setText("<font style='color: white;background: black;'>L=0.00000</font>")
        
        hbox.addWidget(self.resolution)
        hbox.addStretch(1)
        hbox.addSpacing(5)
        hbox.addWidget(self.xpos)
        hbox.addSpacing(5)
        hbox.addWidget(self.ypos)
        hbox.addSpacing(5)
        hbox.addStretch(1)
        hbox.addWidget(self.r)
        hbox.addSpacing(5)
        hbox.addWidget(self.g)
        hbox.addSpacing(5)
        hbox.addWidget(self.b)
        hbox.addSpacing(5)
        hbox.addWidget(self.a)
        hbox.addSpacing(5)
        
        vbox = QtGui.QVBoxLayout()
        vbox.setMargin(1)
        vbox.setSpacing(0)
        vbox.addStretch(0)
        vbox.addWidget(self.swatch)
        vbox.addStretch(0)
        hbox.addLayout(vbox)
        
        hbox.addSpacing(5)
        hbox.addWidget(self.h)
        hbox.addSpacing(5)
        hbox.addWidget(self.s)
        hbox.addSpacing(5)
        hbox.addWidget(self.v)
        hbox.addSpacing(5)
        hbox.addWidget(self.l)
        hbox.addSpacing(5)
        #hbox.addStretch(1)
        
        self.setLayout(hbox)

    def paintEvent(self, evt):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setBrush(QtGui.QColor(0,0,0))
        painter.setPen(QtGui.QColor(0,0,0))
        painter.drawRect(0,0,self.width(), self.height())
        painter.end()
        
    def setWidth(self, w):
        if type(w) == int and w > 0:
            self._w = w
            self.resolution.setText("<font style='color: white;background: black;'>"+str(self._w)+"x"+str(self._h)+"</font>")
            self.update()
            
    def setHeight(self, h):
        if type(h) == int and h > 0:
            self._h = h
            self.resolution.setText("<font style='color: white;background: black;'>"+str(self._w)+"x"+str(self._h)+"</font>")
            self.update()
            
    def setCompSize(self, w, h):
        if type(w) == int and w > 0 and type(h) == int and h > 0:
            self._w = w
            self.resolution.setText("<font style='color: white;background: black;'>"+str(self._w)+"x"+str(self._h)+"</font>")
            self._h = h
            self.resolution.setText("<font style='color: white;background: black;'>"+str(self._w)+"x"+str(self._h)+"</font>")
            self.update()
        
    def setXPos(self, x):
        if type(x) == int:
            self._xpos = x
            self.xpos.setText("<font style='color: white;background: black;'>x="+str(self._xpos)+"</font>")
            self.update()
            
    def setYPos(self, y):
        if type(y) == int:
            self._ypos = y
            self.ypos.setText("<font style='color: white;background: black;'>y="+str(self._ypos)+"</font>")
            self.update()
            
    # this sets the color as floating point numbers
    def setColor(self, r, g, b, a):
        self.swatch.setColor(min(255,r*255),min(255,g*255),min(255,b*255))
        self.r.setText("<font style='color: red;background: black;'>%.5f</font>" % r)
        self.g.setText("<font style='color: green;background: black;'>%.5f</font>" % g)
        self.b.setText("<font style='color: blue;background: black;'>%.5f</font>" % b)
        self.a.setText("<font style='color: white;background: black;'>%.5f</font>" % a)
        
        self.h.setText("<font style='color: white;background: black;'>H:%s</font>" % max(0,self.swatch.color.hue()))
        self.s.setText("<font style='color: white;background: black;'>S:%.2f</font>" % self.swatch.color.saturationF())
        self.v.setText("<font style='color: white;background: black;'>V:%.2f</font>" % self.swatch.color.valueF()**(1/2.2))
        #self.l.setText("<font style='color: white;background: black;'>L:%.5f</font>" % (0.2126*(r**(1/2.2)) + 0.7152*(g**(1/2.2)) + 0.0722*(b**(1/2.2))))
        self.l.setText("<font style='color: white;background: black;'>L:%.5f</font>" % (0.2126*r + 0.7152*g + 0.0722*b))
        
class AllWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
              
        vbox = QtGui.QVBoxLayout()
        vbox.setMargin(0)
        vbox.setSpacing(0)
        
        vbox.addStretch(1)
        iiw = ImageInfoWidget(self)
        iiw.setColor(0.5,0.5,0.5,1)
        vbox.addWidget(iiw)
        trw = TimeRangeWidget(self)
        vbox.addWidget(trw)
        vbox.addStretch(1)
        
        self.setLayout(vbox)
    
def main():
    import sys
    app = QtGui.QApplication(sys.argv)

    w = AllWidget()
    w.show()
    
    app.exec_()
    
if __name__ == '__main__':
    main()