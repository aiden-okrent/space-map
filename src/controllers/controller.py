#
import datetime

import keyboard
from dateutil import tz
from PySide6.QtWidgets import QApplication

from src.models.earth import Earth
from src.models.model3D import Model3D
from src.models.satellite_factory import SatelliteFactory
from src.models.simulation import Simulation, SimulationSingleton
from src.views.mainView import MainView
from src.views.map3DView import Map3DView


class ApplicationController():
    def __init__(self, app: QApplication):
        self.app = app

        #self.Simulation = Simulation(self)

        self.SatelliteFactory = SatelliteFactory()
        self.MainView = MainView(self)
        self.Earth = Earth()
        self.Model3D = Model3D(self)
        self.Map3DView = Map3DView(self, self.MainView, self.Model3D)

        self.MainView.setCentralWidget(self.Map3DView)

    def run(self):
        self.MainView.restoreSettings()
        self.MainView.show()

        self.Map3DView.run()

    # Simulation Controls
    def startSim(self):
        return
        #self.Simulation.start()

    def stopSim(self):
        return
        #self.Simulation.stop()

    def setSimSpeed(self, speed: float):
        return
        #self.Simulation.setSpeed(speed)

    def setSimEpoch(self, epoch: datetime.datetime):
        return
        #self.Simulation.loadEpoch(epoch)

    def getSimEpoch(self):
        return
        #return self.Simulation.now_datetime()

    def kill(self):
        return
        #self.Simulation.stop()
        #self.app.quit()

    # Satellite Controls
    def addSatellite(self, satnum: int):
        if self.Model3D.data['satellites']:
            for sat in self.Model3D.data['satellites']:
                if sat.satnum == satnum:
                    return
        sat = self.SatelliteFactory.new(satnum)
        self.Model3D.addSatellite(sat)