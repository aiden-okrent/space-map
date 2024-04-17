from pathlib import Path

import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QImage, QPalette
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QFrame, QMainWindow, QMenu, QVBoxLayout, QWidget

'''
This is a widget to display the main display of the window.
The main display itself is self.display, which is an OpenGLWidget controlled here.

Display: QOpenGLWidget



'''

class CentralDisplayWidget(QWidget):
    def __init__(self, parent=None):
        super(CentralDisplayWidget, self).__init__(parent)
        self.parent = parent

        # set up render clock called 'runtime'
        self.runtime = QTimer(self)
        self.runtime.timeout.connect(self.onRuntime) # run 'onRuntime' when timer ends
        self.runtime.start(16) # 60fps

        self.initUI()

    def onRuntime(self):
        self.map3DView.update()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # map display first
        mapFrame = QFrame(self)
        mapFrame.setFrameShape(QFrame.Shape.Box)
        mapFrame.setLineWidth(1)
        mapFrameLayout = QVBoxLayout()
        mapFrame.setLayout(mapFrameLayout)

        self.map3DView = Map3DView(self)
        mapFrameLayout.addWidget(self.map3DView)

        # overlay on top of it
        self.overlay = QWidget(self)
        self.overlay.setAutoFillBackground(True)
        self.overlayPalette = QPalette()
        self.overlayPalette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0, 0))
        self.overlay.setPalette(self.overlayPalette)
        self.overlay.setFixedSize(800, 600)

        self.layout.addWidget(mapFrame)
        #self.layout.addWidget(self.overlay)

class Map3DView(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def initializeGL(self):
        # This method is called once upon the first time OpenGL context is available
        # Setup OpenGL state and resources
        # Enable depth and textures

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)

        # Enable/configure lighting
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glLightfv(GL_LIGHT0, GL_POSITION, [-7500, 10000, 10000])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 0.8, 1])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1, 1, 1, 1])

        self.loadTextures()


        # these loadTexture and loadTextures methods are bad, should really be handled by the controller and simply passed in
    def loadTextures(self):
        # Load textures
        map_textures = Path(__file__).resolve().parent / "assets" / "images" / "solarsystemscope.com"

        self.earth_daymap = self.loadTexture(imagePath=os.path.join(map_textures, "2k_earth_daymap.jpg"))
        self.earth_clouds = self.loadTexture(imagePath=os.path.join(map_textures, "2k_earth_clouds.jpg"))
        self.earth_specular = self.loadTexture(imagePath=os.path.join(map_textures, "2k_earth_specular_map.tif"))
        self.stars_milky_way = self.loadTexture(imagePath=os.path.join(map_textures, "2k_stars_milky_way.jpg"))
        self.earth_nightmap = self.loadTexture(imagePath=os.path.join(map_textures, "2k_earth_nightmap.jpg"))

    def loadTexture(self, imagePath):
        # Load a texture from a file
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        image = QImage(imagePath)
        image = image.convertToFormat(QImage.Format.Format_RGBA8888)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width(), image.height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, image.bits())
        return texture



    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, w / h, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
