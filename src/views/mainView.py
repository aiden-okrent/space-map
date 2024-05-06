#
import datetime
import os

from config.paths import ASSETS, CONFIG, TLE
from dateutil import tz
from PySide6 import QtCore
from PySide6.QtCore import QEvent, QPoint, QSettings, QSize, Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDockWidget,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProxyStyle,
    QSpinBox,
    QStyle,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from src.views.mainToolBar import MainToolBar
from src.views.map3DView import Map3DView


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
        # Close on ctrl+q
        if event.key() == Qt.Key.Key_Q and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
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
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._name = "Space Map v2"
        self.setWindowTitle(self._name)
        self.settingsGroup = self._name
        self.initUI()

    def initUI(self):
        self.menuBar = self.menuBar()
        fileMenu = self.menuBar.addMenu("&File")

        folderSubmenu = fileMenu.addMenu("Open Folder...")
        folderSubmenu.addAction("Assets...", lambda: os.system(f"start {ASSETS}"))
        folderSubmenu.addAction("Config...", lambda: os.system(f"start {CONFIG}"))
        folderSubmenu.addAction("TLE Files...", lambda: os.system(f"start {TLE}"))

        settingsSubmenu = fileMenu.addMenu("Settings...")
        settingsSubmenu.addAction('Toggle Orbits', lambda: self.controller.toggleOrbitVisibility())
        settingsSubmenu.addAction('Toggle Hidden', lambda: self.controller.toggleHidden())


        qualitySubmenu = settingsSubmenu.addMenu("Set Quality")
        qualitySubmenu.addAction("Low", lambda: self.controller.setQuality('low'))
        qualitySubmenu.addAction("High", lambda: self.controller.setQuality('high'))
        qualitySubmenu.addAction("Debug", lambda: self.controller.setQuality('debug'))

        fileMenu.addSeparator()
        github_url = "https://github.com/aiden-okrent/space-map/tree/dev"
        fileMenu.addAction("Github", lambda: os.system(f"start {github_url}"))
        fileMenu.addAction("Quit", self.controller.kill)

        resourceMenu = self.menuBar.addMenu("Resources")
        resourceMenu.addSection("Assets")
        gisIcons_url = "https://icon-sets.iconify.design/gis/?category=Maps+%2F+Flags"
        resourceMenu.addAction("GIS Icon Set", lambda: os.system(f"start {gisIcons_url}"))
        bluemarble_url = "https://visibleearth.nasa.gov/collection/1484/blue-marble"
        resourceMenu.addAction("NASA Earth Textures - Blue Marble Next Gen", lambda: os.system(f"start {bluemarble_url}"))
        celestrak_url = "https://celestrak.org/NORAD/elements/"
        resourceMenu.addAction("TLE Data - www.celestrak.org", lambda: os.system(f"start {celestrak_url}"))

        resourceMenu.addSection("Publications")
        resourceMenu.addAction("1984 NASA Prediction Bulletin", lambda: os.system(f"start {nasaPBulletin_pdf}"))
        noaa_url = "https://www.star.nesdis.noaa.gov/goes/fulldisk.php?sat=G16"
        rstr3_pdf = "https://celestrak.com/publications/AIAA/2006-6753/AIAA-2006-6753-Rev3.pdf"
        resourceMenu.addAction("2006 Revisiting Spacetrack Report #3", lambda: os.system(f"start {rstr3_pdf}"))
        nasaPBulletin_pdf = "https://celestrak.org/NORAD/documentation/NASA%20Prediction%20Bulletins.pdf"

        resourceMenu.addSection("Satellite Info")
        resourceMenu.addAction("NOAA - GOES 16", lambda: os.system(f"start {noaa_url}"))
        trackISS_url = "http://wsn.spaceflight.esa.int/iss/index_portal.php"
        resourceMenu.addAction("ESA - ISS Tracker", lambda: os.system(f"start {trackISS_url}"))

        self.menuBar.addSeparator()
        self.menuBar.addAction("Reset Time", lambda: self.controller.resetSimEpoch())

        self.MainToolBar = MainToolBar(self, self.controller)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.MainToolBar)
        self.MainToolBar.addSeparator()