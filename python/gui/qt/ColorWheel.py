from PyQt4 import QtCore, QtGui
import sys, math

# lift / gamma / gain
# outColor = ( gainColor * ( inputColor + liftColor * ( 1 - inputColor ))) ^ ( 1/gammaColor )
#
# or ASC CDL
# outcolor = (incolor * slope + offset) ^ power
# power = 1/gamma, slope = gain, offset = lift


class ColorWheelWidget(QtGui.QWidget):
    def __init__(self, parent=None, mainDiameter=256, outerRingWidth=30):
        QtGui.QWidget.__init__(self, parent)
        # this is the pixel diameter of the actual color wheel, without the extra decorations drawn as part of this widget
        self.dim = mainDiameter
        self.offset = outerRingWidth
        
        self.master_radius = (self.dim/2)+self.offset+1
        # the color wheel image, only needs to be generated once
        self.image = QtGui.QImage(self.master_radius*2, self.master_radius*2, QtGui.QImage.Format_ARGB32)
        self.image.fill(QtGui.QColor(QtCore.Qt.white).rgb())
        
        self.center = (self.master_radius, self.master_radius)
        
        # this is the color value that this widget represents
        self.color = QtGui.QColor()
        self.color.setHsv(0,0,0,0)
        
        # this is the image for the current color selection
        self.current_image = QtGui.QImage(self.master_radius*2, self.master_radius*2, QtGui.QImage.Format_ARGB32)
        self.current_image.fill(QtGui.QColor(self.color).rgba())
        
        # these are used for the current color selection image
        self.bMouseDown = False
        
        self.points = self.getRadialLinePoints((self.dim / 2), self.master_radius, 14.5)
        self.points2 = self.getRadialLinePoints((self.dim / 2), self.master_radius, 106.5)
        
        self.huepoint = (self.master_radius, self.master_radius)
        self.value_angle = 0.0
        
        for y in range(self.master_radius*2):
            for x in range(self.master_radius*2):
                d = 2 * self.getDist((x,y),self.center) / self.dim
                if d <= 1:
                    color = QtGui.QColor()
                    hue = self.getHue(x, y)
                    color.setHsv(hue,(d*255),255,255)
                    self.image.setPixel(x,y, color.rgba())
                else:
                    d2 = self.getDist((x,y),self.center) / (self.master_radius-1)
                    if d2 > 1:                        
                        color = QtGui.QColor()
                        color.setAlpha(0)
                        self.image.setPixel(x,y, color.rgba())
                    else:
                        #get the cc angle in degrees from 15 deg cc from due north of center
                        color = QtGui.QColor()
                        v = self.getHue(x, y) * 255 / 360
                        if v <= (255/4):
                            v = 128
                            color.setHsv(0,128,128,255)
                            self.current_image.setPixel(x,y, color.rgba())
                        else:
                            v = 1.333333333 * v - 85
                            color.setHsv(0,0,v,255)
                            self.image.setPixel(x,y, color.rgba())
                            
    def getRadialLinePoints(self, r_inner, r_outer, angle):
        rad = math.radians(angle)
        sr = math.sin(rad)
        cr = math.cos(rad)
        x1 = r_outer - (r_outer * sr)
        y1 = r_outer - (r_outer * cr) 
        x2 = r_outer - (r_inner * sr)
        y2 = r_outer - (r_inner * cr)
        return (x1, y1, x2, y2)
                
    def getHue(self, x, y):
        return int( ( math.degrees ( math.atan2 ( 2*(x - self.master_radius),2*(y - self.master_radius))) + 165 ) % 360)
    
    def setColor(self, h, s, v):
        self.color.setHsv(h,s,v)
        alpha = self.current_image.alphaChannel()
        self.current_image.fill(self.color.rgb())
        self.current_image.setAlphaChannel(alpha)
        self.update()                
        
    def getDist(self, (x1, y1), (x2, y2)):
        return math.sqrt((x2-x1)**2 + (y2-y1)**2)
        
    def paintEvent(self, evt):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        pen = QtGui.QPen()
        pen.setColor(QtGui.QColor(100,100,100))
        pen.setWidth(2)
        painter.setPen(pen)
        
        painter.drawImage(0,0,self.image)
        painter.drawImage(0,0,self.current_image)
        r = self.dim/2 
        r2 = r + self.offset
        center = QtCore.QPoint(r2+1,r2+1)  
        
        painter.drawEllipse(center, r, r )
        painter.drawEllipse(center, r2, r2 )
        
        (x1,y1,x2,y2) = self.points
        painter.drawLine(x1,y1+1,x2,y2)
        (x1,y1,x2,y2) = self.points2
        painter.drawLine(x1+2,y1,x2,y2)
        
        pen.setWidth(1)
        pen.setColor(QtGui.QColor(0,0,0))
        painter.setPen(pen)
        
        (hpx, hpy) =  self.huepoint
        painter.drawEllipse(QtCore.QPoint(hpx, hpy), 5, 5)
        
        (x1,y1,x2,y2) = self.getRadialLinePoints((self.dim / 2)+1, self.master_radius, self.value_angle+16)        
        (x3,y3,x4,y4) = self.getRadialLinePoints((self.dim / 2)+1, self.master_radius, self.value_angle+14)
        painter.drawLine(x1,y1,x2,y2)
        painter.drawLine(x2,y2,x4,y4)
        painter.drawLine(x3,y3,x4,y4)
        painter.drawLine(x3,y3,x1,y1)
        
    def alterColor(self, x, y):
        d = 2 * self.getDist((x,y),self.center) / self.dim
        if d <= 1:
            hue = self.getHue(x, y)
            self.huepoint = (x,y)
            self.setColor(hue,int(d*255),self.color.value())
        else:
            d = self.getDist((x,y),self.center) / self.master_radius
            if d <= 1:
                self.value_angle = (self.getHue(x, y)) % 360
                v = self.value_angle * 255 / 360
                if v > (255/4):
                    v = 1.333333333 * v - 85
                    self.setColor(self.color.hue(), self.color.saturation(), v)
        
    def mousePressEvent(self, evt):
        self.bMouseDown = True
        self.alterColor(evt.x(), evt.y())
    
    def mouseMoveEvent(self, evt):
        if self.bMouseDown:
            self.alterColor(evt.x(), evt.y())
    
    def mousereleaseEvent(self, evt):
        self.bMouseDown = False

def main(args):
    app=QtGui.QApplication(args)
    win=ColorWheelWidget()
    win.show()
    app.connect(app, QtCore.SIGNAL("lastWindowClosed()")
                 , app
                 , QtCore.SLOT("quit()")
                 )
    app.exec_()
  
if __name__=="__main__":
    main(sys.argv)
