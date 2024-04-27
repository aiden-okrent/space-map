'''
The controller is the main switchboard responsible for handling the communication between the model and view which don't speak to each other directly.
The controller is the first thing run by main.py and is responsible for setting up the application and handling the main event loop.
'''

import keyboard
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.basemap import Basemap
from skyfield.api import Timescale, load

from controller_protocol import ControllerProtocol
from model import Earth, Satellite, TLEManager
from view import Globe3DView, MainView


class ApplicationController(ControllerProtocol):
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
        self.Globe3DView = Globe3DView(self, self.Earth)

        # add the GlobeOverlayView widget to the MainView as a transparent overlay on top of the Globe3DView

        # set the current satellite to the ISS for debugging
        self.setCurrentSatellite(self.TLEManager.getSatellite('25544'))

        self.MainView.current_sat_id_spinbox.editingFinished.connect(self.track_Satellite)
        self.refresh_combobox()
        self.MainView.satellite_combobox.activated.connect(self.sat_combobox_activated)
        self.MainView.setCentralWidget(self.Globe3DView)

        # bind whenever the key F3 is pressed to fire .toggleVisibility()
        keyboard.on_press_key("F3", self.toggleOverlayVisibility)

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

        """     def display_2D_map(self):
        # opens the earth texture in a matplotlib window and displays the satellite's position as a red dot longitude and latitude
        fig = plt.figure()

        icrf = self.current_satellite.at(self.Timescale.now())
        subpoint = icrf.subpoint()
        longitude = subpoint.longitude.degrees
        latitude = subpoint.latitude.degrees
        height = subpoint.elevation.km

        h = height
        m = Basemap(projection='nsper',lon_0=longitude,lat_0=latitude, satellite_height=h*1000.,resolution='l')
        m.drawparallels(np.arange(-90.,120.,30.))
        m.drawmeridians(np.arange(0.,420.,60.))
        m.warpimage(image=self.Earth.textures_8k["earth_daymap"])
        x, y = m(longitude, latitude)

        m.plot(x, y, 'ro', markersize=10)

        plt.show()

        """
    def display_2D_map(self):
        # better version using get2DCartesianCoordinates
        fig = plt.figure()

        coords = self.Earth.get2DCartesianCoordinates(self.current_satellite, self.Timescale.now())
        longitude = coords[0].degrees
        latitude = coords[1].degrees

        #m = Basemap(projection='geos', lon_0=longitude, resolution='l')
        m = Basemap(projection='geos',lon_0=longitude,resolution='l',rsphere=(6378137.00,6356752.3142))
        m.drawparallels(np.arange(-90., 120., 30.))
        m.drawmeridians(np.arange(0., 420., 60.))
        m.warpimage(image=self.Earth.textures_2k["earth_daymap"])
        x, y = m(longitude, latitude)
        m.plot(x, y, 'ro', markersize=10)
        plt.show()

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
        quality = self.Globe3DView.getQuality().value
        #if quality is 0, set to 1, if its 1, set to 2, if its 2, set to 0
        quality = (quality + 1) % 3

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

    def toggleOverlayVisibility(self, event):
        self.Globe3DView.toggleOverlayVisibility()

    def toggle_camera_mode(self):
        mode = self.Globe3DView.camera.getCameraMode()
        if mode == self.Globe3DView.camera.CameraMode.STATIC:
            mode = self.Globe3DView.camera.CameraMode.FOLLOW
        elif mode == self.Globe3DView.camera.CameraMode.FOLLOW:
            mode = self.Globe3DView.camera.CameraMode.ORBIT
        else:
            mode = self.Globe3DView.camera.CameraMode.STATIC

        self.Globe3DView.camera.setCameraMode(mode)