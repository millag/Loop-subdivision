from geometry import *
from ctypes import *


from OpenGL import GL
from OpenGL import GLU

import subdiv

def draw_frame():
    # draw frame reference
    GL.glDisable(GL.GL_DEPTH_TEST)
    GL.glBegin(GL.GL_LINES)
    
    GL.glColor3f(1,0,0)
    GL.glVertex3f(0,0,0)
    GL.glVertex3f(1,0,0)
        
    GL.glColor3f(0,1,0)
    GL.glVertex3f(0,0,0)
    GL.glVertex3f(0,1,0)

    GL.glColor3f(0,0,1)
    GL.glVertex3f(0,0,0)
    GL.glVertex3f(0,0,1)
    
    GL.glEnd()
    GL.glEnable(GL.GL_DEPTH_TEST)

def draw_grid():
    GL.glColor3f(0.6,0.6,0.6)
    GL.glEnable(GL.GL_LINE_STIPPLE)
    GL.glLineStipple(1,0x5555)
    
    GL.glBegin(GL.GL_LINES)
    for i in xrange(-5,6):
        GL.glVertex3f(i,0,-5)
        GL.glVertex3f(i,0,5)
        GL.glVertex3f(-5,0,i)
        GL.glVertex3f(5,0,i)
    GL.glEnd()
    GL.glDisable(GL.GL_LINE_STIPPLE)
    

class TriangleMesh(Structure):
    _fields_ = [('vNum',c_uint),('v',POINTER(Vector)),
                ('viNum',c_uint),('vi',POINTER(c_uint)),
                ('vnNum',c_uint),('vn',POINTER(Vector)),
                ('vni',POINTER(c_uint)),
                ('subdNum',c_uint),('subdLevel',c_uint),('is_subd',c_ubyte)]
                
    def __init__(self, v = tuple(), vi = tuple(), vn = tuple(), vni = tuple(), subdNum = 0):
        
        self.vNum = len(v)
        self.viNum = len(vi)
        self.vnNum = len(vn)
        
        self.subdNum = subdNum
        self.subdLevel = 0
        self.is_subd = False
        
        vniNum = len(vni)
        
        if self.viNum % 3 or vniNum % 3 :
            raise ValueError("ERROR in TriangleMesh: not enought elements !!!!!!")
        
        self.v = (Vector * self.vNum)(*v)
        self.vi = (c_uint * self.viNum)(*vi)

        if self.vnNum:
            self.vn = (Vector * self.vnNum)(*vn)
            if not vniNum:
                self.vni = (c_uint * self.viNum)(*vi)
            else:
                self.vni = (c_uint * vniNum)(*vni)
        else:
            if not vniNum:
                self.vn = subdiv.get_normals(self.vNum, self.v, self.viNum, self.vi)
                self.vni = (c_uint * self.viNum)(*vi)
            else:
                pass
        
        self.__dlist = [None]*(subdNum + 1)
    
    def subdivide(self):
        if not self.is_subd and self.subdNum > 0:
            self.is_subd = True
            #~ lists = subdiv.subdivide(self.vNum, self.v, self.viNum, self.vi, self.subdNum)
            #~ self.__dlist[1:] = lists
            #~ print 'lists',self.__dlist
            
        if self.subdLevel >= self.subdNum:
            return False
            
        self.subdLevel +=1
        return True

    def unsubdivide(self):
        if self.subdLevel == 0:
            return False
        self.subdLevel -= 1
        return True
    
    def draw(self):
        GL.glPushAttrib(GL.GL_ALL_ATTRIB_BITS)

        if self.__dlist[self.subdLevel] == None:
            self.__dlist[self.subdLevel] = GL.glGenLists(1)

            GL.glNewList(self.__dlist[self.subdLevel], GL.GL_COMPILE)
            GL.glBegin(GL.GL_TRIANGLES)
            for i in xrange(self.viNum):
                GL.glNormal3f( self.vn[self.vni[i]].x,
                        self.vn[self.vni[i]].y,
                        self.vn[self.vni[i]].z)
                GL.glVertex3f( self.v[self.vi[i]].x,
                        self.v[self.vi[i]].y,
                        self.v[self.vi[i]].z)
            GL.glEnd()
            GL.glEndList()
        GL.glCallList(self.__dlist[self.subdLevel])

        GL.glPopAttrib()
