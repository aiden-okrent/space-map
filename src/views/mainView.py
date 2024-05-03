#
import os

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
        self.MainToolBar = MainToolBar(self, self.controller)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.MainToolBar)
        self.MainToolBar.addSeparator()

        print(self.centralWidget())