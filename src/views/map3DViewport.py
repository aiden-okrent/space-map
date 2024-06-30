import time
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from PySide6.QtCore import QPoint, Qt, QTimer, QSize
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QWidget
from PySide6.QtOpenGLWidgets import QOpenGLWidget


from PySide6.QtCore import Signal
from PySide6.QtOpenGL import *
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QSurfaceFormat


class Map3DViewport(QOpenGLWidget):
    def __init__(self, MainView, Controller, parent: QWidget):
        super().__init__(parent)
        self.MainView = MainView
        self.parent = parent
        self.Controller = Controller
        self.model = Controller.model
        self.Earth = Controller.model.earth
        self.Simulation = Controller.sim
        self.TextureService = TextureService()

        self.frameCount = 0
        self.lastFrameTime = 0
        self.fps = 0

        earthRadius = self.Earth.radius.km
        self.camera = {
            "position": [0, 0, 0],
            "upVector": [0, 0, 1],
            "lookAt": [0, 0, 0],
            "phi": 0,
            "theta": 0,
            "zoom": 5 * earthRadius,
            "maxZoom": 30 * earthRadius,
            "minZoom": 0.12 * earthRadius,
        }

        self.mouse = {
            "lastPos": QPoint(),
        }

    def setOverlay(self, overlay):
        self.overlay = overlay

    def initializeGL(self):
        print("Initializing Map3DViewport")

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)

        self.setup_scene()
        self.startFPSCounter()

    def setup_scene(self):
        self.root = Object3D(None)
        self.obj = self.Controller.objects[2]
        glLightfv(GL_LIGHT0, GL_POSITION, (0, 0, 0, 1))

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        self.updateFPS()
        self.updateCamera()
        self.obj.draw(self.Simulation.now_Time)

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)

    def startFPSCounter(self):
        self.lastFrameTime = time.time()

    def updateFPS(self):
        self.frameCount += 1
        currentTime = time.time()
        elapsedTime = currentTime - self.lastFrameTime
        if elapsedTime >= 1.0:
            self.fps = self.frameCount / elapsedTime
            self.frameCount = 0
            self.lastFrameTime = currentTime
            self.MainView.setWindowTitle(f"{self.MainView.title} - {int(self.fps)} FPS")

    def mousePressEvent(self, event: QMouseEvent):
        self.mouse["lastPos"] = event.pos()
        self.updateCamera()

    def mouseMoveEvent(self, event: QMouseEvent):
        dx = event.x() - self.mouse["lastPos"].x()
        dy = event.y() - self.mouse["lastPos"].y()

        if event.buttons() & Qt.LeftButton:
            self.camera["theta"] -= dx / 2
            self.camera["phi"] += dy / 2

        self.mouse["lastPos"] = event.pos()
        self.updateCamera()

    def wheelEvent(self, event):
        self.camera["zoom"] -= event.angleDelta().y() / 1200 * self.camera["zoom"]
        self.updateCamera()

    def updateCamera(self):
        self.camera["phi"] = max(min(self.camera["phi"], 89), -89)
        self.camera["theta"] %= 360

        self.camera["zoom"] = max(
            min(self.camera["zoom"], self.camera["maxZoom"]), self.camera["minZoom"]
        )

        phi_rad = np.radians(self.camera["phi"])
        theta_rad = np.radians(self.camera["theta"])

        x = self.camera["zoom"] * np.cos(phi_rad) * np.cos(theta_rad)
        y = self.camera["zoom"] * np.cos(phi_rad) * np.sin(theta_rad)
        z = self.camera["zoom"] * np.sin(phi_rad)  # Up Vector

        self.camera["position"] = [x, y, z]

        self.update()
