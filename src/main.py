import sys

from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtWidgets import QApplication

from src.controllers.controller import ApplicationController
from src.services.icon_service import IconService

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
    sys.argv += ['-platform', 'windows:darkmode=2']

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    taskbar_icon = IconService().getIcon('gis--network.svg', Qt.GlobalColor.darkGray)
    app.setWindowIcon(taskbar_icon)

    appController = ApplicationController(app)
    appController.run()

    app.aboutToQuit.connect(appController.kill)
    sys.exit(app.exec())

# run application
if __name__ == "__main__":
    main()
