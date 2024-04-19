import os
from math import cos, radians, sin

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PySide6.QtGui import QImage
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
from PySide6.QtWidgets import (
    QApplication,
    QCalendarWidget,
    QDateTimeEdit,
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QPlainTextDocumentLayout,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSplitter,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
from skyfield.toposlib import GeographicPosition

from config import map_textures


class AbstractWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.settings = QSettings()
        self.settingsGroup = "default"

    def resize(self, size: QSize) -> None:
        return super().resize(size)

    def move(self, position: QPoint) -> None:
        return super().move(position)

    def setWindowState(self, state: Qt.WindowState) -> None:
        return super().setWindowState(state)

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

    def moveEvent(self, event: QEvent):
        super().moveEvent(event)

    def closeEvent(self, event):
        self.saveSettings()
        super().closeEvent(event)

class MainView(AbstractWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.settingsGroup = "Main View"
        self.initUI()

    def initUI(self):
        # toolbar
        self.toolBar = QToolBar("Toolbar")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)

        self.show_ISS_button = self.toolBar.addAction("Show ISS", self.controller.show_ISS_button_clicked)
        self.quality_Action = self.toolBar.addAction("Quality: ", self.controller.toggle_quality)
        self.currentScene_Action = self.toolBar.addAction("Current Scene: ", self.controller.toggle_scene)


        # empty right dockwidget
        self.dockWidget = QDockWidget(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dockWidget)

        self.setWindowTitle("Space Map")


    def setQualityText(self, quality):
        self.quality_Action.setText("Quality: " + str(quality))

    def setSceneText(self, scene):
        self.currentScene_Action.setText("Current Scene: " + str(scene))

class Globe3DView(QOpenGLWidget):
    """ Render a 3D globe using OpenGL, with different scenes such as GLOBE_VIEW, SATELLITE_TRACKING_VIEW, SATELLITES_EXPLORE_VIEW """
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.renderDistance = 160

        self.quality = self.RenderQuality.LOW # default quality
        self.current_scene = self.SceneView.GLOBE_VIEW # default scene

        self.runtime = QTimer(self)
        self.runtime.timeout.connect(self.update) # run 'onRuntime' when timer ends
        self.runtime.start(16) # 60fps

    def setScene(self, scene):
        if scene in self.SceneView:
            self.current_scene = scene
        else:
            raise ValueError("Invalid Scene, " + scene)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        self.drawSkybox()

        if self.current_scene == self.SceneView.GLOBE_VIEW:
            self.drawGlobeView()
        if self.current_scene == self.SceneView.SATELLITE_TRACKING_VIEW:
            self.drawSatelliteTrackingView()
        elif self.current_scene == self.SceneView.SATELLITES_EXPLORE_VIEW:
            self.drawSatellitesExploreView()

    def drawGlobeView(self):
        gluLookAt(-40, 0, 0, 0, 0, 0, 0, 0, -1) # static camera position
        self.drawEarth() # draw just the Earth

    def drawSatelliteTrackingView(self):
        # TODO: Implement satellite tracking view around the Earth
        translation = self.controller.get_current_satellite_translation()
        print(translation)

        translation = [translation[0]/1000, translation[1]/1000, translation[2]/1000]

        lookat = translation

        largest_translation = max(translation[0], translation[1], translation[2])
        if largest_translation > 0:
            lookat = [coord + 10 if coord == largest_translation else coord for coord in lookat]
        elif largest_translation < 0:
            lookat = [coord - 10 if coord == largest_translation else coord for coord in lookat]

        gluLookAt(lookat[0], lookat[1], lookat[2], 0, 0, 0, 0, 0, -1) # camera follows satellite

        self.drawEarth()


        # draw a single sphere at the satellite position
        glPushMatrix()
        glTranslatef(translation[0], translation[1], translation[2])
        glColor3f(1, 0, 0)
        quadric = gluNewQuadric()
        gluSphere(quadric, .1, 16, 16)
        glPopMatrix()
        glColor3f(1, 1, 1) # reset color

    def drawSatellitesExploreView(self):
        self.drawEarth()
        # TODO: Implement satellite explore view around the Earth, which displays multiple satellites and allows the user to select from them to track

    def initializeGL(self):
        # Enable depth and textures
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

    def setQuality(self, quality):
        self.quality = quality
        self.getTextures(quality)

    def getQuality(self):
        return self.quality

    def getTextures(self, quality):
        if quality == self.RenderQuality.LOW:
            print("Setting quality to low")
            glShadeModel(GL_FLAT)
            self.earth_triangles = 16
            self.lighting_enabled = False
            self.earth_daymap = self.unpackImageToTexture(imagePath=os.path.join(map_textures, "land_ocean_ice_2048.jpg"))
            self.stars_milky_way = self.unpackImageToTexture(imagePath=os.path.join(map_textures, "2k_stars_milky_way.jpg"))

        elif quality == self.RenderQuality.HIGH:
            print("Setting quality to high")
            glShadeModel(GL_SMOOTH)
            self.earth_triangles = 256
            self.lighting_enabled = True
            self.earth_daymap = self.unpackImageToTexture(imagePath=os.path.join(map_textures, "blue_marble_NASA_land_ocean_ice_8192.png"))
            self.stars_milky_way = self.unpackImageToTexture(imagePath=os.path.join(map_textures, "8k_stars_milky_way.jpg"))

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

    def drawEarth(self):
        glEnable(GL_TEXTURE_2D)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.earth_daymap)
        #glPushMatrix()

        # draw earth sphere
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)  # Enable texture mapping
        gluSphere(quadric, self.controller.Earth.geoid.radius.km/1000, self.earth_triangles, self.earth_triangles)

        #glPopMatrix()

    def drawSkybox(self):
        # disable lighting and depth masks because we want the skybox to be drawn behind everything
        glDisable(GL_LIGHTING)
        glDepthMask(GL_FALSE)
        #glPushMatrix()

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
        #glPopMatrix()
        glEnable(GL_LIGHTING)


    def resizeGL(self, width, height):
        # Update projection matrix on resize
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / float(height), 1, self.renderDistance)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    class RenderQuality(Enum):
        LOW = 0
        HIGH = 1

        def __str__(self):
            return self.name.capitalize()

    class SceneView(Enum):
        GLOBE_VIEW = 0
        SATELLITE_TRACKING_VIEW = 1
        SATELLITES_EXPLORE_VIEW = 2

        def __str__(self):
            return self.name.upper()