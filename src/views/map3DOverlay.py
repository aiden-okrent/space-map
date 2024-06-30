#

from typing import TYPE_CHECKING

import datetime
import dateutil.tz as tz

from PySide6.QtCore import QSize, Qt, QTime, QTimer
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QRegion, QResizeEvent, QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QStyle,
    QStyleOption,
    QVBoxLayout,
    QWidget,
)

from OpenGL.GL import *
from OpenGL.GLU import *


from src.services.icon_service import IconService
from src.models.satelliteRegistry import SatelliteRegistry
from src.models.satellite import Satellite

if TYPE_CHECKING:
    from src.controllers.controller import ApplicationController
    from src.models.earth import Earth
    from src.models.simulation import Simulation
    from src.views.map3DViewport import Map3DViewport

class Map3DOverlay(QWidget):

    Controller: 'ApplicationController'

    def __init__(self, MainView, Controller: 'ApplicationController', parent):
        super().__init__(parent)
        self.MainView = MainView
        self.parent = parent
        self.Controller = Controller
        self.model = Controller.model

        self.initUI()

    def setViewport(self, viewport: 'Map3DViewport'):
        self.viewport = viewport

    def initUI(self):
        self.initTimeDisplay()

    def resizeEvent(self, event: QResizeEvent):
        self.setGeometry(0, 0, self.parent.width(), self.parent.height())
        maskReg = QRegion(self.parent.geometry())
        maskReg -= QRegion(self.geometry())
        maskReg += self.childrenRegion()
        self.setMask(maskReg)
        return super().resizeEvent(event)


    def update(self):
        self.updateTimeDisplay(self.Controller.sim.now_datetime())
        super().update()

    def get2DScreenCoordsFrom3D(self, x, y, z) -> tuple:
        modelView = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)

        screenX, screenY, screenZ = gluProject(x, y, z, modelView, projection, viewport)
        return (screenX, screenY, screenZ)

    def drawSatelliteLabel(self, sat: Satellite, pos3D: tuple):

        for child in self.parent.children():
            if child.objectName() == str(sat.satnum):
                child.deleteLater()

        label = QLabel(self.parent)
        label.setObjectName(str(sat.satnum))
        label.setFixedSize(20, 20)
        label.setScaledContents(True)
        label.setPixmap(sat.icon.pixmap(20, 20))

        pos2D = self.get2DScreenCoordsFrom3D(*pos3D)


        x = pos2D[0]
        y = self.height() - pos2D[1]

        # offset the label to be centered on the satellite's position
        x -= label.width() / 2
        y -= label.height() / 2

        label.move(x, y)
        return label


    def initTimeDisplay(self):
        self.timeDisplay = QLabel(self)
        self.timeDisplay.setStyleSheet("color: white; font-size: 20px;")
        self.timeDisplay.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.timeDisplay.setScaledContents(True)
        self.timeDisplay.setWordWrap(True)
        self.timeDisplay.setMargin(5)
        self.timeDisplay.setGeometry(0, 0, 250, 50)
        self.timeDisplay.resizeEvent = lambda event: self.timeDisplay.setGeometry(0, 0, 250, 50)

        self.Controller.sim.epochChanged.connect(self.updateTimeDisplay)

    def updateTimeDisplay(self, epoch: datetime.datetime):
        epoch = epoch.astimezone(tz.tzlocal())
        self.timeDisplay.setText(f"{epoch.date().year}-{epoch.date().month}-{epoch.date().day} {epoch.time().strftime('%#I:%M:%S %p')}")




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

        # the label would be beyond the borders of the widget, hide it
        if x < 0 or x > self.width() or y < 0 or y > self.height():
            self.satellite_label.setVisible(False)
            return

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
