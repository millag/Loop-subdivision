from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import QtOpenGL

from OpenGL import GL
from OpenGL import GLU

import glutils
import shapes
from geometry import *

import math

class DrawingWindow(QtOpenGL.QGLWidget):
    def __init__(self, format, parent = None, shareWidget = None):
        QtOpenGL.QGLWidget.__init__(self, format, parent, shareWidget)
        
        self.camera = Camera(20, math.pi/4, math.pi/4)
        self.frameRef = True
        self.grid = True
        self.wireframe = False
        
        self.__display_list = []
        self.selected_mesh = None
    
    def addToDisplayList(self, item):
        self.selected_mesh = item
        self.__display_list.append(item)
        self.glDraw()
        
    def refine_selected(self):
        if self.selected_mesh:
            self.selected_mesh.subdivide()
            self.glDraw()
            
    def unrefine_selected(self):
        if self.selected_mesh:
            self.selected_mesh.unsubdivide()
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
            #~ GL.glShadeModel(GL.GL_SMOOTH)
            #~ GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
            GL.glEnable(GL.GL_LIGHTING)
            GL.glMaterialfv(GL.GL_FRONT_AND_BACK, GL.GL_DIFFUSE, (GL.GLfloat * 4) ( 1, 1, 1, 1 ))
            GL.glDisable(GL.GL_TEXTURE_2D)
            GL.glColor3f(1, 1, 1)
            
        for item in self.__display_list:
            item.draw()
        
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


class Camera(object):
    def __init__(self, distance, rot_x, rot_y, zNear = 0.1, zFar = 1000.0, fovy = 60.0):
        self.zNear = zNear
        self.zFar = zFar
        self.fovy = fovy
        
        self.__rot_x = rot_x
        self.__rot_y = rot_y
        self.eye = polar(distance, rot_x,rot_y)
        self.at = Vector()
        self.up = polar(1 , self.__rot_x  , self.__rot_y + math.pi/2)
        
    
    def rotate(self, dx, dy):
        self.__rot_x += dx*math.pi
        self.__rot_y += dy*math.pi
        dirz = self.eye - self.at
        self.eye = self.at + polar(dirz.length() , self.__rot_x , self.__rot_y)
        self.up = polar(1 , self.__rot_x  , self.__rot_y + math.pi/2)
    
    def pan(self, dx, dy, w , h):
        dirz = self.at - self.eye
        wheight = 2 * dirz.length() * math.tan( math.radians(self.fovy / 2) )
        wwidth = wheight * float(w) / h
        
        diry = self.up.copy()
        diry.normalize()
        dirx = diry.cross(dirz)
        dirx.normalize()
        
        self.at = self.at + dx*wwidth*dirx + dy*wheight*diry
        self.eye = self.eye + dx*wwidth*dirx + dy*wheight*diry
    
    def zoom(self, dx, dy):    
        dirz = self.at - self.eye
        if dirz.length() > self.zFar and dy < 0:
            return
        self.eye = self.eye + dy*dirz
