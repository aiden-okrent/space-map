from pathlib import Path

import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QImage, QPalette
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QFrame, QMainWindow, QMenu, QVBoxLayout, QWidget
from skyfield.api import load, wgs84

import config

'''

'''

class Map3DViewWidget(QWidget):
    def __init__(self, parent=None):
        super(Map3DViewWidget, self).__init__(parent)
        self.parent = parent

        # set up render clock called 'runtime'
        self.runtime = QTimer(self)
        self.runtime.timeout.connect(self.onRuntime) # run 'onRuntime' when timer ends
        self.runtime.start(16) # 60fps

        self.initUI()

    def onRuntime(self):
        self.map3DView.update()

    def setMapQuality(self, quality):
        self.map3DView.quality = quality
        self.map3DView.getTextures(quality)

    def getMapQuality(self):
        return self.map3DView.quality

    def initUI(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # map display
        self.map3DView = Map3DView(self)
        self.layout.addWidget(self.map3DView)

class Map3DView(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.quality = 0
        self.renderDistance = 160

    def initializeGL(self):
        # This method is called once upon the first time OpenGL context is available
        # Setup OpenGL state and resources
        # Enable depth and textures

        # Setup OpenGL state and resources
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)  # Enable texture mapping
        glEnable(GL_LIGHTING)   # Enable lighting
        glEnable(GL_LIGHT0)     # Enable light source 0
        glEnable(GL_COLOR_MATERIAL)  # Enable color materials
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)  # Set color materials to affect both ambient and diffuse components

        glLightfv(GL_LIGHT0, GL_POSITION, (-75, 100, 100, 1.0))

        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.3, 0.3, 0.3, 1.0))
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0.6, 0.6, 0.6, 1.0))
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 100.0)

        self.getTextures(self.quality)

    def getTextures(self, quality):
        if quality == 0:
            glShadeModel(GL_FLAT)
            self.earth_triangles = 16
            self.lighting_enabled = False
            self.earth_daymap = self.unpackImageToTexture(imagePath=os.path.join(config.map_textures, "land_ocean_ice_2048.jpg"))
            self.stars_milky_way = self.unpackImageToTexture(imagePath=os.path.join(config.map_textures, "2k_stars_milky_way.jpg"))

        elif quality == 1:
            glShadeModel(GL_SMOOTH)
            self.earth_triangles = 256
            self.lighting_enabled = True
            self.earth_daymap = self.unpackImageToTexture(imagePath=os.path.join(config.map_textures, "blue_marble_NASA_land_ocean_ice_8192.png"))
            self.stars_milky_way = self.unpackImageToTexture(imagePath=os.path.join(config.map_textures, "8k_stars_milky_way.jpg"))

    def unpackImageToTexture(self, imagePath):
        # Load a texture from an image file
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

    def resizeGL(self, width, height):
        # Update projection matrix on resize
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / float(height), 1, self.renderDistance)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()


    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluLookAt(-40, 0, 0, 0, 0, 0, 0, 0, -1)

        self.drawSkybox()
        glEnable(GL_LIGHTING)
        self.drawEarth()


    def drawEarth(self):
        glEnable(GL_TEXTURE_2D)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.earth_daymap)
        glPushMatrix()

        # draw earth sphere
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)  # Enable texture mapping
        gluSphere(quadric, wgs84.radius.km/1000, self.earth_triangles, self.earth_triangles)

        glPopMatrix()

    def drawSkybox(self):
        # disable lighting and depth masks because we want the skybox to be drawn behind everything
        glDisable(GL_LIGHTING)
        glDepthMask(GL_FALSE)
        glPushMatrix()

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.stars_milky_way)

        # Draw the skybox as a sphere
        glTranslatef(0, 0, 0)
        glScalef(-1, 1, 1)
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, 80, 32, 32)

        # restore settings so other objects are drawn correctly
        glDepthMask(GL_TRUE)
        glPopMatrix()
