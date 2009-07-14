from ctypes import *
import math

class Vector(Structure):
    __err = 0.0001
    
    _fields_ = [('x', c_float),('y', c_float),('z', c_float)]
    
    def __init__(self, x = 0, y = 0, z = 0):
        self.x = x
        self.y = y
        self.z = z
    
    def copy(self):
        return Vector(self.x,self.y,self.z)
    
    def __bool__(self):
        return not self == Vector()
        
    def __eq__(self, other):
        return abs(self.x - other.x) < Vector.__err and abs(self.y - other.y) < Vector.__err and abs(self.z - other.z) < Vector.__err
        
    
    def __lt__(self, other):
        t1 = self.tuple()
        t2 = other.tuple()
        return t1 < t2
    
    def __le__(self, other):
        if self == other or self < other:
            return True
        return False
        
    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
            
    def __abs__(self):
        return self.length()
            
    def normalize(self):
        l = self.length()
        if l:
            self.x /=l
            self.y /=l
            self.z /=l
    
    def get_angle_to(self, other):
        dot_prod = self.dot(other)
        return math.acos( dot_prod / (self.length() * other.length()) )
        
    def cross(self, other):
        return Vector(self.y * other.z - self.z * other.y,
                      self.z * other.x - self.x * other.z,
                      self.x * other.y - self.y * other.x)
                      
    def dot(self,other):
        return self.x * other.x + self.y * other.y + self.z * other.z
        
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
        
    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def __neg__(self):
        return Vector(-self.x, -self.y, -self.z)
    
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
        
    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self
        
    def __mul__(self, other):
        return Vector(other * self.x, other * self.y, other * self.z)
        
    def __imul(self, other):
        self.x *= other
        self.y *= other
        self.z *= other
        return self
        
    def __rmul__(self, other):
        return  self * other
    
    def __div__(self, scalar):
        return Vector(self.x / scalar, self.y / scalar, self.z / scalar)
    
    def __idiv__(self, scalar):
        self.x /= scalar
        self.y /= scalar
        self.z /= scalar
        return self
    
    def __rdiv__(self, scalar):
        return self / scalar

    def __hash__(self):
        return hash((self.x, self.y, self.z))
        
    def __str__(self):
        return '({0}, {1}, {2})'.format(self.x, self.y, self.z)
    
    def __repr__(self):
        return 'Vector({0}, {1}, {2})'.format(self.x, self.y, self.z)
    
    def tuple(self):
        return (self.x,self.y,self.z)

Vector.e1 = lambda : Vector(1,0,0)
Vector.e2 = lambda : Vector(0,1,0)
Vector.e3 = lambda : Vector(0,0,1)

def polar(distance , phi , theta):
    # phi is the angle between the vectors's projection in Oxz and x axis 
    # theta is the angle between the vector and it's projection in Oxz
        
    x = distance * math.cos(theta) * math.cos(phi)
    z = distance * math.cos(theta) * math.sin(phi)
    y = distance * math.sin(theta)
    return  Vector(x,y,z)

def get_polar_coords(vec):
        distance = vec.length()
        if not distance:
            return (0, 0, 0)
            
        theta = math.asin(vec.y / distance)
        if math.cos(theta) :
            phi = math.acos(vec.x / (distance * math.cos(theta)))
        else:
            phi = 0
        return (distance, phi, theta)
        
def collinear(v1, v2):
    l1 = v1.length()
    l2 = v2.length()
    if l2 :
        k = l1 / l2
        if v1.x != k * v2.x:
            return 0
        if v1.y != k * v2.y:
            return 0 
        if v1.z != k * v2.z:
            return 0 
        return k
    return 0
