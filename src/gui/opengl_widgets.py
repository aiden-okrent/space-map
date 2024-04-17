import datetime
import os
import time
from math import cos, radians, sin

import numpy as np
import OpenGL.GL.shaders
import requests
from matplotlib.pyplot import thetagrids
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
from PySide6 import QtCore
from PySide6.QtCore import QDate, QTime, QTimer
from PySide6.QtGui import QImage, QMouseEvent, QTransform
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import (
    QDateEdit,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)
from skyfield.api import load, wgs84

import config
from services.tracker_service import TrackerService


class EarthMapView3D(QOpenGLWidget):
    def __init__(self, parent=None, quality=0):
        super(EarthMapView3D, self).__init__(parent)
        self.quality = quality
        self.y_rotate = 0.0
        # Create a QTimer
        self.timer = QTimer()
        # Connect the timer's timeout signal to the update method
        self.timer.timeout.connect(self.update)
        # Start the timer to trigger an update every 16 milliseconds
        self.timer.start(16)

        # Labels
        self.scale_label = QLabel()
        self.scale_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.scale_label.setMaximumSize(200, 50)
        self.scale_label.setMinimumSize(200, 50)

        # Camera Altitude Label
        self.cameraAltitude_label = QLabel()
        self.cameraAltitude_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.cameraAltitude_label.setMaximumSize(200, 50)
        self.cameraAltitude_label.setMinimumSize(200, 50)

        # Camera Position Label
        self.cameraPos_label = QLabel()
        self.cameraPos_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.cameraPos_label.setMaximumSize(200, 50)
        self.cameraPos_label.setMinimumSize(200, 50)

        self.frameCount = 0


        self.trackerService = TrackerService()

    def setQuality(self, quality):
        self.quality = quality
        self.loadTextures(self.quality)

    def initializeGL(self):
        # This method is called once upon the first time OpenGL context is available
        # Setup OpenGL state and resources
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)  # Enable texture mapping
        glEnable(GL_LIGHTING)   # Enable lighting
        glEnable(GL_LIGHT0)     # Enable light source 0
        glEnable(GL_COLOR_MATERIAL)  # Enable color materials
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)  # Set color materials to affect both ambient and diffuse components

        # Calculate the position of the sun
        self.sun_position = np.array([-7500, 10000, 10000])  # Sun position around the equator

        # Set the position of the light source to align with the sun
        glLightfv(GL_LIGHT0, GL_POSITION, [self.sun_position[0], self.sun_position[1], self.sun_position[2], 0])

        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 0.8, 1])  # Modify the diffuse color to make it more sun-like
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1, 1, 1, 1])
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.3, 0.3, 0.3, 1.0))
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0.6, 0.6, 0.6, 1.0))
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 100.0)

        self.tilt_axis = False
        self.spin = True

        # Load textures according to the quality setting
        self.loadTextures(self.quality)

        # base scale is kilometers
        self.scale = 1/1000 # scaled 1km:1000m
        self.unit = "m"

        self.earthRadius =       wgs84.radius.km # radius of the earth in km, a standard calculated by NASA in 1984 (6378.137 km)
        self.karman_line =       100 # altitude of the karman line in km, representing the edge of space
        self.cloud_height =      12 # height of the troposphere in km, where clouds are located and weather occurs
        self.renderDistance =    160000 # km
        self.starmapRadius =     80000 # km
        self.maxCameraAltitude = 70000 # maximum camera altitude in km
        self.minCameraAltitude = 10000 #km
        self.cameraZoom = 2000 #km scroll distance
        self.slowCameraZoom = 100 #km scroll distance for shift+scroll

        self.earthRadius = self.earthRadius * self.scale
        self.karman_line = self.karman_line * self.scale
        self.cloud_height = self.cloud_height * self.scale
        self.renderDistance = self.renderDistance * self.scale
        self.starmapRadius = self.starmapRadius * self.scale
        self.maxCameraAltitude = self.maxCameraAltitude * self.scale
        self.minCameraAltitude = self.minCameraAltitude * self.scale
        self.cameraZoom = self.cameraZoom * self.scale
        self.slowCameraZoom = self.slowCameraZoom * self.scale

        self.isDragging = False
        self.lastPos = QtCore.QPoint()
        self.lastPosX = 0
        self.lastPosY = 0
        self.theta = 0
        self.phi = 0
        self.cameraAltitude = (self.maxCameraAltitude + self.minCameraAltitude) / 2
        # 40,000 km above the earth

        self.translations = []
        self.translations2 = []

        self.cameraPosX = 0
        self.cameraPosY = 0
        self.cameraPosZ = 5

        # bind mouse click and drag events
        self.mousePressEvent = self.mouseButton
        self.mouseReleaseEvent = self.mouseButton
        self.mouseMoveEvent = self.mouseMove

        self.updateCamera(0, 0, self.cameraAltitude)

    def loadTextures(self, quality):
        if quality == 0:
            glShadeModel(GL_FLAT)
            self.earth_daymap = self.loadTexture(imagePath=os.path.join(config.map_textures, "2k_earth_daymap.jpg"))
            self.earth_clouds = self.loadTexture(imagePath=os.path.join(config.map_textures, "2k_earth_clouds.jpg"))
            self.earth_specular = self.loadTexture(imagePath=os.path.join(config.map_textures, "2k_earth_specular_map.tif"))
            self.stars_milky_way = self.loadTexture(imagePath=os.path.join(config.map_textures, "2k_stars_milky_way.jpg"))
            self.earth_nightmap = self.loadTexture(imagePath=os.path.join(config.map_textures, "2k_earth_nightmap.jpg"))

        elif quality == 1:
            glShadeModel(GL_SMOOTH)
            self.earth_daymap = self.loadTexture(imagePath=os.path.join(config.map_textures, "8k_earth_daymap.jpg"))
            self.earth_clouds = self.loadTexture(imagePath=os.path.join(config.map_textures, "8k_earth_clouds.jpg"))
            self.stars_milky_way = self.loadTexture(imagePath=os.path.join(config.map_textures, "8k_stars_milky_way.jpg"))
            self.earth_nightmap = self.loadTexture(imagePath=os.path.join(config.map_textures, "8k_earth_nightmap.jpg"))

        elif quality == 2:
            glShadeModel(GL_SMOOTH)
            self.earth_clouds = self.loadTexture(imagePath=os.path.join(config.map_textures, "clouds-alpha.png"))
            self.earth_specular = self.loadTexture(imagePath=os.path.join(config.map_textures, "specular.jpg"))
            self.earth_daymap = self.loadTexture(imagePath=os.path.join(config.map_textures, "land_ocean_ice_8192.png"))
            self.stars_milky_way = self.loadTexture(imagePath=os.path.join(config.map_textures, "8k_stars_milky_way.jpg"))
            self.earth_nightmap = self.loadTexture(imagePath=os.path.join(config.map_textures, "8k_earth_nightmap.jpg"))

    def loadTexture(self, imagePath):
        image = Image.open(imagePath)
        image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)  # Flip the image
        imageData = np.array(list(image.getdata()), np.uint8)  # Convert to numpy array

        # Generate a texture ID
        textureID = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, textureID)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        # Upload the texture data
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, imageData)
        return textureID

    # code enabling the camera to be rotated around the earth via mouse dragging on the screen
    def updateCamera(self, theta, phi, cameraAltitude):
        # clamp camera looking up or down too far
        if phi > 89:
            phi = 89
        if phi < -89:
            phi = -89

        # convert zoom to scaled elevation around the geoid (wgs84 radius)

        cameraAltitude = max(cameraAltitude, self.minCameraAltitude)
        cameraAltitude = min(cameraAltitude, self.maxCameraAltitude)

        # Update the camera position based on the current theta and phi values, which represent the camera's spherical coordinates
        theta_rad = radians(theta)
        phi_rad = radians(phi)

        # Calculate the camera position on the sphere
        self.cameraPosX = cameraAltitude * sin(-theta_rad) * cos(-phi_rad)
        self.cameraPosY = cameraAltitude * sin(phi_rad)
        self.cameraPosZ = cameraAltitude * cos(-theta_rad) * cos(-phi_rad)

        # Calculate the point to look at
        lookAtX = 0  # X coordinate of the point to look at
        lookAtY = 0  # Y coordinate of the point to look at
        lookAtZ = 0  # Z coordinate of the point to look at

        # Adjust camera position based on earth's tilt
        if self.tilt_axis:
            self.cameraPosX *= cos(radians(23.5))
            self.cameraPosZ *= cos(radians(23.5))

        self.cameraAltitude = cameraAltitude

    def mouseMove(self, event=QMouseEvent):
        if self.isDragging:
            dx = self.lastPosX - event.pos().x()
            dy = self.lastPosY - event.pos().y()

            self.theta -= dx / 2
            self.phi -= dy / 2
            self.updateCamera(self.theta, self.phi, self.cameraAltitude)

            self.lastPos = event.pos()
            self.lastPosX = event.pos().x()
            self.lastPosY = event.pos().y()

    def mouseButton(self, event=QMouseEvent):
        button = event.button()
        if button == QtCore.Qt.MouseButton.LeftButton:
            if event.type() == QtCore.QEvent.Type.MouseButtonPress:
                self.isDragging = True
                self.lastPos = event.pos()
                self.lastPosX = event.pos().x()
                self.lastPosY = event.pos().y()
            elif event.type() == QtCore.QEvent.Type.MouseButtonRelease:
                self.isDragging = False

    def wheelEvent(self, event=QMouseEvent):
        # Zoom in and out based on the mouse wheel
        # Interpolate the scroll distance based on the current camera altitude
        t = (self.cameraAltitude - self.minCameraAltitude) / (self.maxCameraAltitude - self.minCameraAltitude)
        interpolatedScrollDistance = (1 - t) * self.slowCameraZoom + t * self.cameraZoom * 2

        if event.angleDelta().y() > 0:
            self.cameraAltitude -= interpolatedScrollDistance
        else:
            self.cameraAltitude += interpolatedScrollDistance

        self.cameraAltitude = max(self.cameraAltitude, self.minCameraAltitude)
        self.cameraAltitude = min(self.cameraAltitude, self.maxCameraAltitude)

        self.updateCamera(self.theta, self.phi, self.cameraAltitude)

    def resizeGL(self, width, height):
        # Update projection matrix on resize
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / float(height), 1, self.renderDistance)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def drawSkybox(self):
        # disable lighting and depth masks because we want the skybox to be drawn behind everything
        glDisable(GL_LIGHTING)
        glDepthMask(GL_FALSE)
        glPushMatrix()

        # GL_TEXTURE0 = stars skybox texture
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.stars_milky_way)

        # Draw the skybox as a sphere
        glTranslatef(0, 0, 0)
        glScalef(-1, 1, 1)
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, self.starmapRadius, 32, 32)

        # re-enable lighting and depth masks for the earth
        glPopMatrix()
        glEnable(GL_LIGHTING)
        glDepthMask(GL_TRUE)

    def drawEquator(self):
        # Draw the equator
        glLineWidth(3.0)
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_LINE_LOOP)
        for i in range(360):
            theta = i * 3.14159 / 180
            glVertex3f(cos(theta), sin(theta), 0)
        glEnd()

    def drawPoles(self):
        # Draw the poles
        glLineWidth(3.0)
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 1.5)
        glVertex3f(0, 0, -1.5)
        glEnd()

    def drawAtmosphere(self):
        # Draw the atmosphere

        # texture of clouds
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.earth_clouds)

        glDepthMask(GL_FALSE)
        glDisable(GL_LIGHTING)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glEnable(GL_BLEND)
        glColor4f(1.0, 1.0, 1.0, 0.5)
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        cloud_height_above_earth = self.cloud_height + self.earthRadius
        gluSphere(quadric, cloud_height_above_earth, 256, 256)

        # draw the karman line as a opacity sphere
        glColor4f(1.0, 1.0, 1.0, 0.05)
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_FALSE)
        gluSphere(quadric, self.karman_line + self.earthRadius, 256, 256)

        #reset to default
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
        glDepthMask(GL_TRUE)




    def drawEarth(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.earth_daymap)

        # draw earth sphere
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)  # Enable texture mapping
        gluSphere(quadric, self.earthRadius, 256, 256)

    def calcSatelliteOrbit(self, satellite_name):
        satellite = []
        satellite.append(self.trackerService.fetch_or_use_local_tle(satellite_name))
        points = self.trackerService.calculate_orbit_points_around_globe(satellite[0])
        translations = []
        for point in points:
            theta = point.longitude.degrees
            phi = point.latitude.degrees

            elevation = self.earthRadius + point.elevation.km

            translations.append([elevation * cos(radians(phi)) * cos(radians(theta)),
                                 elevation * cos(radians(phi)) * sin(radians(theta)),
                                 elevation * sin(radians(phi))])

        return translations

    def calcSatellitePositionAtTime(self, satellite_name, time):
        points = self.trackerService.calculate_satellite_position_at_time(self.trackerService.fetch_or_use_local_tle(satellite_name), time)
        translations = []
        for point in points:
            theta = point.longitude.degrees
            phi = point.latitude.degrees

            elevation = self.earthRadius + point.elevation.km

            translations.append([elevation * cos(radians(phi)) * cos(radians(theta)),
                                 elevation * cos(radians(phi)) * sin(radians(theta)),
                                 elevation * sin(radians(phi))])

        return translations

    def drawSatelliteOrbit(self):
        if not self.translations:
            self.translations = self.calcSatelliteOrbit("ISS (ZARYA)")

        glDisable(GL_LIGHTING)
        glPushMatrix()
        glLineWidth(2.0)
        glColor4f(0.5, 0.5, 0.5, 0.5)  # opacity grey
        glBegin(GL_LINE_STRIP)
        for translation in self.translations:
            glVertex3f(translation[0], translation[1], translation[2])  # Place a vertex at the translated position
        glEnd()

        # reset color, lighting, and matrix
        glPopMatrix()
        glEnable(GL_LIGHTING)
        glColor(1.0, 1.0, 1.0)

    def drawSatellitePosition(self):

        if self.frameCount % 60 == 0:
            self.translations = self.calcSatellitePositionAtTime("ISS (ZARYA)", self.trackerService.getTime())
        glDisable(GL_LIGHTING)
        glColor3f(1.0, 0.0, 0.0)  # red

        for translation in self.translations:
            glPushMatrix()
            glTranslatef(translation[0], translation[1], translation[2])
            quadric = gluNewQuadric()
            gluQuadricTexture(quadric, GL_FALSE)
            gluSphere(quadric, 0.1, 16, 16)
            glPopMatrix()

        # reset color, lighting, and matrix
        glEnable(GL_LIGHTING)
        glColor(1.0, 1.0, 1.0)

    def updateLabels(self):
        self.scale_label.setText(f"Scale: 1km : {int(1/self.scale)} {self.unit}")
        self.cameraAltitude_label.setText(f"Altitude: {round(self.cameraAltitude, 0) / self.scale} km")
        self.cameraPos_label.setText(f"Position: ({round(self.cameraPosX, 0)}, {round(self.cameraPosY, 0)}, {round(self.cameraPosZ, 0)})")


    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluLookAt(self.cameraPosX, self.cameraPosY, self.cameraPosZ, 0, 0, 0, 0, 1, 0)

        self.drawSkybox()

        # y-axis alignment
        glRotatef(-90, 1, 0, 0)

        # earth matrix
        glPushMatrix()
        #glRotatef(23.5, 0, 1, 0)
        #glRotatef(self.y_rotate, 0, 0, 1)
        self.y_rotate += .025
        self.drawEarth()
        #glRotatef(self.y_rotate/1.025, 0, 0, 1)
        self.drawAtmosphere()
        #self.drawEquator()
        #self.drawPoles()
        glPopMatrix()

        # orbit matrix
        glPushMatrix()
        self.drawSatellitePosition()
        glPopMatrix()

        glPushMatrix()
        self.frameCount += 1
        if self.frameCount % 5 == 0:

            #self.drawSatelliteOrbit()
            self.updateLabels()
        glPopMatrix()