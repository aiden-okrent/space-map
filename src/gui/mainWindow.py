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

import config
import utils.JSONtoDictionary as JSONtoDictionary

from .abstractDockWidget import AbstractDockWidget
from .abstractWindow import AbstractWindow
from .centralDisplayWidget import CentralDisplayWidget
from .dialogs import ConfigMenuDialog, CustomDialog
from .opengl_widgets import EarthMapView3D


class MainWindow(AbstractWindow):
    def __init__(self):
        super().__init__()

        self.settingsGroup = "Main Window"
        self.initUI()

    def initUI(self):

        # self.centralDisplay = CentralDisplayWidget(self)
        # self.setCentralWidget(self.centralDisplay)

        quality = 0 # 0 = low, 1 = medium, 2 = high
        self.centralDisplay = EarthMapView3D(self, quality)
        self.setCentralWidget(self.centralDisplay)

        # toolbar
        self.toolBar = QToolBar("Toolbar")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        self.toolBar.addAction("Settings", self.openCustomDialog)
        self.toolBar.addSeparator()
        #self.toolBar.addAction("Set Quality", self.mainDisplay.setQuality)


        # dockwidget left
        self.dockWidget = AbstractDockWidget(self)
        self.dockWidget.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.dockWidget.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dockWidget)
        #self.dockWidget.setWidget(QLabel("Dock Widget left"))

        # dockwidget right
        self.dockWidget2 = AbstractDockWidget(self)
        self.dockWidget2.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.dockWidget2.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dockWidget2)
        self.dockWidget2.setWidget(QLabel("Dock Widget right"))

        # dockwidget bottom
        self.dockWidget3 = AbstractDockWidget(self)
        self.dockWidget3.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.dockWidget3.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dockWidget3)
        #self.dockWidget3.setWidget(QLabel("Dock Widget bottom"))

    def openCustomDialog(self):
        dialog = CustomDialog(self)
        dialog.exec()
