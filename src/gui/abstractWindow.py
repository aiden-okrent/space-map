from PySide6.QtCore import QEvent, QPoint, QSettings, QSize, Qt
from PySide6.QtWidgets import QApplication, QMainWindow


# An abstract class to serve as the backbone of all windows in the application
class AbstractWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.settings = QSettings()
        self.settingsGroup = "default"

    def resize(self, size: QSize) -> None:
        return super().resize(size)

    def move(self, position: QPoint) -> None:
        return super().move(position)

    def setWindowState(self, state: Qt.WindowState) -> None:
        return super().setWindowState(state)

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

        self.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            QApplication.quit()
        else:
            super().keyPressEvent(event)

    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            self.saveSettings()
        super().changeEvent(event)

    def moveEvent(self, event: QEvent):
        super().moveEvent(event)

    def closeEvent(self, event):
        self.saveSettings()
        super().closeEvent(event)