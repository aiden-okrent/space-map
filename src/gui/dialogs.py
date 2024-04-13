from config import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication, QIcon
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)
from utils import JSONtoDictionary

from .widgets import DoubleListMenuWidget


class ConfigMenuDialog(QDialog):
    def __init__(self, parent=None):
        super(ConfigMenuDialog, self).__init__(parent)
        self.setWindowTitle("Select a Satellite Group to Track")
        self.setWindowIcon(QIcon(":/icons/settings.png"))
        self.setModal(True)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.initUI()

    def initUI(self):
        self.layout.addWidget(QLabel("Select a Satellite Group to Track"))
        self.layout.addWidget(
            DoubleListMenuWidget(self, JSONtoDictionary(satellite_list_items_path))
        )

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

        self.setWindowTitle("HELLO!")

        QBtn = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("Something happened, is that OK?")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
