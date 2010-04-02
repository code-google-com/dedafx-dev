from PyQt4 import QtCore, QtGui, QtOpenGL
import os, sys

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "OpenGL hellogl",
            "PyOpenGL must be installed to run this example.")
    sys.exit(1)
    
class Point:
    
    def __init__(self, x, y, z=None): #z=None means this is a 2d point
        self.x = x
        self.y = y
        self.z = z
        
class CncObject:
    
    """When building a cncObject, the points and lines are given in termas of a local origin. This allows the points to be calculated in global coords
    when constructing multiple pieces with the same object cut descriptions"""
    
    def __init__(self, parent, name=None, offset=Point(0.0,0.0), z_rotation=0.0):
        self.children = [] # empty array, to be filled with other CncObjects, lines, and arcs
        self.parent = parent # object parent must be workpiece or other CncObject
        self.selected = False
        
    def setParent(self, parent):
        self.parent = parent
        
class Workpiece(CncObject):
    
    def __init__(self, width, height, depth, x=0.0, y=0.0, z_top=0.0):
        CncObject.__init__(self, None) #top level object for cuts
        self.min = Point(x, y, z_top-depth)
        self.max = Point(x+width, y+height, z_top)
        
    def __str__(self):
        cmdStr = ""
        
        # fill in the commands for all of the objects as a string
        for obj in self.children:
            cmdStr += str(obj) + '\n'
        
        return cmdStr
    
    def draw(self):
        """this is a series of opengl draw commands for drawing the object in 3d"""
        glColor4f(0.15,0.15,0.15,1.0)
        
        glBegin(GL_LINE_STRIP)        
        glVertex3d(self.min.x, self.min.y, self.min.z)
        glVertex3d(self.min.x, self.max.y, self.min.z)
        glVertex3d(self.max.x, self.max.y, self.min.z)
        glVertex3d(self.max.x, self.min.y, self.min.z)
        glVertex3d(self.min.x, self.min.y, self.min.z)
        glEnd()
        
        glBegin(GL_LINE_STRIP)        
        glVertex3d(self.min.x, self.min.y, self.max.z)
        glVertex3d(self.min.x, self.max.y, self.max.z)
        glVertex3d(self.max.x, self.max.y, self.max.z)
        glVertex3d(self.max.x, self.min.y, self.max.z)
        glVertex3d(self.min.x, self.min.y, self.max.z)
        glEnd()
        
        glBegin(GL_LINES)        
        glVertex3d(self.min.x, self.min.y, self.min.z)
        glVertex3d(self.min.x, self.min.y, self.max.z)        
        glVertex3d(self.min.x, self.max.y, self.min.z)
        glVertex3d(self.min.x, self.max.y, self.max.z)        
        glVertex3d(self.max.x, self.max.y, self.min.z)
        glVertex3d(self.max.x, self.max.y, self.max.z)        
        glVertex3d(self.max.x, self.min.y, self.min.z)
        glVertex3d(self.max.x, self.min.y, self.max.z)        
        glEnd()
        
class Tool:
    
    def __init__(self, radius, tip_type):
        self.radius = radius
        self.tip_type = tip_type        
        
class CncMachine:
    
    """This is the main class to create objects for the gcode, as this class knows the params of the tool and workpiece, and can add items to the workpiece as appropriate"""
    
    def __init__(self, units='in', feedrate=8.0, z_increment=0.1, safe_z = 0.1, workpiece=Workpiece(12.0, 12.0, 0.5), tool=Tool(0.125, 0)):
        self.units = units
        self.feedrate = feedrate
        self.z_increment = z_increment
        self.safe_z = safe_z
        
        self.workpiece = workpiece
        self.tool = tool
        
    def __str__(self):
        """get the gcode as a large string"""
        cmdStr = ""
        
        # fill the header information
        if self.units == 'mm':
            cmdStr += 'G21\n'
        else:
            cmdStr += 'G20\n'
            
        cmdStr += "F{0:.4f}\n".format(self.feedrate)
        
        # goto a safe z height
        cmdStr += 'G00 Z{0:.4f}\n\n'.format(self.safe_z)
        
        cmdStr += str(self.workpiece)
        cmdStr += '\n'
        
        # goto a safe z height
        cmdStr += 'G00 Z{0:.4f}\n'.format(self.safe_z)
        # go back to home position
        cmdStr += 'G00 X0.0000 Y0.0000\n'
        cmdStr += 'M2\n' # end of program
        
        return cmdStr
    
    def setToolRadius(self, radius):
        self.tool.radius = radius
        
    def draw(self):
        self.workpiece.draw()
            
class Line(CncObject):
    
    def __init__(self, parent, point1, point2):
        CncObject.__init__(self, parent)
        self.p1 = point1
        self.p2 = point2
        
    def __str__(self):
        return ("G01 X{:.4f} YX{:.4f}".format(self.p2.x, self.p2.y))
        
    def startpointCmd(self, fastFeed=False):
        if fastFeed:
            return ("G00 X{:.4f} YX{:.4f}".format(self.p1.x, self.p1.y))
        else:
            return ("G01 X{:.4f} YX{:.4f}".format(self.p1.x, self.p1.y))
        
    def draw(self):
        glBegin(GL_LINES)
        glVertex3d(self.p1.x, self.p1.y, self.p1.z)
        glVertex3d(self.p2.x, self.p2.y, self.p2.z)
        glEnd()
        
class LineStrip(CncObject):
    
    def __init__(self, parent, pointArray, closed=True):
        CncObject.__init__(self, parent)
        self.points = pointArray
        self.closed = closed
        
    def __str__(self):
        return ""
    
    def draw(self):
        glBegin(GL_LINE_STRIP)
        for pt in self.points:
            glVertex3d(pt.x, pt.y, pt.z)
        if self.closed and len(self.points) > 0:
            pt = self.points[0]
            glVertex3d(pt.x, pt.y, pt.z)
        glEnd()
        
class Arc(CncObject):
    
    # centerpointIsAbsolute is true when the point is in global machine coords, otherwise it is incremental
    def __init__(self, parent, startpoint, endpoint, centerpoint, clockwise=True, centerpointIsAbsolute=True): 
        CncObject.__init__(self, parent)
        self.startpoint = startpoint
        self.endpoint = endpoint
        self.centerpoint = centerpoint
        self.clockwise = clockwise
        
    def __str__(self):
        if self.clockwise:
            return ("G02 X{:.4f} YX{:.4f} IX{:.4f} JX{:.4f}".format(self.endpoint.x, self.endpoint.y, self.centerpoint.x, self.centerpoint.y))
        else: #ccw
            return ("G03 X{:.4f} YX{:.4f} IX{:.4f} JX{:.4f}".format(self.endpoint.x, self.endpoint.y, self.centerpoint.x, self.centerpoint.y))
        
    def startpointCmd(self, fastFeed=False):
        if fastFeed:
            return ("G00 X{:.4f} YX{:.4f}".format(self.startpoint.x, self.startpoint.y))
        else:
            return ("G01 X{:.4f} YX{:.4f}".format(self.startpoint.x, self.startpoint.y))
        
    def draw(self):
        glStart(GL_LINE_STRIP)
        if self.startpoint.z != None:
            glVertex3d(self.startpoint.x, self.startpoint.y, self.startpoint.z)
        else:
            glVertex3d(self.startpoint.x, self.startpoint.y, 0.0)
            
        # TODO!
        
        if self.startpoint.z != None: #use startpoint z, because this should be a 2d arc on the xy plane!
            glVertex3d(self.endpoint.x, self.endpoint.y, self.startpoint.z)
        else:
            glVertex3d(self.endpoint.x, self.endpoint.y, 0.0)
            
        glEnd()
        
class Contour(CncObject):
    """This is just a collection of lines, arcs, and lineStrips"""
    pass
        
#class Pocket(CncObject):
 #   """A rectangular pocket, which is a series of linear cuts to form a pocketed hole to a certain depth"""
  #  pass

    