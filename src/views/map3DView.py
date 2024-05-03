#
from cgitb import text

import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QColor, QImage, QMouseEvent, QOpenGLFunctions
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from src.models.satellite import Satellite
from src.services.texture_service import TextureService  # Import the OpenGL widget


class Map3DView(QOpenGLWidget):
    def __init__(self, controller, parent, model):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.model = model
        self.TextureService = TextureService()

        self.runtime = QTimer(self)
        self.runtime.timeout.connect(self.update)  # run 'onRuntime' when timer ends

    def run(self):
        self.runtime.start(1000 / 60) # fps in milliseconds

    def resizeGL(self, width, height):
        """ Resize the OpenGL viewport, update the projection matrix, and set the POV Perspective """
        # Update projection matrix on resize
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / float(height), 0.1, 1000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def initializeGL(self):
        self.resetGLDefaults()

    def resetGLDefaults(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClearDepth(1.0)
        glDepthFunc(GL_LEQUAL)
        glDepthMask(GL_TRUE)
        glShadeModel(GL_SMOOTH)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHTING)
        glActiveTexture(GL_TEXTURE0)
        glEnable(GL_TEXTURE_2D)
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)


    def drawSphere(self, radius, slices, stacks):
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, radius, slices, stacks)
        gluDeleteQuadric(quadric)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        self.resetGLDefaults()
        self.setupCamera()

        data = self.model.getData()
        self.drawStars(data['stars'])
        self.drawEarth(data['earth'])
        for sat in data['satellites']:
            self.drawSatellite(sat.getData())
            self.drawOrbitalPath(sat.getData()['orbitalPath'])

    def setupCamera(self):
        gluLookAt(0, 0, 5, 0, 0, 0, 0, 1, 0)

    def drawStars(self, data):
        glDisable(GL_LIGHTING)
        glDepthMask(GL_FALSE)

        glActiveTexture(GL_TEXTURE0)
        self.bindTexture(data['texture'])
        glColor4f(*data['colorf4'])
        self.drawSphere(data['radius'], data['slices'], data['stacks'])

        self.resetGLDefaults()

    def drawEarth(self, data):

        glActiveTexture(GL_TEXTURE0)
        self.bindTexture(data['texture'])
        glMatrixMode(GL_TEXTURE)
        glLoadIdentity()
        glTranslatef(0.75, 0, 0)
        glMatrixMode(GL_MODELVIEW)
        glColor4f(*data['colorf4'])
        self.drawSphere(data['radius'], data['slices'], data['stacks'])


        self.resetGLDefaults()

    def drawSatellite(self, data):
        glTranslatef(*data['position'])

        self.resetGLDefaults()

    def drawOrbitalPath(self, data):
        glDisable(GL_LIGHTING)
        glLineWidth(data['lineWidth'])
        glColor4f(*data['color4f'])
        glBegin(GL_LINE_STRIP)
        for point in data['vertices']:
            glVertex3f(*point)
        glEnd()

        self.resetGLDefaults()

    def bindTexture(self, imagePath):
        """Bind a texture from an image file."""
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        image = QImage(imagePath)
        image = image.convertToFormat(QImage.Format.Format_RGBA8888)
        image = image.mirrored(False, True)
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            image.width(),
            image.height(),
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            image.bits()
        )
        return texture