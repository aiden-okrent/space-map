#
from cgitb import text

import numpy as np
from line_profiler import LineProfiler
from OpenGL.GL import *
from OpenGL.GLU import *
from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QColor, QImage, QMouseEvent, QOpenGLFunctions
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from src.models.satellite import Satellite
from src.services.texture_service import TextureService  # Import the OpenGL widget


class Map3DView(QOpenGLWidget):
    def __init__(self, Controller, parent, Model):
        super().__init__(parent)
        self.parent = parent
        self.Controller = Controller
        self.Model3D = Model
        self.Earth = Controller.Earth
        self.Simulation = Controller.Simulation
        self.TextureService = TextureService()

        self.runtime = QTimer(self)
        self.runtime.timeout.connect(self.update)  # run 'onRuntime' when timer ends

        earthRadius = self.Earth.radius.km
        self.camera = {
            'position': [0, 0, 0],
            'upVector': [0, 0, 1],
            'lookAt': [0, 0, 0],
            'phi': 0,
            'theta': 0,
            'zoom': 5 * earthRadius,
            'maxZoom': 30 * earthRadius,
            'minZoom': .12 * earthRadius,
        }

        self.mouse = {
            'lastPos': QPoint(),
        }

        self.Model3D.dataChanged.connect(self.update)

    def run(self):
        self.runtime.start(1000 / 60) # fps in milliseconds

    def resizeGL(self, width, height):
        """ Resize the OpenGL viewport, update the projection matrix, and set the POV Perspective """
        # Update projection matrix on resize
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / float(height), 0.1, self.Earth.radius.km * 1000)
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
        glShadeModel(GL_SMOOTH)
        glEnable(GL_LINE_SMOOTH)

        self.updateCamera()

    def drawLight(self, light):
        glLightfv(GL_LIGHT0, GL_POSITION, light['translation'])
        glLightfv(GL_LIGHT0, GL_AMBIENT, light['ambient'])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light['diffuse'])
        glLightfv(GL_LIGHT0, GL_SPECULAR, light['specular'])

    def drawSphere(self, data):
        glActiveTexture(GL_TEXTURE0)

        if data['texture'] is '':
            glBindTexture(GL_TEXTURE_2D, 0)
        else:
            texture_id = self.Model3D.getTexture(data['texture'])
            glBindTexture(GL_TEXTURE_2D, texture_id)

            glMatrixMode(GL_TEXTURE)
            if data['texture_offset'] is not None:
                glLoadIdentity()
                glTranslatef(*data['texture_offset'])

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        if data['translation'] is not None:
            glTranslatef(*data['translation'])
        if data['rotation4f'] is not None:
            glRotatef(*data['rotation4f'])
        if data['colorf4'] is not None:
            glColor4f(*data['colorf4'])
        else:
            glColor4f(1, 1, 1, 1)

        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, data['radius'], data['slices'], data['stacks'])
        gluDeleteQuadric(quadric)

        glPopMatrix()
        self.resetGLDefaults()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        self.resetGLDefaults()
        gluLookAt(*self.camera['position'], *self.camera['lookAt'], *self.camera['upVector'])

        data = self.Model3D.data
        for light in data['lights']:
            self.drawLight(light)
        self.drawStars(data['stars'])
        self.drawLines(data['XYZAxis'])

        glPushMatrix()
        self.applyRotation(data['rotations']['earth_Oblique'])

        for sat in data['satellites']:
            if sat.infoData['hidden']:
                continue
            renderData = sat.renderData
            self.drawSatellite(renderData)
            self.drawLines(renderData['toSurface'])
            self.drawOrbitalPath(renderData['orbitalPath'])

        self.applyRotation(data['rotations']['earth_Spin'])
        self.drawSphere(data['earth'])
        self.drawCylinders(data['poles'])
        glPopMatrix()

    def updateCamera(self):
        self.camera['phi'] = max(min(self.camera['phi'], 89), -89)
        self.camera['theta'] %= 360

        self.camera['zoom'] = max(min(self.camera['zoom'], self.camera['maxZoom']), self.camera['minZoom'])

        phi_rad = np.radians(self.camera['phi'])
        theta_rad = np.radians(self.camera['theta'])

        x = self.camera['zoom'] * np.cos(phi_rad) * np.cos(theta_rad)
        y = self.camera['zoom'] * np.cos(phi_rad) * np.sin(theta_rad)
        z = self.camera['zoom'] * np.sin(phi_rad) # Up Vector

        self.camera['position'] = [x, y, z]

        self.update()

    def drawLines(self, data):
        if not data['visible']:
            return
        glDisable(GL_LIGHTING)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, 0)
        glLineWidth(data['lineWidth'])
        for line in data['lines']:
            glPushMatrix()
            glTranslatef(*line['translation'])
            glRotatef(*line['rotation4f'])
            glBegin(GL_LINES)
            glColor4f(*line['color4f'])
            for vertex in line['vertices']:
                glVertex3f(*np.array(vertex) * line['length'])
            glEnd()
            glPopMatrix()

        self.resetGLDefaults()

    def drawCylinders(self, data):
        glDisable(GL_LIGHTING)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, 0)
        for cylinder in data['cylinders']:
            glPushMatrix()
            glTranslatef(*cylinder['translation'])
            glRotatef(*cylinder['rotation4f'])
            glColor4f(*cylinder['color4f'])
            quadric = gluNewQuadric()
            gluQuadricTexture(quadric, GL_TRUE)
            gluCylinder(quadric, cylinder['radius'], cylinder['radius'], cylinder['height'], 16, 16)
            gluDeleteQuadric(quadric)
            glPopMatrix()

        self.resetGLDefaults()

    def drawStars(self, data):
        glDisable(GL_LIGHTING)
        glDepthMask(GL_FALSE)
        self.drawSphere(data)
        self.resetGLDefaults()

    def applyRotation(self, rotation):
        glRotatef(*rotation)

    def drawSatellite(self, data):
        glDisable(GL_LIGHTING)
        self.drawSphere(data['model'])
        self.resetGLDefaults()

    def drawOrbitalPath(self, data):
        if not data['visible']:
            return
        glDisable(GL_LIGHTING)
        glLineWidth(data['lineWidth'])
        glColor4f(*data['color4f'])
        glBegin(GL_LINE_STRIP)
        for point in data['vertices']:
            glVertex3f(*point)
        glEnd()

        self.resetGLDefaults()

    def get2DScreenCoordsFrom3D(self, x, y, z):
        """ Convert 3D coordinates to 2D screen coordinates."""
        viewport = glGetIntegerv(GL_VIEWPORT)
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)

        screen_coords = gluProject(x, y, z, modelview, projection, viewport)
        screen_coords = [int(coord) for coord in screen_coords]

        # Adjust for the height and width of the OpenGL widget
        screen_coords[0] *= self.width() / viewport[2]
        screen_coords[1] *= self.height() / viewport[3]

        return screen_coords

    def mousePressEvent(self, event: QMouseEvent):
        self.mouse['lastPos'] = event.pos()
        self.updateCamera()

    def mouseMoveEvent(self, event: QMouseEvent):
        dx = event.x() - self.mouse['lastPos'].x()
        dy = event.y() - self.mouse['lastPos'].y()

        if event.buttons() & Qt.LeftButton:
            self.camera['theta'] -= dx / 2
            self.camera['phi'] += dy / 2

        self.mouse['lastPos'] = event.pos()
        self.updateCamera()

    def wheelEvent(self, event):
        self.camera['zoom'] -= event.angleDelta().y() / 1200 * self.camera['zoom']
        self.updateCamera()