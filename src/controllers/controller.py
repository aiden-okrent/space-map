#
from PySide6.QtWidgets import QApplication

from src.models.satelliteFactory import SatelliteFactory
from src.models.simulation import Simulation
from src.views.mainView import MainView

from src.models.map3DModel import Map3DModel
from src.models.satelliteRegistry import SatelliteRegistry


class ApplicationController:

    def __init__(self, app: QApplication):
        self.app = app

        self.SatelliteRegistry = SatelliteRegistry()
        self.objects = []

        self.sim = Simulation(self)
        self.model = Map3DModel(self)
        self.SatelliteFactory = SatelliteFactory(self)

        self.MainView = MainView(self)

    def run(self):
        self.MainView.restoreSettings()
        self.MainView.show()
        self.sim.start()

        self.updateSatelliteRegistry(self.SatelliteFactory.searchDir("ISS (ZARYA)"))

    def setSimSpeed(self, speed: float):
        self.sim.setSpeed(speed)

    def resetSimTime(self):
        self.sim.setSpeed(1.0)
        self.sim.resetEpoch()
        self.updateSatelliteRegistry(None)

    def setQuality(self, quality: str):
        self.model.quality = quality

    def getTexture(self, key: str):
        return
        item = self.model.data[key]
        return self.TextureService.getTexture(item["quality"], item["texture"])

    def updateSatelliteRegistry(self, satnums=None):
        print("Updating Satellite Registry with", satnums)
        if satnums:
            for satnum in satnums:
                if satnum not in self.SatelliteRegistry.satellites.keys():
                    sat = self.SatelliteFactory.new(satnum)
                    self.objects.append(sat)
                    self.SatelliteRegistry.add(satnum, sat)
                else:
                    self.objects.remove(self.SatelliteRegistry.get(satnum))
                    self.SatelliteRegistry.remove(satnum)
        else:
            self.SatelliteRegistry.clear()
