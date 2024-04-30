import sys
from pathlib import Path

from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtGui import QColor, QFont, QIcon, QIntValidator, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication, QWidget

from controller import ApplicationController

try:
    from ctypes import windll  # only available on Windows OS
    windll.shell32.SetCurrentProcessExplicitAppUserModelID('com.misterblusky.space-map')
except ImportError:
    pass

# runtime
def main():
    QCoreApplication.setOrganizationName("MisterBluSky")
    QCoreApplication.setOrganizationDomain("misterblusky.com")
    QCoreApplication.setApplicationName("space-map")
    sys.argv += ['-platform', 'windows:darkmode=2'] # dark mode for windows 11
    app = QApplication(sys.argv)
    app.setStyle('Fusion') # set style to Fusion

    icon_path = ('src/assets/icons/gis--network.svg')
    icon = QIcon(str(icon_path))
    pixmap = QPixmap(icon.pixmap(512, 512))  # Set the desired resolution here

    renderer = QSvgRenderer(icon_path)
    pixmap = QPixmap(512, 512)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)

    painter.fillRect(pixmap.rect(), Qt.GlobalColor.white)
    painter.end()

    app.setWindowIcon(pixmap)

    appController = ApplicationController(app)
    appController.run()

    sys.exit(app.exec())

# run application
if __name__ == "__main__":
    main()
