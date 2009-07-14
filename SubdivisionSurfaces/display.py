from ctypes import *

import glutils
from OpenGL import GL
from OpenGL import GLU

import shapes
import subdiv  

class MeshSDWrap(Structure):
    _fields_ = [('mesh',shapes.TriangleMesh),
                ('subdNum',c_uint),('subdLevel',c_uint),('is_subd',c_ubyte)]
                
    def __init__(self, mesh , subdNum = 0):
        self.mesh = mesh
        self.subdNum = subdNum
        self.display_lists = (c_uint * (subdNum + 1))()
        self.subdLevel = 0
        self.is_subd = False
        self.display_lists[self.subdLevel] = glutils.draw_mesh(mesh.viNum, mesh.v, mesh.vi, mesh.vn, mesh.vni)

    def destroy(self):
        for list_name in self.display_lists:
            if list_name:
                GL.glDeleteLists(list_name, 1)
            
    def subdivide(self):
        if not self.is_subd and self.subdNum > 0:
            self.is_subd = True
            mesh_list = subdiv.subdivide(self.mesh, self.subdNum)
            i = 1
            for mesh in mesh_list:
                self.display_lists[i] = glutils.draw_mesh(*mesh)
                i += 1
            
        if self.subdLevel >= self.subdNum:
            return False
        
        self.subdLevel += 1
        return True

    def unsubdivide(self):
        if self.subdLevel == 0:
            return False
        self.subdLevel -= 1
        return True
    
    def draw(self):
        if self.display_lists[self.subdLevel]:
            GL.glCallList(self.display_lists[self.subdLevel])