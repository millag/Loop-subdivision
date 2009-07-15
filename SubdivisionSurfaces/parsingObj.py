import re
import array
from geometry import *
import shapes

from PyQt4 import QtCore

_float_regex = re.compile(r'(?:(?:^|\s))(?P<fnum>[-+]?(\d+(\.\d+(e[+-]\d+)?)?))(?=($|\s))',re.U)
_face_regex = re.compile(r'(?:(?:^|\s))(?P<v>\d+)(/((?P<vt>\d*)/)?(?P<vn>\d+))?(?=($|\s))',re.U)

def read_file(filename):
    mesh = None
    if filename.endsWith('.obj',QtCore.Qt.CaseInsensitive):
        mesh = _read_obj_file(filename)
    return mesh
    
def _read_obj_file(filename):
    vertices = []
    vindices = array.array('I')
    vnormals = []
    vnindices = array.array('I') 
    
    file = QtCore.QFile(filename)
    if not file.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text):
        return
        
    command_regex = re.compile(r'\s*(v|vn|vt|f)\s+',re.U)
    input = QtCore.QTextStream(file)
    while not input.atEnd():
        line = str(input.readLine())
        m = command_regex.match(line)
        if m:
            if m.group(1) == 'v':
                vertex = _parse_vertex_data(line[m.end():])
                vertices.append(vertex)
            elif m.group(1) == 'vn':
                normal = _parse_vertex_data(line[m.end():])
                vnormals.append(normal)
            elif m.group(1) == 'f':
                faces = _parse_face_data(line[m.end():])
                if faces:
                    vindices.extend(faces[0])
                    vnindices.extend(faces[1])
            else:
                pass
        
    file.close()
    return shapes.TriangleMesh(vertices, vindices, vnormals, vnindices)
    

def _parse_vertex_data(s):
    matches = _float_regex.finditer(s)
    coords = map(lambda x:  float(x.group('fnum')), matches)
    return Vector(*coords)
    

def _parse_face_data(s):
    matches = _face_regex.finditer(s)
    vi = array.array('I')
    vni = array.array('I')
    vti = array.array('I')
    
    for x in matches:
        vi.append(int(x.group('v')) - 1)
            
        if x.group('vt'):
            vti.append(int(x.group('vt')) - 1)
        if x.group('vn'):
            vni.append(int(x.group('vn')) - 1)
    if len(vi) < 3:
        return None
    return _triangulate_face(vi, vni, vti)

def _triangulate_face(vi, vni, vti):
    info = vi.buffer_info()
    if info[1] > 3:
        v1 = vi[0]
        v = array.array('I')
        vn1 = vni[0] if len(vni) else None
        vn = array.array('I')
        vt1 = vti[0] if len(vti) else None
        vt = array.array('I')
        for i in xrange(1,info[1] - 1):
            v.extend( (v1, vi[i], vi[i+1]) )
            if vn1 != None:
                vn.extend( (vn1, vni[i], vni[i+1]) )
            if vt1!= None:
                vt.extend( (vt1, vti[i], vti[i+1]) )
        return (v, vn, vt)
    return (vi, vni, vti)
