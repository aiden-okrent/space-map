#
import datetime
from typing import TYPE_CHECKING, Any, Dict

import keyboard
from dateutil import tz
from PySide6.QtWidgets import QApplication

from src.models.earth import Earth
from src.models.model3D import Model3D
from src.models.satellite_factory import SatelliteFactory
from src.models.simulation import Simulation
from src.utilities.singleton import Singleton
from src.views.mainView import MainView
from src.views.map3DView import Map3DView

if TYPE_CHECKING:
    from src.models.satellite import Satellite

class ApplicationController(metaclass=Singleton):

    Satellite: 'Satellite'

    def __init__(self, app: QApplication):
        self.app = app

        self.Simulation = Simulation(self)

        self.Earth = Earth()
        self.SatelliteFactory = SatelliteFactory(self)
        self.MainView = MainView(self)
        self.Model3D = Model3D(self)
        self.Map3DView = Map3DView(self, self.MainView, self.Model3D)

        self.MainView.setCentralWidget(self.Map3DView)

        self.orbitsVisible = False
        self.satsHidden = False

    def run(self):
        self.MainView.restoreSettings()
        self.MainView.show()

        self.Map3DView.run()
        self.Simulation.start()

    # Simulation Controls
    def startSim(self):
        self.Simulation.start()

    def stopSim(self):
        self.Simulation.stop()

    def setSimSpeed(self, speed: float):
        self.Simulation.setSpeed(speed)

    def setSimEpoch(self, epoch: datetime.datetime):
        self.Simulation.loadEpoch(epoch)

    def getSimEpoch(self):
        return self.Simulation.now_datetime()

    def kill(self):
        self.Simulation.stop()
        self.app.quit()

    # Satellite Controls
    def addSatellite(self, satnum: int):
        exists = self.satelliteInData(satnum)
        if not exists:
            print(f"Adding Satellite {satnum}")
            Satellite = self.SatelliteFactory.new(satnum)
            self.Model3D.addSatellite(Satellite)
            self.setOrbitVisibility(self.orbitsVisible)

    def satelliteInData(self, satnum: int):
        for Satellite in self.Model3D.data['satellites']:
            if int(Satellite.satnum) == int(satnum):
                return True
        return False

    def getSatelliteFromData(self, satnum: int):
        for Satellite in self.Model3D.data['satellites']:
            if int(Satellite.satnum) == int(satnum):
                return Satellite
        return None

    def removeSatellite(self, satnum: int):
        exists = self.satelliteInData(satnum)
        if exists:
            Satellite = self.getSatelliteFromData(satnum)
            print(f"Removing Satellite {satnum}")
            self.Model3D.removeSatellite(Satellite)


    def removeSatellites(self, satnums: list):
        for satnum in satnums:
            self.removeSatellite(satnum)

    def toggleOrbitVisibility(self):
        self.orbitsVisible = not self.orbitsVisible
        self.setOrbitVisibility(self.orbitsVisible)

    def setOrbitVisibility(self, visible: bool):
        for Satellite in self.Model3D.data['satellites']:
            Satellite.setOrbitVisibility(visible)

    def toggleHidden(self):
        self.satsHidden = not self.satsHidden
        self.setHidden(self.satsHidden)

    def setHidden(self, hidden: bool):
        for Satellite in self.Model3D.data['satellites']:
            Satellite.setHidden(hidden)

    def addSatellites(self, satnums: list):
        for satnum in satnums:
            self.addSatellite(satnum)

    def addAllSatellites(self):
        self.addSatellites(self.SatelliteFactory.listDirSatnums())

    def searchSatellites(self, search: any, isAdd: bool):
        # if its add, search for the satellite and add it like normal
        if isAdd:
            if search.isdigit():
                self.addSatellite(int(search))
            else:
                self.addSatellites(self.SatelliteFactory.getSatsBySearch(search))
        # if its not add, search for the satellite in the model and remove it
        else:
            if search.isdigit():
                self.removeSatellite(int(search))
            else:
                self.removeSatellites(self.SatelliteFactory.getSatsBySearch(search))