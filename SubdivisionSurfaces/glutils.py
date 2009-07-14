from OpenGL import GL
from OpenGL import GLU


def draw_frame():
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

def draw_mesh(mesh):
    d_list = GL.glGenLists(1)
    if d_list:
        GL.glNewList(d_list, GL.GL_COMPILE)
        GL.glBegin(GL.GL_TRIANGLES)
        for i in xrange(mesh.viNum):
            GL.glNormal3f( mesh.vn[mesh.vni[i]].x,
                            mesh.vn[mesh.vni[i]].y,
                            mesh.vn[mesh.vni[i]].z)
            GL.glVertex3f( mesh.v[mesh.vi[i]].x,
                            mesh.v[mesh.vi[i]].y,
                            mesh.v[mesh.vi[i]].z)
        GL.glEnd()
        GL.glEndList()
            
    return d_list