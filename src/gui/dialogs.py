import os
import tkinter as tk
from tkinter import messagebox

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
)

from config import *
from utils import JSONtoDictionary


class ConfigMenuDialog(QDialog):
    def __init__(self, parent=None):
        super(ConfigMenuDialog, self).__init__(parent)
        self.setWindowTitle("Select a Satellite Group to Track")
        self.setWindowIcon(QIcon(":/icons/settings.png"))
        self.setModal(True)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))

        self.satellite_list_items_path = Path(os.path.join(
            project_root, "src", "assets", "config", "satellite_families.json"
        ))

        self.initUI()

    def initUI(self):
        self.layout.addWidget(QLabel("Select a Satellite Group to Track"))

        self.move(
            QGuiApplication.primaryScreen().geometry().center()
            - self.frameGeometry().center()
        )


class FileSelectMenu(QDialog):
    def __init__(self, parent=None):
        super(FileSelectMenu, self).__init__(parent)
        self.setWindowTitle("Configuration Menu")
        self.setWindowIcon(QIcon(":/icons/settings.png"))
        self.setModal(True)
        # self.setFixedSize(300, 200)
        # self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.initUI()

    def initUI(self):
        self.layout.addWidget(QLabel("Select the configuration file:"))
        self.file_path = QLineEdit()
        self.layout.addWidget(self.file_path)
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse)
        self.layout.addWidget(self.browse_button)
        self.layout.addStretch(1)
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.layout.addWidget(self.ok_button)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.layout.addWidget(self.cancel_button)

        self.move(
            QGuiApplication.primaryScreen().geometry().center()
            - self.frameGeometry().center()
        )

    def browse(self):
        file_path = QFileDialog.getOpenFileName(
            self, "Select Configuration File", "", "Configuration Files (*.conf)"
        )[0]
        if file_path:
            self.file_path.setText(file_path)

    def get_file_path(self):
        return self.file_path.text()


class CustomDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Quality Settings")

        QBtn = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("Select quality of render:")
        self.layout.addWidget(message)

        # Create radio buttons
        self.low_button = QRadioButton("Low")
        self.medium_button = QRadioButton("Medium")
        self.high_button = QRadioButton("High")


        # Set default radio button low
        #self.low_button.setChecked(True)

        # connect all buttons to 1 method with a single arg of 0, 1, or 2
        self.low_button.clicked.connect(lambda: self.setQuality(0))
        self.medium_button.clicked.connect(lambda: self.setQuality(1))
        self.high_button.clicked.connect(lambda: self.setQuality(2))


        # Add radio buttons to layout
        self.layout.addWidget(self.low_button)
        self.layout.addWidget(self.medium_button)
        self.layout.addWidget(self.high_button)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def setQuality(self, quality=0):
        self.parent.centralDisplay.setQuality(quality)
        self.close()