from geometry import *
from ctypes import *
import array
import shapes

def NEXT(i):
    return (i+1)%3
def PREV(i):
    return (i+2)%3

class SDVert(Structure):
    _fields_ = [('pos', Vector),('child',c_int),('startFace',c_int),
                ('boundary',c_ubyte),('regular',c_ubyte),
                ('valence',c_uint),('ring',POINTER(c_uint))]
    
    def __init__(self, pos, b = False, r = False, v = 0):
        self.pos = pos
        self.startFace = -1
        self.child = -1
        self.boundary = b
        self.regular = r
        self.valence = v

class SDFace(Structure):
    _fields_ = [('v', c_int * 3),('nFaces', c_int * 3),('children',c_int * 4)]
    
    def __init__(self,v0 = -1,v1 = -1,v2 = -1):
        self.v[0] =v0 
        self.v[1] =v1
        self.v[2] =v2
        for i in xrange(3):
            self.nFaces[i] = -1
            self.children[i] = -1
        self.children[3] = -1
    
    def vnum(self, vert_i):
        for i in xrange(3):
            if vert_i == self.v[i]:
                return i
        raise ValueError("ERROR in 'vnum' method :the supplied vertex does not belong to the face")
        return -1

    def nextFace(self,vert_i):
        for i in xrange(3):
            if vert_i == self.v[i]:
                return self.nFaces[i]
        raise ValueError("ERROR in 'nextFace' method :the supplied vertex does not belong to the face")
        return -1
    
    def prevFace(self,vert_i):
        for i in xrange(3):
            if vert_i == self.v[i]:
                return self.nFaces[PREV(i)]
        raise ValueError("ERROR in 'prevFace' method :the supplied vertex does not belong to the face")
        return -1
    
    def nextVertex(self,vert_i):
        for i in xrange(3):
            if vert_i == self.v[i]:
                return self.v[NEXT(i)]
        raise ValueError("ERROR in 'nextVertex' method :the supplied vertex does not belong to the face")
        return -1
    
    def prevVertex(self,vert_i):
        for i in xrange(3):
            if vert_i == self.v[i]:
                return self.v[PREV(i)]
        raise ValueError("ERROR in 'prevVertex' method :the supplied vertex does not belong to the face")
        return -1
    
    def otherVertex(self, vert1, vert2):
        for i in xrange(3):
            if not ((vert1 == self.v[i]) or (vert2 == self.v[i])):
                return self.v[i]
        raise ValueError("ERROR in 'otherVertex' method !!!!!!!!")
        return -1

class SDEdge(Structure):
    _fields_ = [('v', c_int * 2)]
    
    def __init__(self, v0, v1):
        self.v[0] = min(v0,v1)
        self.v[1] = max(v0,v1)
    
    def __eq__(self, other):
        return ( self.v[0] == other.v[0] and self.v[1] == other.v[1] )
        
    def __lt__(self, other):
        if self.v[0] == other.v[0]:
            return self.v[1] < other.v[1]
        return self.v[0] < other.v[0]
        
    def __hash__(self):
        return hash((self.v[0], self.v[1]))
  

class SDTriangleMesh(Structure):
    
    _fields_ = [('vNum',c_uint),('sd_verts',POINTER(SDVert)),
                ('fNum',c_uint),('sd_faces',POINTER(SDFace)),
                ('eNum',c_uint),
                ('sdNum',c_ushort)]
                
    def __init__(self, vNum , v, viNum, vi, sd_num = 0):
        self.vNum = vNum
        sd_verts = (SDVert * self.vNum)()
        
        self.fNum = viNum / 3
        sd_faces = (SDFace * self.fNum)()
        
        for i in xrange(vNum):
            sd_verts[i].__init__(v[i])
        
        eNum = 0;
        edge_map = dict()
        for i in xrange(0, viNum, 3):
            index = i / 3
            sd_faces[index].__init__(vi[i], vi[i + 1], vi[i + 2])
            sd_face = sd_faces[index]
            
            for j in xrange(0,3):
                sd_verts[sd_face.v[j]].startFace = index
                
                sd_edge = SDEdge(sd_face.v[j], sd_face.v[ NEXT(j) ])
                other = edge_map.pop(sd_edge,None)
                
                if other != None:
                    sd_face.nFaces[j] = other[1]
                    sd_faces[other[1]].nFaces[other[0]] = index
                else:
                    eNum += 1
                    edge_map.setdefault(sd_edge, (j, index))
            
        edge_map.clear()
        
        for i in xrange(vNum):
            vert = sd_verts[i]
              
            ring =  array.array('I')
            ring.append( sd_faces[vert.startFace].nextVertex(i) )
            face_i = sd_faces[vert.startFace].nextFace(i)
            valence = 1
            
            while face_i != -1 and  face_i != vert.startFace:
                ring.append( sd_faces[face_i].nextVertex(i) )
                face_i = sd_faces[face_i].nextFace(i)
                valence += 1
            
            vert.boundary = (face_i == -1) 
            if not vert.boundary:
                vert.regular = (valence == 6)
            else:
                face_i = vert.startFace
                ring.reverse()
                while face_i != -1:
                    ring.append( sd_faces[face_i].prevVertex(i) )
                    face_i = sd_faces[face_i].prevFace(i)
                    valence += 1
                vert.regular = (valence == 4)
                
            vert.valence = valence
            vert.ring = (c_uint * vert.valence)(*ring)
            
        self.sdNum = sd_num
        self.sd_verts = sd_verts
        self.sd_faces = sd_faces
        self.eNum = eNum
    
    def refine(self):
        vNum = self.vNum
        fNum = self.fNum
        eNum = self.eNum
        sd_verts = self.sd_verts
        sd_faces = self.sd_faces
        
        mesh_list = []
        
        for k in xrange(self.sdNum):
            newVNum = vNum + eNum
            newFNum = 4*fNum
            newENum = 2*eNum + 3*fNum
            new_verts = (SDVert * newVNum)()
            new_faces = (SDFace * newFNum)()
            
            #~ compute new even vertices
            for i in xrange(vNum):
                vert = sd_verts[i]
                if vert.boundary:
                    pos = weightBoundaryVert(vert, float(1)/8, sd_verts)
                else:
                    pos = weightRingAround(vert, beta(vert), sd_verts)
                    
                new_verts[i].__init__(pos, vert.boundary, vert.regular, vert.valence)
                vert.child = i
            
            #~ create new faces, compute new odd vertices and init new faces vertices and update new vertices startFace pointer
            edge_map = dict()
            v_index = vNum
            for i in xrange(fNum):
                face = sd_faces[i]
                #~ create 4 new successor faces
                for j in xrange(4):
                    new_faces[i*4 + j].__init__()
                    face.children[j] = i*4 + j
                
                for j in xrange(3):
                    edge = SDEdge(face.v[j], face.v[ NEXT(j) ])
                    
                     #~ compute new edge vertex if not computed before
                    if not edge in edge_map:
                        neighbour_face = face.nFaces[j]
                        if neighbour_face != -1:
                            pos = (sd_verts[edge.v[0]].pos + sd_verts[edge.v[1]].pos) * (3.0 / 8.0) + (sd_verts[face.v[ PREV(j) ]].pos + sd_verts[ sd_faces[neighbour_face].otherVertex(face.v[j], face.v[ NEXT(j) ]) ].pos) * (1.0 / 8.0)
                        else:
                            pos = (sd_verts[edge.v[0]].pos + sd_verts[edge.v[1]].pos) * 0.5
                        
                        new_verts[v_index].__init__(pos , (neighbour_face == -1), True)
                        new_vert = new_verts[v_index]
                        new_vert.valence = 4 if new_vert.boundary else 6
                        new_vert.startFace = face.children[3]
                        
                        edge_map.setdefault(edge,v_index)
                        v_index +=1
                        
                    #~ set the corresonding vertex pointers in child faces
                    edge_vert_index = edge_map[edge]
                    new_faces[face.children[j]].v[j] = sd_verts[face.v[j]].child 
                    new_faces[face.children[j]].v[NEXT(j)] = edge_vert_index
                    new_faces[face.children[NEXT(j)] ].v[j] = edge_vert_index
                    new_faces[face.children[3]].v[j] = edge_vert_index
                    #~ set startFace on each even Vertex
                    new_verts[sd_verts[face.v[j]].child].startFace = face.children[j]
            edge_map.clear()
            
            #~ update new_faces neighbour_faces pointers and compute new vertex rings
            for i in xrange(fNum):
                face = sd_faces[i]
                for j in xrange(3):
                    #~ update child in the center neighbour_faces pointers
                    new_faces[face.children[3]].nFaces[j] = face.children[NEXT(j)]
                    new_faces[face.children[j]].nFaces[NEXT(j)] = face.children[3]
                    
                    neighbour_face = face.nFaces[j]
                    if neighbour_face != -1:
                        index = sd_faces[neighbour_face].vnum(face.v[j])
                        new_faces[face.children[j]].nFaces[j] = sd_faces[neighbour_face].children[index]
                        
                    neighbour_face = face.nFaces[ PREV(j) ]
                    if neighbour_face != -1:
                        index = sd_faces[neighbour_face].vnum(face.v[j])
                        new_faces[face.children[j]].nFaces[ PREV(j) ] = sd_faces[neighbour_face].children[index]
                        
            #~ prepare for next level of subdivision
            #~ compute new vertex rings
            for i in xrange(newVNum):
                set_vertex_ring(new_verts[i], i, new_faces)
            
            vNum = newVNum
            fNum = newFNum
            eNum = newENum
            sd_verts = new_verts
            sd_faces = new_faces
            
            mesh_list.append(convert(vNum , sd_verts, fNum, sd_faces))
            
        return mesh_list

def set_vertex_ring(vert, vert_index, sd_faces):
    ring = (c_uint * vert.valence)()
    
    i = 0
    ring[i] = sd_faces[vert.startFace].nextVertex(vert_index)
    face_i = sd_faces[vert.startFace].nextFace(vert_index)
    i += 1
    while face_i != -1 and face_i != vert.startFace:
        ring[i] = sd_faces[face_i].nextVertex(vert_index)
        face_i = sd_faces[face_i].nextFace(vert_index)
        i += 1
            
    if vert.boundary:
        ring[0], ring[i - 1] = ring[i - 1], ring[0]
        face_i = vert.startFace
        
        while face_i != -1:
            ring[i] = sd_faces[face_i].prevVertex(vert_index)
            face_i = sd_faces[face_i].prevFace(vert_index)
            i += 1
    
    vert.ring = ring

def beta(vertex):
    if vertex.regular:
        return 1.0 / 16.0
    if vertex.valence == 3:
        return 3.0 / 16.0
    return  3.0 / (8.0 * vertex.valence)

def weightRingAround(vertex, beta, sd_verts):
    vec = Vector()
    for i in xrange(vertex.valence):
        vec += sd_verts[vertex.ring[i]].pos
    vec *= beta
    vec += vertex.pos * (1.0 - vertex.valence * beta)
    
    return vec

def weightBoundaryVert(vertex, beta, sd_verts):
    vec = sd_verts[vertex.ring[0]].pos + sd_verts[vertex.ring[vertex.valence - 1]].pos
    vec *= beta
    vec += vertex.pos * (1.0 - 2 * beta)
    return vec

def convert(vNum , sd_verts , fNum, sd_faces):
    viNum = fNum*3
    v = (Vector * vNum)()
    vi = (c_uint * viNum)()
    for i in xrange(vNum):
        v[i] = sd_verts[i].pos
        
    for i in xrange(fNum):
        index = i*3
        vi[index] = sd_faces[i].v[0]
        vi[index + 1] = sd_faces[i].v[1]
        vi[index + 2] = sd_faces[i].v[2]
    
    vn = shapes.get_normals(vNum, v, viNum, vi)
    vni = (c_uint * viNum)(*vi)
    return (viNum, v, vi, vn, vni)
    
def subdivide(mesh, subdNum):
    subd_mesh = SDTriangleMesh(mesh.vNum, mesh.v, mesh.viNum, mesh.vi, subdNum)
    return subd_mesh.refine()
    