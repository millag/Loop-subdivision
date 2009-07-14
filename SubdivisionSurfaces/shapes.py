from geometry import *
from ctypes import *  

class TriangleMesh(Structure):
    _fields_ = [('vNum',c_uint),('v',POINTER(Vector)),
                ('viNum',c_uint),('vi',POINTER(c_uint)),
                ('vnNum',c_uint),('vn',POINTER(Vector)),
                ('vni',POINTER(c_uint))]
                
    def __init__(self, v = tuple(), vi = tuple(), vn = tuple(), vni = tuple()):
        
        self.vNum = len(v)
        self.viNum = len(vi)
        self.vnNum = len(vn)
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
                self.vn = get_normals(self.vNum, self.v, self.viNum, self.vi)
                self.vni = (c_uint * self.viNum)(*vi)
            else:
                pass

def get_normals(vNum, vertices, viNum, indices):
    res  = (Vector * vNum)()
    
    for j in xrange(0,viNum,3):
        for i in xrange(3): 
            dirx = vertices[indices[j + (i + 1)%3]] - vertices[indices[j + i]]
            dirz = vertices[indices[j + (i + 3 - 1)%3]] - vertices[indices[j + i]]
            diry = dirx.cross(dirz)
            
            res[indices[j + i]] += diry
            
    for j in xrange(vNum):
        res[j].normalize()
        
    return res    
