from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import QtOpenGL

from OpenGL import GL
from OpenGL import GLU

import glutils
import displayutils

import math

class DrawingWindow(QtOpenGL.QGLWidget):
    def __init__(self, format, parent = None, shareWidget = None):
        QtOpenGL.QGLWidget.__init__(self, format, parent, shareWidget)
        
        self.camera = displayutils.Camera(20, math.pi/4, math.pi/4)
        self.frameRef = True
        self.grid = True
        self.wireframe = False
        
        self.display_object = None
    
    def setDisplayObject(self, item):
        if self.display_object:
            self.display_object.destroy()
            
        self.display_object = item
        self.glDraw()
        
    def refine_object(self):
        if self.display_object:
            self.display_object.subdivide()
            self.glDraw()
            
    def unrefine_object(self):
        if self.display_object:
            self.display_object.unsubdivide()
            self.glDraw()
        
    def toggle_grid(self):
        self.grid = not self.grid
        self.glDraw()
        
    def toggle_frame(self):
        self.frameRef = not self.frameRef
        self.glDraw()
    
    def toggle_wireframe(self):
        self.wireframe = not self.wireframe
        self.glDraw()
        
    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.NoButton or not (event.modifiers() & QtCore.Qt.AltModifier):
            return
        
        dx = (float(event.x() - self.lastPos.x())/self.width())
        dy = (float(event.y() - self.lastPos.y())/self.height())
        

        if event.buttons() & QtCore.Qt.LeftButton:
            self.camera.rotate(dx, dy)
            self.glDraw()
        elif event.buttons() & QtCore.Qt.RightButton:
            self.camera.zoom(dx, dy)
            self.glDraw()
        elif event.buttons() & QtCore.Qt.MidButton:
            self.camera.pan(dx, dy, self.width(), self.height())
            self.glDraw()
        
        self.lastPos = event.pos()
        
    
    def initializeGL(self):
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_LIGHTING)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_DIFFUSE, (GL.GLfloat *4) (1, 1, 1, 1 ))
        GL.glEnable(GL.GL_LIGHT0)
        GL.glDisable(GL.GL_TEXTURE_2D)
        
        GL.glClearColor(0.15,0.15,0.15,1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    
    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        
        GL.glPushMatrix()
        GL.glLoadIdentity()
        GLU.gluLookAt(self.camera.eye.x, self.camera.eye.y, self.camera.eye.z,
            self.camera.at.x , self.camera.at.y, self.camera.at.z ,
            self.camera.up.x , self.camera.up.y, self.camera.up.z)
        
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, (GL.GLfloat *4) ( self.camera.eye.x, self.camera.eye.y, self.camera.eye.z, 1 ))
        
        if self.wireframe:
            GL.glDisable(GL.GL_LIGHTING)
            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
            GL.glColor3f(0, 1, 0)
        else:
            GL.glEnable(GL.GL_LIGHTING)
            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
            GL.glMaterialfv(GL.GL_FRONT_AND_BACK, GL.GL_DIFFUSE, (GL.GLfloat * 4) ( 1, 1, 1, 1 ))
            
        if self.display_object:
            self.display_object.draw()
        
        GL.glDisable(GL.GL_LIGHTING)
        if self.grid:
            glutils.draw_grid()
            
        if self.frameRef:
            glutils.draw_frame()
        GL.glEnable(GL.GL_LIGHTING)
        
        GL.glPopMatrix()
    
    def resizeGL(self, w, h):
        if h == 0:
            h = 1
        if w == 0:
            w = 1
        
        GL.glViewport(0, 0, w, h)
    
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
    
        aspectRatio = float(w) / h
        GLU.gluPerspective(self.camera.fovy, aspectRatio, self.camera.zNear, self.camera.zFar)
    
        GL.glMatrixMode(GL.GL_MODELVIEW)

