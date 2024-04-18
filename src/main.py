import sys
from pathlib import Path

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

from controller import ApplicationController

# dark mode for windows 11
sys.argv += ['-platform', 'windows:darkmode=2']

# runtime
def main():
    QCoreApplication.setOrganizationName("MisterBluSky")
    QCoreApplication.setOrganizationDomain("misterblusky.com")
    QCoreApplication.setApplicationName("space-map")
    app = QApplication(sys.argv)

    app.setStyle('Fusion')

    appController = ApplicationController()
    appController.run()

    #widget = MainWindow()
    #widget.restoreSettings()

    sys.exit(app.exec())

# run application
if __name__ == "__main__":
    main()
