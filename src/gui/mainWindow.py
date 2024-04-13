# pyqt6 main window, run by an external app
import json
import os
import time
from datetime import datetime
from turtle import right

from PyQt6.QtCore import QDateTime, QPoint, QRect, QSize, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QDateTimeEdit,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from skyfield.api import iers2010, load  # type: ignore

import config
import utils.JSONtoDictionary as JSONtoDictionary

from .abstractWindow import AbstractWindow
from .dialogs import ConfigMenuDialog, CustomDialog
from .opengl_widgets import CubeView3D, EarthMapView3D, SphereView3D
from .widgets import InfoWidget, TimeWidget


class MainWindow(AbstractWindow):
    def __init__(self):
        super().__init__()

        self.settingsGroup = "Main Window"
        self.setWindowTitle("Main Window")
        self.initUI()

    def initUI(self):

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        self.mainLayout = QHBoxLayout()
        centralWidget.setLayout(self.mainLayout)

        # Column layouts
        leftColumnLayout = QVBoxLayout()
        centerColumnLayout = QVBoxLayout()
        rightColumnLayout = QVBoxLayout()

        # Add column layouts to the main horizontal layout
        # With stretch factors to set the ratio 1:2
        self.mainLayout.addLayout(leftColumnLayout, 1)
        self.mainLayout.addLayout(rightColumnLayout, 2)

        # 3D Cube view (Left Column)
        self.cubeView = CubeView3D(self)
        self.cubeView.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.cubeView.setMinimumSize(200, 200)
        self.cubeView.setMaximumSize(200, 200)
        leftColumnLayout.addWidget(self.cubeView)

        # 3D Sphere View (also left Column)
        self.sphereView = SphereView3D(self)
        self.sphereView.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.sphereView.setMinimumSize(200, 200)
        self.sphereView.setMaximumSize(200, 200)
        leftColumnLayout.addWidget(self.sphereView)

        # 3D Earth (right Column)
        quality = 0 # 0: low, 1: medium, 2: high
        self.earthMapView = EarthMapView3D(self, quality)
        self.earthMapView.setMinimumSize(200, 200)
        rightColumnLayout.addWidget(self.earthMapView)
        leftColumnLayout.addWidget(self.earthMapView.scale_label)
        leftColumnLayout.addWidget(self.earthMapView.cameraAltitude_label)
        leftColumnLayout.addWidget(self.earthMapView.cameraPos_label)


    def openConfigMenu(self):
        dialog = ConfigMenuDialog(self)
        dialog.exec()

    def testDialogOpen(self):
        dialog = CustomDialog(self)
        dialog.exec()
