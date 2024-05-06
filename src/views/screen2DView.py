#

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

if TYPE_CHECKING:
    from src.controllers.controller import ApplicationController
    from src.models.earth import Earth
    from src.models.simulation import Simulation
    from src.views.map3DView import Map3DView


class Screen2DView(QWidget):

    Controller: 'ApplicationController'
    Earth: 'Earth'
    Simulation: 'Simulation'
    Map3DView: 'Map3DView'

    def __init__(self, Controller: 'ApplicationController', parent, Model, Map3DView):
        super().__init__(parent)
        self.parent = parent
        self.Controller = Controller
        self.Model3D = Model
        self.Map3DView = Map3DView
        self.Earth = Controller.Earth
        self.Simulation = Controller.Simulation

        self.initUI()

    def initUI(self):
        self.setHidden(False)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setStyleSheet("background: transparent;")

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)

        self.setGeometry(self.Controller.Map3DView.rect())

        self.runtime = QTimer(self)
        self.runtime.timeout.connect(self.render_widgets)

        self.show()

        self.render_widgets()

    @property
    def _widgets(self):
        return {
            'Time': {
                'move': (200, 10),
                'label': {
                    'type': 'QLabel',
                    'text': 'Current Time',
                },
                'value': {
                    'type': 'QLabel',
                    'text': self.Controller.Simulation.now_localtime().strftime('%Y-%m-%d %H:%M:%S'),
                },
            },
        }

    def run(self):
        self.runtime.start(1000 / 60) # fps in milliseconds

    def render_widgets(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for widget in self._widgets:
            self.layout.addWidget(self.buildWidget(self._widgets[widget]))

    def buildWidget(self, data):
        widget = QWidget()
        widget.setLayout(QVBoxLayout())
        widget.move(*data['move'])

        for child, contents in data.items():
            if isinstance(contents, dict) and 'type' in contents:  # Check if contents is a dictionary and has 'type'
                if contents['type'] == 'QLabel':
                    label = QLabel()
                    label.setStyleSheet("color: white; font-size: 20px;")
                    label.setText(contents['text'])
                    label.setAlignment(Qt.AlignmentFlag.AlignTop)
                    widget.layout().addWidget(label)

        return widget

'''
OLD VERSION

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



'''