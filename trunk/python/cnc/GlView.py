from PyQt4 import QtCore, QtGui, QtOpenGL
import os, sys

try:
    from OpenGL import GL, GLU
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "OpenGL hellogl",
            "PyOpenGL must be installed to run this example.")
    sys.exit(1)

class GlView(QtOpenGL.QGLWidget):
    
    def __init__(self, parent = None, cnc=None):
        QtOpenGL.QGLWidget.__init__(self, parent)
        self.xsize = 512
        self.ysize = 512
        self.cnc = cnc
        self.viewType = 0 #persp, top, front, side
        self.vpw = 0
        self.vph = 0
        self.setMouseTracking(True)
        self.MouseButton = -1
        self.last_x = 0.
        self.last_y = 0.
        self.rot_x = 0.
        self.rot_y = 0.
        self.rot_z = 0.
        self.trn_x = 0.
        self.trn_y = 0.
        self.trn_z = 0.
        
        self.mode = 0 # selection/translate/rotate the object/selection, pan/rotate/zoom the view
        self.selectBuffer = []

    def initializeGL(self):
        self.qglClearColor(QtGui.QColor(0.0,0.0,0.0))
        GL.glShadeModel(GL.GL_FLAT)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
        self.selectBuffer = GL.glSelectBuffer(32) 
        
    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glPushMatrix()
        GL.glRotatef(self.rot_x,1.,0.,0.)
        GL.glRotatef(self.rot_y,0.,1.,0.)
        GL.glRotatef(self.rot_z,0.,0.,1.)        

        GL.glTranslatef(self.trn_x,self.trn_y,self.trn_z)
        
        GL.glBegin(GL.GL_LINES)
        GL.glColor3f (1.0, 0.0, 0.0)
        GL.glVertex3f(0,0,0)
        GL.glVertex3f(1,0,0)
        GL.glColor3f(0.0,1.0,0.0)
        GL.glVertex3f(0,0,0)
        GL.glVertex3f(0,1,0)
        GL.glColor3f(0.0,0.0,1.0)
        GL.glVertex3f(0,0,0)
        GL.glVertex3f(0,0,1)
        GL.glEnd()

        if self.cnc:
            self.cnc.draw()
            #wp = self.cnc.workpiece
            #GL.glTranslatef((wp.max.x-wp.min.x)/2,(wp.max.y-wp.min.y)/2,0.)
        GL.glPopMatrix()

    def resizeGL(self, width, height):
        if width <= 0 or height <= 0:
            return
        GL.glViewport( 0, 0, width, height )

        if self.viewType == 1: #top
            pass
        elif self.viewType == 2: #front
            pass
        elif self.viewType == 3: #side
            GL.glMatrixMode(GL.GL_PROJECTION)
            GL.glLoadIdentity()
            wp = self.cnc.workpiece
            GL.glOrtho( wp.min.y-2.0, wp.max.y+2.0, wp.min.z-2.0, wp.min.z+2.0, wp.max.x+2.0, wp.min.x-2.0 )
        else: #persp            
            GL.glMatrixMode(GL.GL_PROJECTION)
            GL.glLoadIdentity()
            GLU.gluPerspective(35.0,1.0*width/height,0.001,1000.0)
            
            GL.glMatrixMode(GL.GL_MODELVIEW)
            GL.glLoadIdentity()
            wp = self.cnc.workpiece
            GLU.gluLookAt((wp.max.x-wp.min.x)/2,-20.0,5.0, (wp.max.x-wp.min.x)/2,(wp.max.y-wp.min.y)/2,0.0, 0.0,0.0,1.0)
        
    def mousePressEvent(self,ev):
        button = ev.button()
        if button == QtCore.Qt.LeftButton:
            self.MouseButton = 0
            #picking
            vp = [0,0,0,0]
            #GL.glRenderMode(GL.GL_SELECT)
            #GL.glMatrixMode(GL.GL_PROJECTION)
            GL.glPushMatrix()
            #GL.glLoadIdentity()
            vp = GL.glGetIntegerv(GL.GL_VIEWPORT)
            print 'vp', vp
            GLU.gluPickMatrix(ev.x(), vp[3]-ev.y(), 5, 5, vp)
            #GLU.gluPerspective(45,1,0.1,1000)
            #GL.glMatrixMode(GL.GL_MODELVIEW);

            self.cnc.drawPick()
            res = GL.glRenderMode(GL.GL_RENDER)
            GL.glPopMatrix()
            print str(res)#, res[0][2], res[0][2][-1]
            if res and res[0][2]:
                if res[0][2][-1] == 0:
                    print 'workpiece selected'
                else:
                    print 'nothing selected'
        elif button == QtCore.Qt.RightButton:
            self.MouseButton = 2
        else:
            self.MouseButton = 1
        self.last_x = ev.x()
        self.last_y = ev.y()
        self.update()

    def mouseReleaseEvent(self,ev):
        self.MouseButton = -1

    def mouseMoveEvent(self,ev):
        x,y = ev.x(),ev.y()
        dx = x-self.last_x
        dy = y-self.last_y
        mouse = self.MouseButton
        if mouse == 0: #left mouse btn
            self.rot_x += .2*dy
            self.rot_z += .2*dx
            self.update()
        elif mouse == 1: #middle mouse btn
            self.trn_x += .02*dx
            self.trn_z -= .02*dy
            self.update()
        elif mouse == 2: #right mouse btn
            pass
        self.last_x = x
        self.last_y = y
        

    def wheelEvent(self,ev):
        delta = ev.delta() # usually +/- 120
        scale = self.scale
        if delta != 0:
            scale += 6./float(delta)
            self.scale = min(2.,max(.2,scale))