import sys
from argparse import ArgumentParser

from PyQt6.QtCore import QCoreApplication, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QApplication

from config import *
from core.services.tracker_service import TrackerService
from gui import MainWindow


# runtime
def main():
    QCoreApplication.setOrganizationName("MisterBluSky")
    QCoreApplication.setOrganizationDomain("misterblusky.com")
    QCoreApplication.setApplicationName("skywatch_project")
    app = QApplication(sys.argv)

    # Comment out GUI Init for now
    widget = MainWindow()
    widget.restoreSettings()

    sys.exit(app.exec())

    parser = ArgumentParser(description="SkyWatch Satellite Tracker")
    parser.add_argument(
        "--track", metavar="SATELLITE", type=str, help="Track a satellite by its name"
    )

    args = parser.parse_args()

    if args.track:
        track_satellite(args.track)


#def track_satellite(satellite_name):
    # Assume TrackerService can handle the tracking logic
    #service = TrackerService()
    #print(service.track_satellite(satellite_name))


# run application
if __name__ == "__main__":
    main()
