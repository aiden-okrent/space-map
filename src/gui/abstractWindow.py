from PyQt6.QtCore import QPoint, QSettings, QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow


# An abstract class to serve as the backbone of all windows in the application
class AbstractWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.settings = QSettings()
        self.settingsGroup = "default"

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            QApplication.quit()
        else:
            super().keyPressEvent(event)

    def saveSettings(self):
        print("saving settings for", self.settingsGroup)
        self.settings.beginGroup(self.settingsGroup)
        self.settings.setValue("size", self.size())  # QSize
        self.settings.setValue("position", self.pos())  # QPoint
        self.settings.setValue("maximized", self.isMaximized())  # bool
        self.settings.endGroup()

    def restoreSettings(self):
        print("restoring settings for", self.settingsGroup)
        self.settings.beginGroup(self.settingsGroup)
        size = self.settings.value("size", QSize())  # QSize
        self.resize(size)
        position = self.settings.value("position", QPoint())  # QPoint
        self.move(position)

        if self.settings.value("maximized", False):
            self.showMaximized()
        else:
            self.show()

        self.settings.endGroup()

    def closeEvent(self, event):
        self.saveSettings()
        event.accept()
