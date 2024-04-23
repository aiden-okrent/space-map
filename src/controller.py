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
        # when toolbar text input (current_sat_input is the action, current_sat_input_line is the QLineEdit)
        self.MainView.current_sat_id_spinbox.editingFinished.connect(self.track_Satellite)
        self.refresh_combobox()
        self.MainView.satellite_combobox.activated.connect(self.sat_combobox_activated)
        self.MainView.setCentralWidget(self.Globe3DView)

    def run(self):
        self.MainView.restoreSettings()
        self.Globe3DView.run()

    def refresh_combobox(self):
        self.MainView.satellite_combobox.clear()
        satellites = self.get_satellite_dict()
        # first, find the iss and put it at the top. use 25544 as id
        self.MainView.satellite_combobox.addItem('---------')
        self.MainView.satellite_combobox.addItem('ISS (ZARYA)')
        for sat_name in satellites:
            if sat_name == 'ISS (ZARYA)':
                continue
            self.MainView.satellite_combobox.addItem(sat_name)

        if self.current_satellite is None:
            return
        self.MainView.satellite_combobox.setCurrentIndex(self.MainView.satellite_combobox.findText(self.current_satellite.name))

    def track_Satellite(self):
        text = self.MainView.current_sat_id_spinbox.textFromValue(self.MainView.current_sat_id_spinbox.value())
        sat = self.TLEManager.getSatellite(text)
        if sat is None:
            return
            #self.setCurrentSatellite(None)
            #self.MainView.current_sat_id_spinbox.setValue(0)
            #self.Globe3DView.setScene(self.Globe3DView.SceneView.GLOBE_VIEW)
        else:
            self.setCurrentSatellite(sat)
            self.Globe3DView.setScene(self.Globe3DView.SceneView.TRACKING_VIEW)
        self.refresh_combobox()


    def sat_combobox_activated(self, index):
        value = int(self.get_satellite_dict()[self.MainView.satellite_combobox.currentText()])

        self.MainView.current_sat_id_spinbox.setValue(value)

        self.track_Satellite()

    def get_satellite_dict(self):
        return self.TLEManager.tle_name_dict()

    def setCurrentSatellite(self, satellite: Satellite):
        self.current_satellite = satellite

    def get_current_satellite_translation(self):
        if self.current_satellite is None:
            return None
        return self.current_satellite.calc_sat_pos_xyz()


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
