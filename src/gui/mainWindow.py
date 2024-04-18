# pyqt6 main window, run by an external app
import copy
import json
import os
import time
from datetime import datetime
from turtle import right

from PySide6.QtCore import QDateTime, QPoint, QRect, QSize, Qt
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

from .abstractDockWidget import AbstractDockWidget
from .abstractWindow import AbstractWindow
from .JSONtoDictionary import JSONtoDictionary
from .mapView3D import Map3DViewWidget
from .opengl_widgets import EarthMapView3D
from .settingsDialogs import QualityDialog


class MainWindow(AbstractWindow):
    def __init__(self):
        super().__init__()

        self.settingsGroup = "Main Window"
        self.initUI()

    def initUI(self):

        self.centralDisplay = Map3DViewWidget(self)

        #self.centralDisplay = EarthMapView3D(self, 0)
        self.setCentralWidget(self.centralDisplay)

        # toolbar
        self.toolBar = QToolBar("Toolbar")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)
        self.toolBar.addAction("Quality", self.openQualityDialog)

        # dockwidget
        self.dockWidget = AbstractDockWidget(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dockWidget)

    def openQualityDialog(self):
        dialog = QualityDialog(self)
        dialog.exec()

