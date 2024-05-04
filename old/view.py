import os
import re
from datetime import timedelta
from math import cos, e, pi, radians, sin, sqrt
from typing import TYPE_CHECKING

import numpy as np
from bidict import inverted
from OpenGL.GL import *
from OpenGL.GLU import *
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

from controller_protocol import ControllerProtocol
from PySide6 import QtSvg
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
from PySide6.QtGui import QColor, QFont, QIntValidator, QPainter, QPixmap
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QApplication,
    QCalendarWidget,
    QComboBox,
    QDateTimeEdit,
    QDialog,
    QDockWidget,
    QDoubleSpinBox,
    QFormLayout,
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
from skyfield.timelib import Time
from skyfield.toposlib import GeographicPosition
from skyfield.units import Angle, Distance, Velocity


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

        self.quality_combobox = QComboBox()
        self.quality_combobox.setStyle(MyProxyStyle())

        self.ctrl_dock_widget = QDockWidget("Parameters", self)
        self.ctrl_widget = QWidget()
        self.ctrl_layout = QVBoxLayout()
        self.ctrl_widget.setLayout(self.ctrl_layout)

        self.ctrl_dock_widget.setWidget(self.ctrl_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.ctrl_dock_widget)

        orbitpath_grp = QGroupBox("Orbit Path")
        orbitpath_grp_layout = QFormLayout()
        orbitpath_grp.setLayout(orbitpath_grp_layout)


        self.hours_behind_spinbox = QDoubleSpinBox()
        self.hours_behind_spinbox.setRange(0, 7*24)
        self.hours_behind_spinbox.setSingleStep(0.5)
        self.hours_behind_spinbox.setDecimals(1)
        self.hours_behind_spinbox.setValue(0.5)
        self.hours_behind_spinbox.setPrefix("")
        self.hours_behind_spinbox.setSuffix(" hrs")
        self.hours_behind_spinbox.valueChanged.connect(lambda: self.hours_behind_spinbox.setSuffix(" hr ") if self.hours_behind_spinbox.value() == 1 else self.hours_behind_spinbox.setSuffix(" hrs"))
        self.hours_behind_spinbox.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.hours_behind_spinbox.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.hours_behind_spinbox.setContentsMargins(0, 0, 0, 0)

        self.hours_ahead_spinbox = QDoubleSpinBox()
        self.hours_ahead_spinbox.setRange(0, 7*24)
        self.hours_ahead_spinbox.setSingleStep(0.5)
        self.hours_ahead_spinbox.setDecimals(1)
        self.hours_ahead_spinbox.setValue(0.5)
        self.hours_ahead_spinbox.setPrefix("")
        self.hours_ahead_spinbox.setSuffix(" hrs")
        self.hours_ahead_spinbox.valueChanged.connect(lambda: self.hours_ahead_spinbox.setSuffix(" hr ") if self.hours_ahead_spinbox.value() == 1 else self.hours_ahead_spinbox.setSuffix(" hrs"))
        self.hours_ahead_spinbox.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.hours_ahead_spinbox.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.hours_ahead_spinbox.setContentsMargins(0, 0, 0, 0)

        self.increment_spinbox = QDoubleSpinBox()
        self.increment_spinbox.setRange(1, 60)
        self.increment_spinbox.setSingleStep(5)
        self.increment_spinbox.setDecimals(0)
        self.increment_spinbox.setValue(2)
        self.increment_spinbox.setPrefix("")
        self.increment_spinbox.setSuffix(" mins")
        self.increment_spinbox.valueChanged.connect(lambda: self.increment_spinbox.setSingleStep(4) if self.increment_spinbox.value() == 1 else self.increment_spinbox.setSingleStep(5))
        self.increment_spinbox.valueChanged.connect(lambda: self.increment_spinbox.setSuffix(" min ") if self.increment_spinbox.value() == 1 else self.increment_spinbox.setSuffix(" mins"))
        self.increment_spinbox.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.increment_spinbox.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.increment_spinbox.setContentsMargins(0, 0, 0, 0)



        hrs_behind_row = QHBoxLayout()
        hrs_behind_row.setSpacing(0)
        hrs_behind_prefix = QLabel("-")
        hrs_behind_row.addWidget(hrs_behind_prefix)
        hrs_behind_row.addWidget(self.hours_behind_spinbox)

        hrs_ahead_row = QHBoxLayout()
        hrs_ahead_row.setSpacing(0)
        hrs_ahead_prefix = QLabel("+")
        hrs_ahead_row.addWidget(hrs_ahead_prefix)
        hrs_ahead_row.addWidget(self.hours_ahead_spinbox)

        orbitpath_grp_layout.addRow("Past", hrs_behind_row)
        orbitpath_grp_layout.addRow("Future", hrs_ahead_row)
        orbitpath_grp_layout.addRow("Resolution", self.increment_spinbox)
        self.ctrl_layout.addWidget(orbitpath_grp)
        self.ctrl_layout.addStretch(1)



        self.mousePressEvent = lambda event: self.increment_spinbox.clearFocus() if self.increment_spinbox.hasFocus() else None
        self.mousePressEvent = lambda event: self.hours_ahead_spinbox.clearFocus() if self.hours_ahead_spinbox.hasFocus() else None
        self.mousePressEvent = lambda event: self.hours_behind_spinbox.clearFocus() if self.hours_behind_spinbox.hasFocus() else None

        self.increment_spinbox.editingFinished.connect(self.increment_spinbox.clearFocus)
        self.hours_ahead_spinbox.editingFinished.connect(self.hours_ahead_spinbox.clearFocus)
        self.hours_behind_spinbox.editingFinished.connect(self.hours_behind_spinbox.clearFocus)

        # Add actions to the topBar
        self.topBar.addWidget(self.current_sat_input)
        self.topBar.addWidget(self.quality_combobox)
        self.display_2D_map_Action = self.topBar.addAction("2D Map", self.controller.display_2D_map)

class TransparentOverlayView(QWidget):
    def __init__(self, controller: ControllerProtocol, globe3DView: QOpenGLWidget):
        super().__init__(globe3DView)
        self.controller = controller
        self.globe3DView = globe3DView
        self.initUI()

    def initUI(self):
        self.setVisible(False)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setStyleSheet("background: transparent;")  # Set background to transparent

        self.layout = QVBoxLayout(self)
        #self.layout.setContentsMargins(0, 0, 0, 0)
        #self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)

        self.labels = {}

        self.labels["Scene"] = self.drawLabel("RenderSettings", "")
        self.labels["CameraMode"] = self.drawLabel("CameraMode", "")
        self.labels["CameraTarget"] = self.drawLabel("CameraTarget", "")
        self.labels["2DCartesianCoordinates"] = self.drawLabel("2DCartesianCoordinates", "")
        self.labels["CurrentTime"] = self.drawLabel("CurrentTime", "")
        self.labels["TargetSunlit"] = self.drawLabel("TargetSunlit", "")

    def setVisibility(self, visible):
        self.setVisible(visible)

    def update(self):
        self.drawRenderSettings()
        self.drawCameraTarget()
        self.draw2DCartesianCoordinates()
        self.drawCurrentTime()
        self.drawTargetSunlit()


    def drawLabel(self, name, text):
        # Create a new label for the overlay
        label = QLabel(name, self)
        label.setStyleSheet("color: white; font-size: 20px;")
        label.setText(text)
        self.layout.addWidget(label)
        return label

    def drawRenderSettings(self):
        scene = self.globe3DView.getScene()
        self.labels["Scene"].setText(f"Scene: {scene}")
        camera_mode = self.globe3DView.camera.getCameraMode()
        self.labels["CameraMode"].setText(f"Camera Mode: {camera_mode}")

    def drawCameraTarget(self):
        target = self.globe3DView.cameraTarget
        name = target["name"]
        position = target["position"]
        x = f"{position[0]:.1f}"
        y = f"{position[1]:.1f}"
        z = f"{position[2]:.1f}"

        self.labels["CameraTarget"].setText(f"Target: {name} ({x}, {y}, {z})")

    def draw2DCartesianCoordinates(self):
        coords = self.controller.Earth.get2DCartesianCoordinates(self.controller.current_satellite, self.controller.Timescale.now())
        latitude = coords[0].dstr()
        longitude = coords[1].dstr()
        altitude = coords[2] / self.controller.scale # Convert to km

        self.labels["2DCartesianCoordinates"].setText(f"LATITUDE: {latitude}\nLONGITUDE: {longitude}\nALTITUDE: {altitude:.1f} km")

    def drawCurrentTime(self):
        # current time in .est
        time = self.controller.local_time
        self.labels["CurrentTime"].setText(f"Current Time: {time}")

    def drawTargetSunlit(self):
        target = self.controller.current_satellite
        isSunlit = self.controller.Earth.isSunlit(target, self.controller.Timescale.now())
        self.labels["TargetSunlit"].setText(f"Sunlit: {isSunlit}")


class Globe3DView(QOpenGLWidget):
    """ Render a 3D globe using OpenGL, with different scenes such as GLOBE_VIEW, TRACKING_VIEW, and EXPLORE_VIEW."""
    def __init__(self, controller: ControllerProtocol, earth):
        super().__init__()
        self.controller = controller
        self.renderDistance = Distance.au(2.5).km * self.controller.scale
        self.camera = self.Camera(controller, self, earth)
        self.Earth = earth

        self.ts = self.controller.Timescale

        self.overlay = TransparentOverlayView(self.controller, self)
        self.overlay.setGeometry(self.rect())

        self.quality = self.RenderQuality.LOW
        self.current_scene = self.SceneView
        self.setScene(self.SceneView.EXPLORE_VIEW)

        self.runtime = QTimer(self)
        self.runtime.timeout.connect(self.update) # run 'onRuntime' when timer ends

        self.satellite_position = None
        self.frame_count = 0

        # camera orbit settings
        self.lastPos = QPoint()
        self.cameraDistance = 20
        self.theta = 0
        self.phi = 0
        self.maxCameraAltitude = self.Earth.radius.km * 50
        self.minCameraAltitude = self.Earth.radius.km + 1
        self.isDragging = False
        self.cameraPosXYZ = [0, 0, 20]
        self.cameraTarget = {"name": "", "position": [0, 0, 0]}

        self.orbitDistance = self.Earth.radius.km + 10

        self.satellite_label = QLabel(self)
        self.satellite_label.setFixedSize(20, 20)
        color = QColor(255, 0, 0)
        self.satellite_label.setPixmap(self.recolorSVG("src/assets/icons/gis--satellite.svg", Qt.GlobalColor.white))

        app_icon = self.recolorSVG("src/assets/icons/gis--network.svg", Qt.GlobalColor.white)
        #self.controller.app.setWindowIcon(QPixmap(app_icon.scaled(512, 512)))

        # set the app icon used in the windows taskbar


        self.mousePressEvent = self.mousePressEvent
        self.mouseMoveEvent = self.mouseMoveEvent
        self.mouseReleaseEvent = self.mouseReleaseEvent


    def recolorSVG(self, path, color):
        renderer = QtSvg.QSvgRenderer(path)
        pixmap = QPixmap(self.satellite_label.size())
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)

        painter.fillRect(pixmap.rect(), color)
        painter.end()
        return pixmap


    def run(self):
        self.runtime.start(16) # 60fps

    # Init OpenGL view
    def initializeGL(self):

        glEnable(GL_DEPTH_TEST) # Enable depth testing
        glDepthFunc(GL_LEQUAL) # Set the depth function to less than or equal
        glEnable(GL_TEXTURE_2D) # Enable texture mapping
        glEnable(GL_LIGHTING) # Enable lighting
        glEnable(GL_LIGHT0) # Enable light source 0
        glEnable(GL_COLOR_MATERIAL)  # Enable color materials
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE) # Set color materials to affect both ambient and diffuse components

        self.loadTextures(self.quality) # Set the textures based on the quality

        # sun light0 settings
        sun_position = np.array([Distance.au(1.0).km, 0, 0]) * self.controller.scale
        glLightfv(GL_LIGHT0, GL_POSITION, [sun_position[0], sun_position[1], sun_position[2], 0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1]) # ambient: gray
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 0.8, 1]) # diffuse: yellow
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1, 1, 1, 1]) # specular: white

        # material settings
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.3, 0.3, 0.3, 1.0)) # ambient: gray
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0.6, 0.6, 0.6, 1.0)) # diffuse: gray
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0)) # specular: white
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50.0) # shininess: 100 MAX

    def setOverlayVisibility(self, visible):
        return self.overlay.setVisibility(visible)

    def setCameraTarget(self, target, position):
        self.cameraTarget = {"name": target, "position": position}
        self.orbitDistance = 20 if target == "Earth" else 1

    # Every frame, draw the OpenGL scene
    def paintGL(self):
        self.overlay.update()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # Clear the color and depth buffers
        glLoadIdentity() # Reset the modelview matrix to the identity matrix

        glEnable(GL_LIGHTING)
        glColor4f(1.0, 1.0, 1.0, 1.0) # Set base color to white
        glEnable(GL_TEXTURE_2D)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.earth_daymap)
        glMatrixMode(GL_MODELVIEW)

        # draw the current scene
        self.camera.update()
        self.drawScene_EXPLORE_VIEW()
        return

        if self.current_scene == self.SceneView.GLOBE_VIEW:
            self.drawScene_GLOBE_VIEW()
        if self.current_scene == self.SceneView.TRACKING_VIEW:
            self.drawScene_TRACKING_VIEW()
        elif self.current_scene == self.SceneView.EXPLORE_VIEW:
            self.drawScene_EXPLORE_VIEW()

    def drawScene_GLOBE_VIEW(self):
        return

    def drawScene_TRACKING_VIEW(self):
        return


    def drawScene_EXPLORE_VIEW(self):
        self.setCameraTarget("Earth", [0, 0, 0])

        satellite = self.controller.current_satellite # get the current satellite object to track

        if self.controller.isDebug:
            self.drawXYZAxis()
        time = self.controller.Timescale.now()


        glRotatef(-90, 1, 0, 0) # Align Earth's North Pole with the z-axis
        self.drawSkybox()
        glEnable(GL_LIGHTING)
        glColor4f(1.0, 1.0, 1.0, 1.0) # Set base color to white
        glEnable(GL_TEXTURE_2D)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.earth_daymap)
        glMatrixMode(GL_MODELVIEW)
        self.drawSun()

        glRotatef(self.Earth.axial_tilt, 0, 1, 0) # Rotate the Earth's axial tilt
        self.drawSatellite(satellite, now=time, color=QColor(255, 255, 255))

        # elliptical orbit path
        glLineWidth(1)
        glColor4f(1.0, 0.0, 0.0, 1.0)
        self.drawSatelliteOrbit(satellite)

        rotation = self.Earth.calculateRotation(self.controller.Timescale.now())
        glRotatef(rotation, 0, 0, 1) # Rotate the Earth around the z-axis to simulate the Earth's rotation

        self.drawEarth()

        if self.controller.isDebug:
            self.drawParallels()
            self.drawMeridians()
            self.drawPoles()

    def drawSatelliteOrbit(self, satellite):
        glDisable(GL_LIGHTING)
        glPushMatrix()
        glLineWidth(1)
        glEnable(GL_LINE_SMOOTH)

        positions = self.controller.orbit_data # a stored array of positions for the current satellite's orbit
        glBegin(GL_LINE_STRIP)
        for position in positions:
            glVertex3f(*position)
        glVertex3f(*positions[0]) # Close the loop
        glEnd()




        glPopMatrix()
        glDisable(GL_LINE_SMOOTH)
        glEnable(GL_LIGHTING)

    def drawSatellite(self, satellite, now, color):
        """ Draw the satellite at the given position. """

        glEnable(GL_LIGHTING)
        glDepthMask(GL_TRUE)

        # use gluProject to convert 3D coordinates to 2D screen coordinates
        viewport = glGetIntegerv(GL_VIEWPORT)
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)

        # getECICoordinates returns a numpy array of sat positions if a list of times is passed, but a single position if a single time is passed
        position = self.Earth.getECICoordinates(satellite, now)

        screen_coords = self.get2DScreenCoordsFrom3D(*position)
        x = screen_coords[0]
        y = self.height() - screen_coords[1]

        # offset the label to be centered on the satellite's position
        x -= self.satellite_label.width() / 2
        y -= self.satellite_label.height() / 2

        # Extract camera position and calculate the vector to the satellite
        cam_position = np.linalg.inv(np.array(modelview)).reshape(4,4).T[:3, 3]
        vector_to_satellite = np.array(position) - cam_position
        forward_direction = -np.array(modelview)[:3, 2]
        dot_product = np.dot(forward_direction, vector_to_satellite)
        raycast = self.is_occluded(cam_position, position, self.Earth)

        self.satellite_label.setPixmap(self.recolorSVG("src/assets/icons/gis--satellite.svg", color))

        if dot_product > 1 and not raycast:
            self.satellite_label.move(x, y)
            self.satellite_label.setVisible(True)
        else:
            self.satellite_label.move(x, y)
            self.satellite_label.setVisible(False)
        glEnable(GL_LINE_SMOOTH)

        glLineWidth(1)
        glPushMatrix() #draw a straight line that points through the center of the earth
        glBegin(GL_LINES)
        glColor4f(0.5, 0.5, 0.5, 1.0)
        glVertex3f(*position)
        glVertex3f(0, 0, 0)
        glEnd()
        glPopMatrix()

        '''
        glPushMatrix()
        glDisable(GL_LIGHTING)
        ground_path = self.controller.ground_path
        glBegin(GL_LINE_STRIP)
        for position in ground_path:
            glColor4f(1.0, 1.0, 1.0, 1.0)
            glVertex3f(*position)
        glEnd()
        glPopMatrix()
        glEnable(GL_LIGHTING)
            '''

        if self.controller.isDebug:
            glPushMatrix()
            surface_position = normalize(position) * self.controller.Earth.radius.km
            glTranslatef(*surface_position)
            glColor4f(1.0, 1.0, 1.0, 1.0)
            quadric = gluNewQuadric()
            gluSphere(quadric, .1, self.earth_triangles, self.earth_triangles)
            glPopMatrix()

            glPushMatrix()
            glTranslatef(*position)
            glColor4f(1.0, 1.0, 1.0, 1.0)
            quadric = gluNewQuadric()
            gluSphere(quadric, 0.01, self.earth_triangles, self.earth_triangles)
            glPopMatrix()

        # reset color

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


    def intersect_ray_sphere(self, ray_origin, ray_direction, sphere_center, sphere_radius):
        oc = sphere_center - ray_origin
        tca = np.dot(oc, ray_direction)
        d2 = np.dot(oc, oc) - tca * tca
        if d2 > sphere_radius * sphere_radius:
            return None  # No intersection
        thc = np.sqrt(sphere_radius * sphere_radius - d2)
        t0 = tca - thc
        t1 = tca + thc
        if t0 > t1:
            t0, t1 = t1, t0
        if t0 < 0:
            t0 = t1
            if t0 < 0:
                return None
        # Calculate the intersection point
        intersection_point = ray_origin + ray_direction * t0
        return intersection_point

    def is_occluded(self, camera_position, target_position, sphere):
        ray_origin, ray_direction = self.get_ray(camera_position, target_position)
        intersection_point = self.intersect_ray_sphere(ray_origin, ray_direction, sphere.center, sphere.radius.km)
        if intersection_point is not None:
            # Calculate vector to the satellite and to the intersection point
            vector_to_satellite = np.array(target_position) - ray_origin
            vector_to_intersection = intersection_point - ray_origin

            # Check if the intersection point is closer than the satellite
            distance_to_satellite = np.linalg.norm(vector_to_satellite)
            distance_to_intersection = np.linalg.norm(vector_to_intersection)

            return distance_to_intersection < distance_to_satellite
        return False


    def get_ray(self, camera_position, target_position):
        direction = np.array(target_position) - np.array(camera_position)
        normalized_direction = direction / np.linalg.norm(direction)
        return camera_position, normalized_direction

    def drawSun(self):
        glPushMatrix()  # Save the current matrix state

        ra = self.Earth.sun_ra
        dec = self.Earth.sun_dec
        distance = self.Earth.sun_distance
        sun_radius = 696340 * self.controller.scale # Radius of the Sun in km

        glTranslate(distance, 0, 0)
        glColor3f(1.0, 1.0, 0.0)  # Color the Sun yellow
        quadric = gluNewQuadric()
        gluSphere(quadric, sun_radius, 16, 16)  # Draw the Sun as a sphere

        glLightfv(GL_LIGHT0, GL_POSITION, [distance, 0, 0, 1])  # Set the position of the Sun light source
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 0.9, 1]) # Set the diffuse color of the Sun light source
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1, 1, 1, 1])  # specular: white
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1])  # ambient: gray



        glPopMatrix()  # Restore the previous matrix state

    def drawClouds(self):
        # draw clouds
        glDepthMask(GL_FALSE)
        glDisable(GL_LIGHTING)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        #glEnable(GL_BLEND)

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
        glBlendFunc(GL_ONE, GL_ZERO)
        glColor4f(1.0, 1.0, 1.0, 1)

    def drawKarmanLine(self):
        # draw the karman line, official boundary of space at 100km
        glDepthMask(GL_FALSE)
        glDisable(GL_LIGHTING)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)
        glColor4f(1.0, 1.0, 1.0, 0.5)

        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_FALSE)
        gluSphere(quadric, self.controller.Earth.karman_line, self.earth_triangles, self.earth_triangles)

        #glBlendFunc(GL_ONE, GL_ZERO)
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
        glDepthMask(GL_TRUE)
        glBlendFunc(GL_ONE, GL_ZERO)
        glColor4f(1.0, 1.0, 1.0, 1.0)

    def setScene(self, scene):
        # Set the current scene
        if scene == self.SceneView.GLOBE_VIEW:
            self.to_GLOBE_VIEW()
        elif scene == self.SceneView.TRACKING_VIEW:
            self.to_TRACKING_VIEW()
        elif scene == self.SceneView.EXPLORE_VIEW:
            self.to_EXPLORE_VIEW()

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
            return self.name.capitalize()

    def loadTextures(self, quality):

        if quality == self.RenderQuality.DEBUG:
            print("DEBUG MODE")
            glShadeModel(GL_FLAT)
            self.earth_triangles = 16
            self.controller.MainView.increment_spinbox.setValue(5)
            self.earth_daymap = self.unpackImageToTexture(imagePath=self.controller.Earth.textures_debug["earth_daymap"])
            self.stars_milky_way = self.unpackImageToTexture(imagePath=self.controller.Earth.textures_debug["stars_milky_way"])
            self.earth_clouds = self.unpackImageToTexture(imagePath=self.controller.Earth.textures_debug["earth_clouds"])


        elif quality == self.RenderQuality.LOW:
            glShadeModel(GL_FLAT)
            self.earth_triangles = 16
            self.controller.MainView.increment_spinbox.setValue(2)
            self.earth_daymap = self.unpackImageToTexture(imagePath=self.controller.Earth.textures_2k["earth_daymap"])
            self.stars_milky_way = self.unpackImageToTexture(imagePath=self.controller.Earth.textures_2k["stars_milky_way"])
            self.earth_clouds = self.unpackImageToTexture(imagePath=self.controller.Earth.textures_2k["earth_clouds"])

        elif quality == self.RenderQuality.HIGH:
            glShadeModel(GL_SMOOTH)
            self.earth_triangles = 128
            self.controller.MainView.increment_spinbox.setValue(1)
            self.earth_daymap = self.unpackImageToTexture(imagePath=self.controller.Earth.textures_8k["earth_daymap"])
            self.stars_milky_way = self.unpackImageToTexture(imagePath=self.controller.Earth.textures_8k["stars_milky_way"])
            self.earth_clouds = self.unpackImageToTexture(imagePath=self.controller.Earth.textures_8k["earth_clouds"])

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
        image = image.mirrored(False, True) # Flip the image vertically
        glTexImage2D(
            GL_TEXTURE_2D,      # target: Specifies the target texture. GL_TEXTURE_2D is the most common target.
            0,                  # level: Specifies the level-of-detail number. Level 0 is the base image level.
            GL_RGBA,            # internalformat: Specifies the number of color components in the texture.
            image.width(),      # width: Specifies the width of the texture image.
            image.height(),     # height: Specifies the height of the texture image.
            0,                  # border: This value must be 0.
            GL_RGBA,            # format: Specifies the format of the pixel data. It should match internalformat.
            GL_UNSIGNED_BYTE,   # type: Specifies the data type of the pixel data.
            image.bits()        # pixels: Specifies a pointer to the image data in memory.
        )

        return texture

    def drawEarth(self):
        glColor4f(1.0, 1.0, 1.0, 1.0) # Set color to white
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.earth_daymap) # Bind active texture to Earth texture

        glMatrixMode(GL_TEXTURE)
        glLoadIdentity()
        glTranslatef(0.75, 0, 0)  # Adjust texture offset if needed to align Prime Meridian
        glMatrixMode(GL_MODELVIEW)

        # Create and draw the sphere with Earth texture
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, self.controller.Earth.radius.km, self.earth_triangles, self.earth_triangles)
        gluDeleteQuadric(quadric)

    def drawPoles(self):
        glLineWidth(10)
        glDisable(GL_LIGHTING)
        # Draw South Pole
        glPushMatrix()
        glTranslatef(0, 0, -self.controller.Earth.radius.km)
        glColor4f(0.0, 0.0, 1.0, 1.0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, -2)
        glEnd()
        glPopMatrix()

        # Draw North Pole
        glPushMatrix()
        glTranslatef(0, 0, self.controller.Earth.radius.km)
        glColor4f(1.0, 0.0, 0.0, 1.0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 2)
        glEnd()
        glPopMatrix()

        glColor4f(1.0, 1.0, 1.0, 1.0) # Reset color
        glEnable(GL_LIGHTING)

    def drawMeridians(self):
        longitudes = self.Earth.meridians
        for longitude in longitudes:
            glPushMatrix()
            glLineWidth(2)
            glColor4f(1.0, 1.0, 1.0, 0.5)
            glRotatef(longitude, 0, 0, 1)
            glBegin(GL_LINE_LOOP)
            for i in range(0, 360):
                x = (self.controller.Earth.radius.km + .1) * cos(radians(i))
                z = (self.controller.Earth.radius.km + .1) * sin(radians(i))
                glVertex3f(x, 0, z)
            glEnd()
            glPopMatrix()

    def drawParallels(self):
        latitudes = self.Earth.parallels
        for latitude in latitudes:
            glPushMatrix()
            glLineWidth(2)
            glColor4f(1.0, 1.0, 1.0, 0.5) # Set color to white with 50% transparency to make parallels semi-transparent

            # Calculate the radius and z position for each parallel
            radius = (self.controller.Earth.radius.km + .1) * cos(radians(latitude))
            z = self.controller.Earth.radius.km * sin(radians(latitude))

            glBegin(GL_LINE_LOOP)
            for i in range(360):
                x = radius * cos(radians(i))
                y = radius * sin(radians(i))
                glVertex3f(x, y, z)  # Use the calculated z-value to position the parallel at the correct latitude
            glEnd()
            glPopMatrix()


    def drawXYZAxis(self):
        axisLength = self.controller.Earth.radius.km * 1.5  # Make axes slightly longer than the radius
        lineWidth = 5

        glDisable(GL_LIGHTING)

        # X-Axis (Red)
        glPushMatrix()
        glColor4f(1.0, 0.0, 0.0, 1.0)
        glLineWidth(lineWidth)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(axisLength, 0, 0)
        glEnd()
        glPopMatrix()

        # Y-Axis (Green)
        glPushMatrix()
        glColor4f(0.0, 1.0, 0.0, 1.0)
        glLineWidth(lineWidth)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, axisLength, 0)
        glEnd()
        glPopMatrix()

        # Z-Axis (Blue)
        glPushMatrix()
        glColor4f(0.0, 0.0, 1.0, 1.0)
        glLineWidth(lineWidth)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, axisLength)
        glEnd()
        glPopMatrix()

        glEnable(GL_LIGHTING)
        glColor4f(1.0, 1.0, 1.0, 1.0) # Reset color

    def drawSphereManual(self):
        # draw a sphere manually
        lat_steps = self.earth_triangles
        long_steps = lat_steps * 2


        radius = self.controller.Earth.radius.km

        glPushMatrix()
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
        glPushMatrix()
        glDisable(GL_LIGHTING) # Disable lighting for the skybox
        glDepthMask(GL_FALSE) # Disable writing to the depth buffer for the skybox, so it is always drawn behind other objects

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.stars_milky_way) # Bind active texture to stars texture

        # Draw the skybox as a sphere
        glTranslatef(0, 0, 0)
        glScalef(-1, 1, 1)
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, Distance.au(2.25).km * self.controller.scale, self.earth_triangles, self.earth_triangles)

        glDepthMask(GL_TRUE) # Re-enable writing to the depth buffer
        glEnable(GL_LIGHTING) # Re-enable lighting`
        glActiveTexture(GL_TEXTURE0)


        glPopMatrix()

    def resizeGL(self, width, height):
        """ Resize the OpenGL viewport, update the projection matrix, and set the POV Perspective """
        # Update projection matrix on resize
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / float(height), 0.1, self.renderDistance)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    def setQuality(self, quality):
        """ Set the render quality

        Args:
            quality (RenderQuality): The quality of the rendering: LOW or HIGH or DEBUG
        """
        if isinstance(quality, int):
            quality = self.RenderQuality(quality)
        self.quality = quality
        print(f"Setting render quality to {quality}")
        self.loadTextures(quality)
    def getQuality(self):
        """ Return current render quality setting

        Returns:
            RenderQuality: The current render quality setting: LOW or HIGH
        """
        return self.quality
    class RenderQuality(Enum):
        """ Enum for the different render qualities: LOW, HIGH, or DEBUG """
        DEBUG = 0
        LOW = 1
        HIGH = 2

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
            self.cameraDistance -= scrollDistance / 120
            self.updateOrbitCamera()
            self.update()


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

            x = self.cameraDistance * sin(theta_rad) * cos(phi_rad) + target_pos[0]
            y = self.cameraDistance * sin(phi_rad) + target_pos[1]
            z = self.cameraDistance * cos(theta_rad) * cos(phi_rad) + target_pos[2]
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
                #glPushMatrix()
                gluLookAt(
                    0, 0, 30,
                    0, 0, 0,
                    0, 0, 1
                )
                #glPopMatrix()

            elif self.mode == self.CameraMode.FOLLOW:
                glRotatef(-90, 1, 0, 0) # Align Earth's North Pole with the z-axis
                glRotatef(-90, 0, 0, 1) # Align Earth's Prime Meridian with the x-axis

                target = self.globe3DView.cameraTarget
                target_pos = target["position"]

                # firstly, normalize the target position
                normalized_target_pos = normalize(target_pos) * (self.Earth.radius.km * 1.5)

                # then, calculate the camera position with cross product
                #camera_pos = np.cross(normalized_target_pos, [0, 0, 1])

                gluLookAt(*target_pos, 0,0,0, 0,0,1)
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

            def __str__(self):
                return self.name.capitalize()


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