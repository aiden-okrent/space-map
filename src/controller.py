'''
The controller is the main switchboard responsible for handling the communication between the model and view which don't speak to each other directly.
The controller is the first thing run by main.py and is responsible for setting up the application and handling the main event loop.
'''

from skyfield.api import Timescale, load

from model import Earth, Satellite, TLEManager
from view import Globe3DView, MainView


class ApplicationController:
    def __init__(self):
        self.Earth = Earth(self)
        self.TLEManager = TLEManager(self)
        self.MainView = MainView(self)

        self.Globe3DView = Globe3DView(self)
        #self.Globe3DView.setQuality(self.Globe3DView.RenderQuality.LOW)
        #self.Globe3DView.setScene(self.Globe3DView.SceneView.GLOBE_VIEW)

        self.current_satellite = None # current satellite being tracked


        self.MainView.setCentralWidget(self.Globe3DView)

        # a timescale is an abstraction representing a linear timeline independent from any constraints from human-made time standards
        self.Timescale = load.timescale() # timescale from skyfield

    def run(self):
        self.MainView.restoreSettings()
        self.refresh_toolbar_actions_text()


    def show_ISS_button_clicked(self):
        sat = self.TLEManager.getSatellite("25544")
        self.set_current_satellite(sat)
        self.Globe3DView.setScene(self.Globe3DView.SceneView.SATELLITE_TRACKING_VIEW)
        self.refresh_toolbar_actions_text()

    def set_current_satellite(self, satellite: Satellite):
        self.current_satellite = satellite

    def get_current_satellite_translation(self):
        if self.current_satellite is None:
            return None
        current_time = self.Timescale.now()
        lat, lon, elv = self.current_satellite.latlon_at(current_time)
        point = self.Earth.geoid.latlon(lat, lon, elv)
        translation = self.Earth.point_to_translation(point)
        return translation


    def refresh_toolbar_actions_text(self):
        self.MainView.setQualityText(self.Globe3DView.getQuality())
        self.MainView.setSceneText(self.Globe3DView.current_scene)

    def toggle_quality(self):
        # either 0 for low or 1 for high, so toggle between
        RenderQuality = self.Globe3DView.RenderQuality
        quality = self.Globe3DView.getQuality()
        if quality == RenderQuality.LOW:
            quality = RenderQuality.HIGH
        else:
            quality = RenderQuality.LOW
        self.Globe3DView.setQuality(quality)
        self.refresh_toolbar_actions_text()


    def toggle_scene(self):
        scene = self.Globe3DView.current_scene
        if scene == self.Globe3DView.SceneView.GLOBE_VIEW:
            scene = self.Globe3DView.SceneView.SATELLITE_TRACKING_VIEW
        elif scene == self.Globe3DView.SceneView.SATELLITE_TRACKING_VIEW:
            scene = self.Globe3DView.SceneView.SATELLITES_EXPLORE_VIEW
        else:
            scene = self.Globe3DView.SceneView.GLOBE_VIEW

        self.Globe3DView.setScene(scene)
        self.refresh_toolbar_actions_text()