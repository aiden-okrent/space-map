#
import datetime

import keyboard
from dateutil import tz

from src.models.model3D import Model3D
from src.models.simulation import Simulation
from src.views.mainView import MainView
from src.views.map3DView import Map3DView


class ApplicationController():
    def __init__(self, app):
        self.app = app

        self.Simulation = Simulation(self)
        self.Model3D = Model3D(self)
        self.MainView = MainView(self)
        self.Map3DView = Map3DView(self, self.MainView, self.Model3D)

        self.MainView.setCentralWidget(self.Map3DView)

    def run(self):
        self.MainView.restoreSettings()
        self.MainView.show()

        self.Simulation.loadEpoch(epoch=datetime.datetime.now(tz=tz.tzutc()))
        self.Simulation.setSpeed(1)
        #self.Simulation.start()

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
        return self.Simulation.now()

    def kill(self):
        self.Simulation.stop()
        self.app.quit()