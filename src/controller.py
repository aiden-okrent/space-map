'''
The controller is the main switchboard responsible for handling the communication between the model and view which don't speak to each other directly.
The controller is the first thing run by main.py and is responsible for setting up the application and handling the main event loop.
'''

from skyfield.api import Timescale, load

from model import Earth, Satellite, TLEManager
from view import Globe3DView, MainView


class ApplicationController:
    def __init__(self):
        # app variables
        self.scale = 1/1000 # scale of the earth model
        self.current_satellite = None # current satellite being tracked
        self.Timescale = load.timescale() # a timescale is an abstraction representing a linear timeline independent from any constraints from human-made time standards

        # models
        self.Earth = Earth(self, self.scale)
        self.TLEManager = TLEManager(self)

        # views
        self.MainView = MainView(self)
        self.Globe3DView = Globe3DView(self)
        self.MainView.setCentralWidget(self.Globe3DView)

    def run(self):
        self.MainView.restoreSettings()
        self.Globe3DView.run()

    def show_ISS_button_clicked(self):
        sat = self.TLEManager.getSatellite("25544")
        self.setCurrentSatellite(sat)
        self.Globe3DView.setScene(self.Globe3DView.SceneView.TRACKING_VIEW)

    def setCurrentSatellite(self, satellite: Satellite):
        self.current_satellite = satellite

    def get_current_satellite_translation(self):
        if self.current_satellite is None:
            return None
        current_time = self.Timescale.now()
        lat, lon, elv = self.current_satellite.latlon_at(current_time)
        point = self.Earth.latlon(lat, lon, elv)
        translation = self.Earth.point_to_translation(point)
        #print(translation)
        return translation


    # view toggles
    def toggle_quality(self):
        # either 0 for low or 1 for high, so toggle between
        RenderQuality = self.Globe3DView.RenderQuality
        quality = self.Globe3DView.getQuality()
        if quality == RenderQuality.LOW:
            quality = RenderQuality.HIGH
        else:
            quality = RenderQuality.LOW
        self.Globe3DView.setQuality(quality)

    def toggle_scene(self):
        scene = self.Globe3DView.current_scene
        if scene == self.Globe3DView.SceneView.GLOBE_VIEW:
            scene = self.Globe3DView.SceneView.TRACKING_VIEW
        elif scene == self.Globe3DView.SceneView.TRACKING_VIEW:
            scene = self.Globe3DView.SceneView.EXPLORE_VIEW
        else:
            scene = self.Globe3DView.SceneView.GLOBE_VIEW

        self.Globe3DView.setScene(scene)
