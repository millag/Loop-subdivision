from geometry import *
from ctypes import *
import glutils

from OpenGL import GL
from OpenGL import GLU

import subdiv    

class TriangleMesh(Structure):
    _fields_ = [('vNum',c_uint),('v',POINTER(Vector)),
                ('viNum',c_uint),('vi',POINTER(c_uint)),
                ('vnNum',c_uint),('vn',POINTER(Vector)),
                ('vni',POINTER(c_uint)),
                ('subdNum',c_uint),('subdLevel',c_uint),('is_subd',c_ubyte)]
                
    def __init__(self, v = tuple(), vi = tuple(), vn = tuple(), vni = tuple()):
        
        self.vNum = len(v)
        self.viNum = len(vi)
        self.vnNum = len(vn)
        
        #~ self.subdNum = subdNum
        #~ self.subdLevel = 0
        #~ self.is_subd = False
        
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
        
        self.__dlist = None
    
    def subdivide(self):
        pass
        #~ if not self.is_subd and self.subdNum > 0:
            #~ self.is_subd = True
            #~ lists = subdiv.subdivide(self.vNum, self.v, self.viNum, self.vi, self.subdNum)
            #~ self.__dlist[1:] = lists
            #~ print 'lists',self.__dlist
            
        #~ if self.subdLevel >= self.subdNum:
            #~ return False
            
        #~ self.subdLevel +=1
        #~ return True

    def unsubdivide(self):
        pass
        #~ if self.subdLevel == 0:
            #~ return False
        #~ self.subdLevel -= 1
        #~ return True
    
    def draw(self):
        if self.__dlist == None:
            self.__dlist = glutils.draw_mesh(self)
        GL.glCallList(self.__dlist)
