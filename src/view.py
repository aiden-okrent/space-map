import glob
import os
from math import cos, e, pi, radians, sin, sqrt
from typing import TYPE_CHECKING

import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PySide6 import QtCore
from PySide6.QtGui import QImage, QMouseEvent, QTransform
from PySide6.QtOpenGLWidgets import QOpenGLWidget

'''
In MVC, the view is the part of the application that is responsible for displaying the data to the user, and for receiving user input.
The view is not aware of the model, so it does not directly interact with the data. It sends and receives data through the controller.

For space-map, the View has several components:
- MainWindow: The base gui which is empty except for the toolbar. Its job is to serve as a container.
- GlobeView: Responsible for the 3D rendering of the Earth and Satellites. Its front and center as its the main feature of the application.
- ControlPanel: A side panel containing user inputs and associated information.

'''

from enum import Enum

from PySide6.QtCore import (
    QDateTime,
    QEvent,
    QPoint,
    QRect,
    QSettings,
    QSize,
    Qt,
    QTimer,
)
from PySide6.QtGui import QFont, QIntValidator
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QApplication,
    QCalendarWidget,
    QComboBox,
    QDateTimeEdit,
    QDockWidget,
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QPlainTextDocumentLayout,
    QProxyStyle,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QStyle,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
from skyfield.toposlib import GeographicPosition
from skyfield.units import Angle, Distance

from controller_protocol import ControllerProtocol


class AbstractWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.settings = QSettings()
        self.settingsGroup = "default"

    def saveSettings(self):
        self.settings.beginGroup(self.settingsGroup)

        self.settings.setValue("windowState", self.windowState())  # Qt.WindowState
        if not self.windowState() & Qt.WindowState.WindowMaximized:
            self.settings.setValue("size", self.size())  # QSize
            self.settings.setValue("position", self.pos())  # QPoint

        self.settings.endGroup()

    def restoreSettings(self):
        self.settings.beginGroup(self.settingsGroup)
        self.move(self.settings.value("position", QPoint()))
        self.resize(self.settings.value("size", QSize()))
        self.settings.setValue("position", self.pos())  # QPoint
        self.settings.setValue("windowState", self.windowState())  # Qt.WindowState
        self.settings.endGroup()

        self.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            QApplication.quit()
        else:
            super().keyPressEvent(event)

    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            self.saveSettings()
        super().changeEvent(event)

    def closeEvent(self, event):
        self.saveSettings()
        super().closeEvent(event)

class MainView(AbstractWindow):
    def __init__(self, controller: ControllerProtocol):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Space Map")
        self.settingsGroup = str(self.windowTitle())
        self.initUI()

    def initUI(self):
        # topBar
        self.topBar = QToolBar()
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.topBar)
        self.topBar.addSeparator()

        # Setup the main widget and layout for the satellite input
        self.current_sat_input = QWidget()
        self.current_sat_input_layout = QHBoxLayout()
        self.current_sat_input_layout.setContentsMargins(0, 0, 0, 0)
        self.current_sat_input.setLayout(self.current_sat_input_layout)

        # Create and configure the satellite tracking label
        self.current_sat_label = QLabel("Tracking Satellite:   ")
        self.current_sat_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.current_sat_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Create and configure the satellite tracking input
        class IDSpinBox(QSpinBox): # Custom QSpinBox to display leading zeros
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setRange(0, 99999)
                self.setFixedWidth(75)
                self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
                self.setFrame(False)
                self.setAlignment(Qt.AlignmentFlag.AlignLeft)
                self.setAlignment(Qt.AlignmentFlag.AlignVCenter)
                self.setKeyboardTracking(False)

            def textFromValue(self, value):
                return "%05d" % value

        self.current_sat_id_spinbox = IDSpinBox()
        self.current_sat_id_spinbox.editingFinished.connect(self.current_sat_id_spinbox.clearFocus)

        class MyProxyStyle(QProxyStyle):
            def styleHint(self, hint, option=None, widget=None, returnData=None):
                if hint == QStyle.SH_ComboBox_Popup:
                    return 0
                return super().styleHint(hint, option, widget, returnData)

        class MyComboBox(QComboBox):
            def __init__(self):
                super().__init__()

            def showPopup(self):
                super().showPopup()
                popup = self.view().window()
                width = self.width()
                height = 200
                popup.resize(width, height)
                popup.move(self.mapToGlobal(self.rect().bottomLeft()))  # Reposition the popup window

        self.satellite_combobox = MyComboBox()
        self.satellite_combobox.setInsertPolicy(QComboBox.InsertPolicy.InsertAtTop)
        self.satellite_combobox.setStyle(MyProxyStyle())

        # Add widgets to the layout
        self.current_sat_input_layout.addWidget(self.satellite_combobox)
        self.current_sat_input_layout.addWidget(self.current_sat_id_spinbox)
        self.current_sat_input_layout.addStretch(1)

        # Connect mouse event to spinbox for focus management
        self.mousePressEvent = lambda event: self.current_sat_id_spinbox.clearFocus() if self.current_sat_id_spinbox.hasFocus() else None

        # Add actions to the topBar
        self.topBar.addWidget(self.current_sat_input)
        self.quality_Action = self.topBar.addAction("Switch Quality", self.controller.toggle_quality)
        self.display_2D_map_Action = self.topBar.addAction("2D Map", self.controller.display_2D_map)
        self.currentScene_Action = self.topBar.addAction("Switch Scene", self.controller.toggle_scene)
        self.cameraMode_Action = self.topBar.addAction("Switch Camera Mode", self.controller.toggle_camera_mode)

class TransparentOverlayView(QWidget):
    def __init__(self, controller: ControllerProtocol, globe3DView: QOpenGLWidget):
        super().__init__(globe3DView)
        self.controller = controller
        self.globe3DView = globe3DView
        self.initUI()

    def initUI(self):
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setStyleSheet("background: transparent;")  # Set background to transparent

        self.layout = QVBoxLayout(self)
        #self.layout.setContentsMargins(0, 0, 0, 0)
        #self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)

        self.labels = {}

        self.labels["RenderSettings"] = self.drawLabel("RenderSettings", "")
        self.labels["CameraStats"] = self.drawLabel("CameraStats", "")
        self.labels["CameraXYZ"] = self.drawLabel("CameraXYZ", "")
        self.labels["CameraTarget"] = self.drawLabel("CameraTarget", "")



    def toggleVisibility(self):
        self.setVisible(not self.isVisible())

    def update(self):
        self.drawRenderSettings()
        self.drawCameraStats()
        self.drawCameraXYZ()
        self.drawCameraTarget()

    def drawLabel(self, name, text):
        # Create a new label for the overlay
        label = QLabel(name, self)
        label.setStyleSheet("color: white; font-size: 24px;")
        label.setText(text)
        self.layout.addWidget(label)
        return label

    def drawRenderSettings(self):
        quality = self.globe3DView.getQuality()
        scene = self.globe3DView.getScene()
        self.labels["RenderSettings"].setText(f"Quality: {quality}, Scene: {scene}")

    def drawCameraStats(self):
        camera_mode = self.globe3DView.camera.getCameraMode()
        camera_distance = self.globe3DView.cameraDistance
        camera_altitude = camera_distance - self.globe3DView.Earth.radius.km
        self.labels["CameraStats"].setText(f"Mode: {camera_mode}\nAlt: {camera_altitude:.0f} km high")

    def drawCameraXYZ(self):
        x, y, z = self.globe3DView.cameraPosXYZ
        self.labels["CameraXYZ"].setText(f"Camera XYZ: ({x:.1f}, {y:.1f}, {z:.1f})")

    def drawCameraTarget(self):
        target = self.globe3DView.cameraTarget
        name = target["name"]
        position = target["position"]
        x = f"{position[0]:.0f}"
        y = f"{position[1]:.0f}"
        z = f"{position[2]:.0f}"

        self.labels["CameraTarget"].setText(f"Target: {target['name']}\nPosition: ({x}, {y}, {z})")



class Globe3DView(QOpenGLWidget):
    """ Render a 3D globe using OpenGL, with different scenes such as GLOBE_VIEW, TRACKING_VIEW, and EXPLORE_VIEW."""
    def __init__(self, controller: ControllerProtocol, earth):
        super().__init__()
        self.controller = controller
        self.renderDistance = 33000
        self.camera = self.Camera(controller, self, earth)
        self.Earth = earth

        self.overlay = TransparentOverlayView(self.controller, self)
        self.overlay.setGeometry(self.rect())

        self.quality = self.RenderQuality.DEBUG
        self.current_scene = self.SceneView
        self.setScene(self.SceneView.EXPLORE_VIEW)

        self.runtime = QTimer(self)
        self.runtime.timeout.connect(self.update) # run 'onRuntime' when timer ends

        self.satellite_position = None
        self.frame_count = 0

        # camera orbit settings
        self.lastPos = QPoint()
        self.cameraDistance = 0
        self.theta = 0
        self.phi = 0
        self.maxCameraAltitude = self.Earth.radius.km * 50
        self.minCameraAltitude = self.Earth.radius.km + 1
        self.isDragging = False
        self.cameraPosXYZ = [0, 0, 20]
        self.cameraTarget = {"name": "", "position": [0, 0, 0]}

        self.orbitDistance = self.Earth.radius.km + 10

        self.mousePressEvent = self.mousePressEvent
        self.mouseMoveEvent = self.mouseMoveEvent
        self.mouseReleaseEvent = self.mouseReleaseEvent


    def run(self):
        self.runtime.start(16) # 60fps

    # Init OpenGL view
    def initializeGL(self):

        glEnable(GL_DEPTH_TEST) # Enable depth testing
        glEnable(GL_TEXTURE_2D) # Enable texture mapping
        glEnable(GL_LIGHTING) # Enable lighting
        glEnable(GL_LIGHT0) # Enable light source 0
        glEnable(GL_COLOR_MATERIAL)  # Enable color materials
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE) # Set color materials to affect both ambient and diffuse components

        self.loadTextures(self.quality) # Set the textures based on the quality

        # sun light0 settings
        sun_position = np.array([-75, 100, 100]) # above and to the right of the Earth
        glLightfv(GL_LIGHT0, GL_POSITION, [sun_position[0], sun_position[1], sun_position[2], 0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1]) # ambient: gray
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 0.8, 1]) # diffuse: yellow
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1, 1, 1, 1]) # specular: white

        # material settings
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.3, 0.3, 0.3, 1.0)) # ambient: gray
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0.6, 0.6, 0.6, 1.0)) # diffuse: gray
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0)) # specular: white
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 100.0) # shininess: 100 MAX

    def toggleOverlayVisibility(self):
        return self.overlay.toggleVisibility()

    def setCameraTarget(self, target, position):
        self.cameraTarget = {"name": target, "position": position}
        self.orbitDistance = 20 if target == "Earth" else 1

    # Every frame, draw the OpenGL scene
    def paintGL(self):
        self.overlay.update()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # Clear the color and depth buffers
        glLoadIdentity() # Reset the modelview matrix to the identity matrix
        self.drawSkybox()

        # draw the current scene
        self.camera.update()
        if self.current_scene == self.SceneView.GLOBE_VIEW:
            self.drawScene_GLOBE_VIEW()
        if self.current_scene == self.SceneView.TRACKING_VIEW:
            self.drawScene_TRACKING_VIEW()
        elif self.current_scene == self.SceneView.EXPLORE_VIEW:
            self.drawScene_EXPLORE_VIEW()

    def drawScene_GLOBE_VIEW(self):
        self.setCameraTarget("Earth", [0, 0, 0])
        self.drawEarth()

    def drawScene_TRACKING_VIEW(self):
        satellite = self.controller.current_satellite # get the current satellite object to track
        if self.satellite_position is None:
            self.satellite_position = self.Earth.get3DCartesianCoordinates(satellite, self.controller.Timescale.now())
        else:
            if self.frame_count % 3 == 0:
                self.satellite_position = self.Earth.get3DCartesianCoordinates(satellite, self.controller.Timescale.now())
        self.frame_count += 1

        self.setCameraTarget(satellite.name, self.satellite_position)
        self.drawEarth()
        self.drawSatellite(self.satellite_position)


    def drawScene_EXPLORE_VIEW(self):
        self.setCameraTarget("Earth", [0, 0, 0])
        self.drawEarth()


    def drawSatellite(self, position):
        """ Draw the satellite at the given position. """
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
        glDepthMask(GL_TRUE)

        glColor4f(1.0, 0, 0, 1.0) # Red color for the satellite
        glPushMatrix()
        glTranslatef(*position)
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_FALSE)
        gluSphere(quadric, 0.01, self.earth_triangles, self.earth_triangles)
        glPopMatrix()

        glPushMatrix()
        surface_position = normalize(position) * self.controller.Earth.radius.km
        glTranslatef(*surface_position)
        glColor4f(1.0, 0, 0, 1.0) # Red color for the satellite
        gluSphere(quadric, 0.01, self.earth_triangles, self.earth_triangles)
        glPopMatrix()


        glPushMatrix() #draw a straight line that points through the center of the earth
        glBegin(GL_LINES)
        glColor4f(1.0, 1.0, 1.0, 1.0) # White color for the line
        glVertex3f(*position)
        inverted_position = [-x for x in position]
        glVertex3f(*inverted_position)
        glEnd()
        glPopMatrix()

        # reset color, lighting, and matrix
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glEnable(GL_LIGHTING)
        glDepthMask(GL_TRUE)
    def drawClouds(self):
        # draw clouds
        glDepthMask(GL_FALSE)
        glDisable(GL_LIGHTING)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glEnable(GL_BLEND)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.earth_clouds)
        glColor4f(1.0, 1.0, 1.0, 0.5)

        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, self.controller.Earth.troposphere, self.earth_triangles, self.earth_triangles)

        #glBlendFunc(GL_ONE, GL_ZERO)
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
        glDepthMask(GL_TRUE)
        glColor4f(1.0, 1.0, 1.0, 1)
    def drawKarmanLine(self):
        # draw the karman line, official boundary of space at 100km
        glDepthMask(GL_FALSE)
        glDisable(GL_LIGHTING)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glEnable(GL_BLEND)
        glColor4f(1.0, 1.0, 1.0, 0.5)

        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_FALSE)
        gluSphere(quadric, self.controller.Earth.karman_line, self.earth_triangles, self.earth_triangles)

        #glBlendFunc(GL_ONE, GL_ZERO)
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
        glDepthMask(GL_TRUE)
        glColor4f(1.0, 1.0, 1.0, 1)

    def setScene(self, scene):
        # Set the current scene
        if scene == self.SceneView.GLOBE_VIEW:
            self.to_GLOBE_VIEW()
        elif scene == self.SceneView.TRACKING_VIEW:
            self.to_TRACKING_VIEW()
        elif scene == self.SceneView.EXPLORE_VIEW:
            self.to_EXPLORE_VIEW()

        #self.current_scene = scene

    def to_GLOBE_VIEW(self):
        self.camera.setCameraMode(self.camera.CameraMode.STATIC)
        self.current_scene = self.SceneView.GLOBE_VIEW

    def to_TRACKING_VIEW(self):
        self.camera.setCameraMode(self.camera.CameraMode.FOLLOW)
        self.current_scene = self.SceneView.TRACKING_VIEW

    def to_EXPLORE_VIEW(self):
        self.camera.setCameraMode(self.camera.CameraMode.ORBIT)
        self.current_scene = self.SceneView.EXPLORE_VIEW


    def getScene(self):
        # Get the current scene
        return self.current_scene
    class SceneView(Enum):
        """ Enum for the different scenes that can be rendered in Globe3DView"""
        GLOBE_VIEW = 0
        TRACKING_VIEW = 1
        EXPLORE_VIEW = 2

        def __str__(self):
            return self.name

    def loadTextures(self, quality):
        if quality == self.RenderQuality.LOW:
            print("Setting quality to low")
            glShadeModel(GL_FLAT)
            self.earth_triangles = 16
            self.lighting_enabled = False
            self.earth_daymap = self.unpackImageToTexture(imagePath=self.controller.Earth.textures_2k["earth_daymap"])
            self.stars_milky_way = self.unpackImageToTexture(imagePath=self.controller.Earth.textures_2k["stars_milky_way"])
            self.earth_clouds = self.unpackImageToTexture(imagePath=self.controller.Earth.textures_2k["earth_clouds"])

        elif quality == self.RenderQuality.HIGH:
            print("Setting quality to high")
            glShadeModel(GL_SMOOTH)
            self.earth_triangles = 32
            self.lighting_enabled = True
            self.earth_daymap = self.unpackImageToTexture(imagePath=self.controller.Earth.textures_8k["earth_daymap"])
            self.stars_milky_way = self.unpackImageToTexture(imagePath=self.controller.Earth.textures_8k["stars_milky_way"])
            self.earth_clouds = self.unpackImageToTexture(imagePath=self.controller.Earth.textures_8k["earth_clouds"])

        elif quality == self.RenderQuality.DEBUG:
            print("Setting quality to debug")
            glShadeModel(GL_FLAT)
            self.earth_triangles = 16
            self.lighting_enabled = False
            self.earth_daymap = self.unpackImageToTexture(imagePath=self.controller.Earth.textures_debug["earth_daymap"])
            self.stars_milky_way = self.unpackImageToTexture(imagePath=self.controller.Earth.textures_debug["stars_milky_way"])
            self.earth_clouds = self.unpackImageToTexture(imagePath=self.controller.Earth.textures_debug["earth_clouds"])

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
        #image = image.mirrored(True, False)  # Flip horizontally
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width(), image.height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, image.bits())
        return texture

    def drawEarth(self):

        glDepthMask(GL_TRUE) # Re-enable writing to the depth buffer
        glEnable(GL_LIGHTING) # Re-enable lighting
        glDisable(GL_BLEND)

        glEnable(GL_TEXTURE_2D)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.earth_daymap) # Bind active texture to Earth texture

        # draw earth sphere
        glColor4f(1.0, 1.0, 1.0, 1.0)
        #glRotatef(180, 0, 1, 0)
        self.drawSphereManual()
        #glRotatef(-180, 0, 1, 0)

    def drawXYZAxis(self):
        # draw XYZ axis
        glPushMatrix()
        glLineWidth(2)
        glBegin(GL_LINES)
        glColor4f(1.0, 0, 0, 1.0) # Red color for the X-axis
        glVertex3f(0, 0, 0)
        glVertex3f(1, 0, 0)
        glColor4f(0, 1.0, 0, 1.0) # Green color for the Y-axis
        glVertex3f(0, 0, 0)
        glVertex3f(0, 1, 0)
        glColor4f(0, 0, 1.0, 1.0) # Blue color for the Z-axis
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 1)
        glEnd()
        glPopMatrix()
        glColor4f(1.0, 1.0, 1.0, 1.0) # Reset color

    def drawSphereManual(self):
        # draw a sphere manually
        lat_steps = self.earth_triangles
        long_steps = lat_steps * 2


        radius = self.controller.Earth.radius.km

        glPushMatrix()

        # up = y, down = -y
        # right = x, left = -x
        # forward = z, backward = -z

        # rotate the earth to have positive y-axis pointing up
        glRotatef(90, 1, 0, 0)
        # yaw/turn right
        glRotatef(90, 0, 0, 1)



        glDepthMask(GL_TRUE)
        glEnable(GL_LIGHTING)
        glDisable(GL_BLEND)
        glEnable(GL_TEXTURE_2D)
        glActiveTexture(GL_TEXTURE0)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glBindTexture(GL_TEXTURE_2D, self.earth_daymap) # Bind active texture to Earth texture

        for i in range(lat_steps):
            lat0 = pi * (-0.5 + float(i) / lat_steps)
            z0 = sin(lat0)
            zr0 = cos(lat0)

            lat1 = pi * (-0.5 + float(i + 1) / lat_steps)
            z1 = sin(lat1)
            zr1 = cos(lat1)

            glBegin(GL_QUAD_STRIP)
            for j in range(long_steps + 1):
                lng = 2 * pi * float(j) / long_steps - pi
                x = cos(lng)
                y = sin(lng)

                # Adjust texture coordinates to flip the texture horizontally
                s = 1.0 - (lng + pi) / (2 * pi)
                t0 = i / lat_steps
                t1 = (i + 1) / lat_steps

                glTexCoord2f(s, t0)
                glNormal3f(x * zr0, y * zr0, z0)  # Set normal vector for lighting
                glVertex3f(radius * x * zr0, radius * y * zr0, radius * z0)

                glTexCoord2f(s, t1)
                glNormal3f(x * zr1, y * zr1, z1)  # Set normal vector for lighting
                glVertex3f(radius * x * zr1, radius * y * zr1, radius * z1)
            glEnd()

        glPopMatrix()

    def drawSkybox(self):
        """ Draw a skybox around the scene """
        glDisable(GL_LIGHTING) # Disable lighting for the skybox
        glDepthMask(GL_FALSE) # Disable writing to the depth buffer for the skybox, so it is always drawn behind other objects

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.stars_milky_way) # Bind active texture to stars texture

        # Draw the skybox as a sphere
        glPushMatrix()
        glTranslatef(0, 0, 0)
        glScalef(-1, 1, 1)
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, 16000, 32, 32)
        glPopMatrix()

        glDepthMask(GL_TRUE) # Re-enable writing to the depth buffer
        glEnable(GL_LIGHTING) # Re-enable lighting

    def resizeGL(self, width, height):
        """ Resize the OpenGL viewport, update the projection matrix, and set the POV Perspective """
        # Update projection matrix on resize
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / float(height), 1, self.renderDistance)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    def setQuality(self, quality):
        """ Set the render quality

        Args:
            quality (RenderQuality): The quality of the rendering: LOW or HIGH
        """
        if isinstance(quality, int):
            quality = self.RenderQuality(quality)
        self.quality = quality
        self.loadTextures(quality)
    def getQuality(self):
        """ Return current render quality setting

        Returns:
            RenderQuality: The current render quality setting: LOW or HIGH
        """
        return self.quality
    class RenderQuality(Enum):
        """ Enum for the different render qualities: LOW, HIGH, or DEBUG """
        LOW = 0
        HIGH = 1
        DEBUG = 2

        def __str__(self):
            return self.name.capitalize()

    def mousePressEvent(self, event: QMouseEvent):
        if self.camera.getCameraMode() == self.camera.CameraMode.ORBIT:
            if event.button() == Qt.MouseButton.LeftButton:
                self.isDragging = True
                self.lastPos = event.position()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.camera.getCameraMode() == self.camera.CameraMode.ORBIT:
            if self.isDragging:
                dx = event.x() - self.lastPos.x()
                dy = event.y() - self.lastPos.y()

                self.theta -= dx / 2
                self.phi += dy / 2
                self.updateOrbitCamera()

                self.lastPos = event.position()
                self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.camera.getCameraMode() == self.camera.CameraMode.ORBIT:
            if event.button() == Qt.MouseButton.LeftButton:
                self.isDragging = False

    def wheelEvent(self, event: QMouseEvent):
        if self.camera.getCameraMode() == self.camera.CameraMode.ORBIT:
            scrollDistance = event.angleDelta().y()
            t = (self.cameraDistance - self.minCameraAltitude) / (self.maxCameraAltitude - self.minCameraAltitude)
            interpolatedScrollDistance = scrollDistance * t
            self.cameraDistance = self.cameraDistance - interpolatedScrollDistance
            #self.updateOrbitCamera()
            #self.update()

    def updateOrbitCamera(self):
        if self.camera.getCameraMode() == self.camera.CameraMode.ORBIT:

            # clamp camera looking up or down too far
            if self.phi > 89:
                self.phi = 89
            if self.phi < -89:
                self.phi = -89

            max(min(self.cameraDistance, self.maxCameraAltitude), self.minCameraAltitude)

            if self.cameraDistance < self.minCameraAltitude:
                self.cameraDistance = self.minCameraAltitude

            phi_rad = radians(self.phi)
            theta_rad = radians(self.theta)

            target_pos = self.cameraTarget["position"]

            x = self.orbitDistance * sin(theta_rad) * cos(phi_rad) + target_pos[0]
            y = self.orbitDistance * sin(phi_rad) + target_pos[1]
            z = self.orbitDistance * cos(theta_rad) * cos(phi_rad) + target_pos[2]
            self.cameraPosXYZ = [x, y, z]
            self.update()

    class Camera:
        def __init__(self, controller, globe3DView, earth):
            self.controller = controller
            self.globe3DView = globe3DView
            self.Earth = earth
            self.mode = self.CameraMode.STATIC

        def update(self):
            if self.mode == self.CameraMode.STATIC:
                gluLookAt(self.Earth.radius.km + 1, 0, 0, 0, 0, 0, *self.controller.Earth.upVector)

            elif self.mode == self.CameraMode.FOLLOW:
                target = self.globe3DView.cameraTarget
                target_pos = target["position"]

                camera_pos = target_pos
                gluLookAt(*camera_pos, 0,0,0, *self.controller.Earth.upVector)

            elif self.mode == self.CameraMode.ORBIT:
                target = self.globe3DView.cameraTarget
                target_pos = target["position"]

                gluLookAt(*self.globe3DView.cameraPosXYZ, *target_pos, *self.controller.Earth.upVector)



        def setCameraMode(self, mode):
            if isinstance(mode, self.CameraMode):
                self.mode = mode
        def getCameraMode(self):
            if isinstance(self.mode, self.CameraMode):
                return self.mode
        class CameraMode(Enum):
            """ Enum for the different camera modes: STATIC, ORBIT, FOLLOW """
            STATIC = 0
            ORBIT = 1
            FOLLOW = 2



# Utility functions
def normalize(v):
    return v / np.linalg.norm(v)

def compute_normal_of_plane(v1, v2):
    return np.cross(v1, v2)

def look_at(eye, center, up):
    f = normalize(center - eye)  # forward
    s = normalize(np.cross(f, up))  # side
    u = np.cross(s, f)  # recalculate up

    # Create the corresponding rotation matrix
    M = np.identity(4)
    M[0, :3] = s
    M[1, :3] = u
    M[2, :3] = -f

    # Create the translation matrix
    T = np.identity(4)
    T[:3, 3] = -eye

    # Combine rotation and translation into a single matrix
    return np.dot(M, T)

def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    axis = np.asarray(axis)
    axis = axis / np.sqrt(np.dot(axis, axis))
    a = np.cos(theta / 2.0)
    b, c, d = -axis * np.sin(theta / 2.0)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
    return np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                     [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                     [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])