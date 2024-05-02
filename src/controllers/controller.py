#
from models.earth import Earth
from models.satellite import Satellite
from models.satellite_factory import SatelliteFactory
from models.simtime import SimTime
from utilities import constants as C
from utilities import math2D, math3D


class ApplicationController():
    def __init__(self, app):
        self.app = app

        self.Earth = Earth()



    def run(self):
        self.MainView.restoreSettings()
        self.Globe3DView.run()