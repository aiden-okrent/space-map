#
import datetime
import os

from config.paths import ASSETS, CONFIG, TLE
from dateutil import tz
from PySide6 import QtCore
from PySide6.QtCore import QEvent, QPoint, QSettings, QSize, Qt, QTimer
from PySide6.QtWidgets import *
from PySide6.QtGui import QSurfaceFormat

from src.views.map3DOverlay import Map3DOverlay
from src.views.map3DViewport import Map3DViewport


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

    def keyPressEvent(self, event):
        if (
            event.key() == Qt.Key.Key_Q
            and event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
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
    def __init__(self, Controller):
        super().__init__()
        self.Controller = Controller
        self.title = "Space Map v2"
        self.setWindowTitle(self.title)
        self.settingsGroup = self.title

        self.runtime = QTimer(self)
        self.runtime.timeout.connect(self.update)
        self.initUI()

    def initUI(self):
        centralWidget = QWidget()
        layout = QStackedLayout()
        layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        self.viewport = Map3DViewport(self, self.Controller, self.centralWidget())
        self.overlay = Map3DOverlay(self, self.Controller, self.centralWidget())

        layout.addWidget(self.viewport)
        layout.addWidget(self.overlay)

        self.viewport.setOverlay(self.overlay)
        self.overlay.setViewport(self.viewport)

        self.run()

        self.initMenuBar()
        self.initToolbar()

    def run(self):
        self.runtime.start(1000 / 60)

    def update(self):
        self.viewport.update()
        self.overlay.update()
        super().update()

    def initToolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setAllowedAreas(Qt.ToolBarArea.TopToolBarArea)
        toolbar.setOrientation(Qt.Orientation.Horizontal)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        toolbar.addSeparator()

        setSimSpeedWidget = QWidget()
        setSimSpeedLayout = QHBoxLayout()
        setSimSpeedWidget.setLayout(setSimSpeedLayout)
        setSimSpeedLayout.addWidget(QLabel("Speed:"))
        setSimSpeedSpinBox = QDoubleSpinBox()
        setSimSpeedSpinBox.setRange(-100.0, 100.0)
        setSimSpeedSpinBox.setSingleStep(0.25)
        setSimSpeedSpinBox.setValue(1.0)
        setSimSpeedSpinBox.setDecimals(2)
        setSimSpeedSpinBox.setAccelerated(True)  # arrow keys will change the value
        setSimSpeedSpinBox.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        setSimSpeedSpinBox.valueChanged.connect(self.Controller.setSimSpeed)
        setSimSpeedLayout.addWidget(setSimSpeedSpinBox)
        toolbar.addWidget(setSimSpeedWidget)
        self.Controller.sim.speedChanged.connect(
            lambda speed: setSimSpeedSpinBox.setValue(speed)
        )

        satelliteInput = QWidget()
        layout = QHBoxLayout()
        satelliteInput.setLayout(layout)
        inputLine = QLineEdit()
        layout.addWidget(inputLine)
        clearButton = QPushButton()
        clearButton.setFixedWidth(60)
        clearButton.setText("Clear")
        inputLine.editingFinished.connect(
            lambda: self.Controller.updateSatelliteRegistry(
                self.Controller.SatelliteFactory.searchDir(inputLine.text())
            )
        )
        clearButton.clicked.connect(
            lambda: (inputLine.clear(), self.Controller.updateSatelliteRegistry(None))
        )
        layout.addWidget(clearButton)
        toolbar.addWidget(satelliteInput)

        stretch = QWidget()
        stretch.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        toolbar.addWidget(stretch)

    def initMenuBar(self):
        self.menuBar = self.menuBar()
        fileMenu = self.menuBar.addMenu("&File")

        folderSubmenu = fileMenu.addMenu("Open Folder...")
        folderSubmenu.addAction("Assets...", lambda: os.system(f"start {ASSETS}"))
        folderSubmenu.addAction("Config...", lambda: os.system(f"start {CONFIG}"))
        folderSubmenu.addAction("TLE Files...", lambda: os.system(f"start {TLE}"))

        settingsSubmenu = fileMenu.addMenu("Settings...")

        qualitySubmenu = settingsSubmenu.addMenu("Set Quality")
        qualitySubmenu.addAction("Low", lambda: self.Controller.setQuality("low"))
        qualitySubmenu.addAction("High", lambda: self.Controller.setQuality("high"))
        qualitySubmenu.addAction("Debug", lambda: self.Controller.setQuality("debug"))

        fileMenu.addSeparator()
        github_url = "https://github.com/aiden-okrent/space-map/tree/dev"
        fileMenu.addAction("Github", lambda: os.system(f"start {github_url}"))
        fileMenu.addAction("Quit", self.close)

        resourceMenu = self.menuBar.addMenu("Resources")
        resourceMenu.addSection("Assets")
        gisIcons_url = "https://icon-sets.iconify.design/gis/?category=Maps+%2F+Flags"
        resourceMenu.addAction(
            "GIS Icon Set", lambda: os.system(f"start {gisIcons_url}")
        )
        bluemarble_url = "https://visibleearth.nasa.gov/collection/1484/blue-marble"
        resourceMenu.addAction(
            "NASA Earth Textures - Blue Marble Next Gen",
            lambda: os.system(f"start {bluemarble_url}"),
        )
        celestrak_url = "https://celestrak.org/NORAD/elements/"
        resourceMenu.addAction(
            "TLE Data - www.celestrak.org", lambda: os.system(f"start {celestrak_url}")
        )

        resourceMenu.addSection("Publications")
        resourceMenu.addAction(
            "1984 NASA Prediction Bulletin",
            lambda: os.system(f"start {nasaPBulletin_pdf}"),
        )
        noaa_url = "https://www.star.nesdis.noaa.gov/goes/fulldisk.php?sat=G16"
        rstr3_pdf = (
            "https://celestrak.com/publications/AIAA/2006-6753/AIAA-2006-6753-Rev3.pdf"
        )
        resourceMenu.addAction(
            "2006 Revisiting Spacetrack Report #3",
            lambda: os.system(f"start {rstr3_pdf}"),
        )
        nasaPBulletin_pdf = "https://celestrak.org/NORAD/documentation/NASA%20Prediction%20Bulletins.pdf"

        resourceMenu.addSection("Satellite Info")
        resourceMenu.addAction("NOAA - GOES 16", lambda: os.system(f"start {noaa_url}"))
        trackISS_url = "http://wsn.spaceflight.esa.int/iss/index_portal.php"
        resourceMenu.addAction(
            "ESA - ISS Tracker", lambda: os.system(f"start {trackISS_url}")
        )

        self.menuBar.addSeparator()
        self.menuBar.addAction("Reset Time", lambda: self.Controller.resetSimTime())
