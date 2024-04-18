'''
The controller is the main switchboard responsible for handling the communication between the model and view which don't speak to each other directly.
The controller is the first thing run by main.py and is responsible for setting up the application and handling the main event loop.
'''

from math import cos, radians, sin

from skyfield.api import Timescale, load

from model import Earth, TLEManager
from view import MainView, Map3DView


class ApplicationController:
    def __init__(self):
        self.Earth = Earth(self)
        self.TLEManager = TLEManager(self)
        self.MainView = MainView(self)
        self.Map3DView = Map3DView(self)
        self.MainView.setCentralWidget(self.Map3DView)

        # a timescale is an abstraction representing a linear timeline independent from any constraints from human-made time standards
        self.Timescale = load.timescale() # timescale from skyfield

    def run(self):
        self.MainView.restoreSettings()

    def button_clicked(self):
        sat = self.TLEManager.getSatellite("25544")

        current_time = self.Timescale.now()

        print(sat.latlon_at(current_time))




    def toggle_quality(self):
        # either 0 for low or 1 for high, so toggle between
        quality = self.Map3DView.getQuality()
        if quality == 0:
            quality = 1
        else:
            quality = 0
        self.Map3DView.setQuality(quality)