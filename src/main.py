import sys

import qdarkstyle
from OpenGL.GLUT import glutInit
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

from controller import ApplicationController


# runtime
def main():
    QCoreApplication.setOrganizationName("MisterBluSky")
    QCoreApplication.setOrganizationDomain("misterblusky.com")
    QCoreApplication.setApplicationName("space-map")
    sys.argv += ['-platform', 'windows:darkmode=2'] # dark mode for windows 11
    app = QApplication(sys.argv)
    app.setStyle('Fusion') # set style to Fusion

    appController = ApplicationController()
    appController.run()

    sys.exit(app.exec())

# run application
if __name__ == "__main__":
    main()
