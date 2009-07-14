from geometry import *
import math
 
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
