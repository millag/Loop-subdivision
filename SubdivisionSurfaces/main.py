# main.py
import sys

from PyQt4 import QtGui
from PyQt4 import QtCore

from parsingObj import *
from interface import *

import subdiv

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        
        self.setGeometry(100, 100, 1000, 800)
        self.setWindowTitle('3DViewer')
        
        #~ center region
        format = QtOpenGL.QGLFormat(QtOpenGL.QGL.DoubleBuffer | QtOpenGL.QGL.DepthBuffer | QtOpenGL.QGL.Rgba | QtOpenGL.QGL.SampleBuffers)
        self.setCentralWidget(DrawingWindow(format, self))
        
        #~ menu items and status bar
        open = QtGui.QAction('Open', self)
        open.setShortcut('Ctrl+O')
        open.setStatusTip('Open File')
        self.connect(open, QtCore.SIGNAL('triggered()'), self.import_from_file )
        
        exit = QtGui.QAction('Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit application')
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))
        
        grid = QtGui.QAction('Grid', self)
        grid.setStatusTip('Show/Hide Grid')
        grid.setCheckable(True)
        grid.setChecked(True)
        self.connect(grid, QtCore.SIGNAL('triggered()'), self.centralWidget().toggle_grid)
        
        frame = QtGui.QAction('Frame', self)
        frame.setStatusTip('Show/Hide Frame Reference')
        frame.setCheckable(True)
        frame.setChecked(True)
        self.connect(frame, QtCore.SIGNAL('triggered()'), self.centralWidget().toggle_frame)
        
        wireframe = QtGui.QAction('Wireframe', self)
        wireframe.setStatusTip('Toggle Wireframe Mode')
        wireframe.setCheckable(True)
        wireframe.setChecked(False)
        self.connect(wireframe, QtCore.SIGNAL('triggered()'), self.centralWidget().toggle_wireframe)
        
        refine = QtGui.QAction('Refine', self)
        refine.setShortcut('Ctrl+R')
        refine.setStatusTip('Refine Mesh')
        self.connect(refine, QtCore.SIGNAL('triggered()'), self.centralWidget().refine_selected)
        
        unrefine = QtGui.QAction('Unrefine', self)
        unrefine.setShortcut('Ctrl+U')
        unrefine.setStatusTip('Unrefine Mesh')
        self.connect(unrefine, QtCore.SIGNAL('triggered()'), self.centralWidget().unrefine_selected)
        
        menubar = self.menuBar()
        filem = menubar.addMenu('File')
        filem.addAction(open)
        filem.addAction(exit)
        view = menubar.addMenu('View')
        view.addAction(grid)
        view.addAction(frame)
        view.addAction(wireframe)
        edit = menubar.addMenu('Edit')
        edit.addAction(refine)
        edit.addAction(unrefine)
        
        self.statusBar()
        
        self.center()
    
    def center(self):
        s_bounds = QtGui.QDesktopWidget().screenGeometry()
        bounds = self.geometry()
        self.move((s_bounds.width() - bounds.width()) / 2,(s_bounds.height() - bounds.height()) / 2)
    
    def import_from_file(self):
        file_name = QtGui.QFileDialog.getOpenFileName(None, "Open File", "SampleFiles/", "Obj Files (*.obj)")
        mesh = None
        if file_name.endsWith('.obj',QtCore.Qt.CaseInsensitive):
            mesh = read_obj_file(file_name)
        if file_name.endsWith('.off',QtCore.Qt.CaseInsensitive):
            print 'off file'
        if mesh == None:
            return
            
        sd_num = 3
        if mesh.vNum <= 300:
            sd_num = 5
        elif mesh.vNum >= 1000:
            sd_num = 2
        print 'subdivision number',sd_num
        
        self.centralWidget().addToDisplayList(mesh)
        # HACKS
        #~ subdiv_mesh = subdiv.SDTriangleMesh(len(param[0]), param[0], len(param[1]), param[1], sd_num = sd_num)
        #~ param2 = subdiv_mesh.refine()
        #~ print 'refined'
        

def main(*args):
    
    app = QtGui.QApplication(sys.argv)
   
    win  = MainWindow()
    win.show()
    
    sys.exit(app.exec_())
    
main()