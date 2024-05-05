#
import datetime
from typing import Any, Dict

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


class ApplicationController(metaclass=Singleton):

    def __init__(self, app: QApplication):
        self.app = app

        self.Simulation = Simulation(self)

        self.Earth = Earth()
        self.SatelliteFactory = SatelliteFactory(self)
        self.MainView = MainView(self)
        self.Model3D = Model3D(self)
        self.Map3DView = Map3DView(self, self.MainView, self.Model3D)

        self.MainView.setCentralWidget(self.Map3DView)

    def run(self):
        self.MainView.restoreSettings()
        self.MainView.show()

        self.Map3DView.run()

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
        if self.Model3D.data['satellites']:
            for sat in self.Model3D.data['satellites']:
                if sat.satnum == satnum:
                    return
        sat = self.SatelliteFactory.new(satnum)
        self.Model3D.addSatellite(sat)

    def processQuery(self, query: any):
        if isinstance(query, int):
            self.addSatellite(query)
        elif isinstance(query, str):
            self.addSatellites(self.SatelliteFactory.getSatsBySearch(query))

    def toggleOrbit(self):
        for sat in self.Model3D.data['satellites']:
            sat.setOrbitVisible(not sat._orbitVisible)

    def addSatellites(self, satnums: list):
        for satnum in satnums:
            self.addSatellite(satnum)

    def addAllSatellites(self):
        self.addSatellites(self.SatelliteFactory.listDirSatnums())

    def searchSatellites(self, search: str):
        self.addSatellites(self.SatelliteFactory.getSatsBySearch(search))