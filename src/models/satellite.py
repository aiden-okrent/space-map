import datetime
import random
from typing import TYPE_CHECKING

import numpy as np
from skyfield.api import EarthSatellite
from skyfield.elementslib import osculating_elements_of
from skyfield.timelib import Time
from PySide6.QtCore import Qt

from src.services.icon_service import IconService
from src.models.object3D import Object3D
from src.utilities.math3D import normalize

if TYPE_CHECKING:
    from src.controllers.controller import ApplicationController
    from src.models.simulation import Simulation

from datetime import timedelta

class Satellite(EarthSatellite, Object3D):
    """Custom Satellite class to extend the Skyfield EarthSatellite class with additional functionality.
    """

    Controller: 'ApplicationController'
    Simulation: 'Simulation'

    def __init__(self, parent, Controller: 'ApplicationController', line1: str, line2: str, name: str = None):
        Object3D.__init__(self, parent)
        EarthSatellite.__init__(self, line1, line2, name)

        self.Controller = Controller
        self.Simulation = Controller.sim

        self.satnum = self.model.satnum
        self.icon = IconService().getIcon('gis--satellite.svg', Qt.GlobalColor.white)
        self._hidden = False
        self.lastDataUpdateTime = None
        self.dataCache = None
        self.dataCacheInterval = timedelta(seconds=1)
        self.dataUpdateDelay = timedelta(milliseconds=random.randint(0, 500))

        # temporary
        earthRadius = self.Controller.model.earth.radius.km
        at = self.at(self.Simulation.now_Time())
        position = at.position.km * self.Controller.model.earth.scale_factor
        altitude = (at.distance().km * self.Controller.model.earth.scale_factor) - earthRadius
        self.translate(*position)

    @property
    def infoData(self):
        return {
            'hidden': self._hidden,
        }

    @property
    def renderData(self): # Check if cache needs updating
        if self.lastDataUpdateTime is None or (self.Simulation.now_datetime() - self.lastDataUpdateTime) > self.dataCacheInterval + self.dataUpdateDelay:
            self.updateCache()
        return self.dataCache

    def updateCache(self):
        earthRadius = self.Controller.model.earth.radius.km
        at = self.at(self.Simulation.now_Time())
        position = at.position.km * self.Controller.model.earth.scale_factor
        altitude = (at.distance().km * self.Controller.model.earth.scale_factor) - earthRadius

        self.dataCache = {
            'orbitalPath': {
                'vertices': self.orbitalPath() * self.Controller.model.earth.scale_factor,
                'color4f': [1.0, 0.0, 0.0, 0.3],
                'lineWidth': 1.0,
                'visible': True
            },
            'position': position,
            'model': {
                'texture': '',
                'translation': position,
                'rotation4f': (0, 0, 0, 0),
                'radius': .01 * earthRadius,
                'slices': 8,
                'stacks': 8,
                'visible': False,
                'colorf4': (1, 1, 1, 1)
            },
            'toSurface': {
                'lineWidth': 1.0,
                'visible': True,
                'lines': [
                    {
                        'color4f': (0.5, 0.5, 0.5, 1),
                        'vertices': [[0, 0, 0], normalize(position)],
                        'length': altitude,
                        'translation': position - (normalize(position) * altitude),
                        'rotation4f': (0, 0, 1, 0)
                    }
                ]
            }
        }
        self.lastDataUpdateTime = self.Simulation.now_datetime()

    def update(self, data):
        for key, value in data.items():
            setattr(self, key, value)
        self.updateCache()

    def getSubposition_at(self, time: Time) -> np.ndarray:

        subpoint = self.at(time).subpoint()
        lat = subpoint.latitude.degrees
        lon = subpoint.longitude.degrees

        return self.Controller.Earth.latlon_to_position(lat, lon)

    def setHidden(self, hidden: bool):
        self._hidden = hidden
        self.label.setVisible(not hidden)
        self.updateCache()

    def setOrbitVisibility(self, visible: bool):
        self._orbitVisible = visible
        self.updateCache()

    def epochValid_at(self, time: datetime.datetime, margin: int = 7) -> bool:
        # Check if the time is within the epoch of the satellite
        if isinstance(time, Time):
            time = time.utc_datetime()
        elif isinstance(time, datetime.datetime):
            time = time

        epoch = self.epoch.utc_datetime() # Get the epoch of the satellite in UTC
        time = datetime.datetime.fromtimestamp(time.timestamp(), tz=datetime.timezone.utc) # Convert the given time to UTC

        # if time is before epoch margin
        if time < epoch - datetime.timedelta(days=margin):
            return False
        # if time is after epoch margin
        if time > epoch + datetime.timedelta(days=margin):
            return False
        return True

    def orbitalPath(self) -> np.ndarray:
        # Calculate the elements of the osculating satellite's orbit
        elements = osculating_elements_of(self.at(self.Simulation.now_Time()))
        a = elements.semi_major_axis.km
        e = elements.eccentricity
        i = elements.inclination.radians
        Omega = elements.longitude_of_ascending_node.radians
        omega = elements.argument_of_periapsis.radians
        b = elements.semi_minor_axis.km

        u = np.array([
            np.cos(Omega) * np.cos(omega) - np.sin(Omega) * np.sin(omega) * np.cos(i),
            np.sin(Omega) * np.cos(omega) + np.cos(Omega) * np.sin(omega) * np.cos(i),
            np.sin(omega) * np.sin(i)
        ])

        v = np.array([
            -np.cos(Omega) * np.sin(omega) - np.sin(Omega) * np.cos(omega) * np.cos(i),
            -np.sin(Omega) * np.sin(omega) + np.cos(Omega) * np.cos(omega) * np.cos(i),
            np.cos(omega) * np.sin(i)
        ])

        # Sample the orbit to get positions
        t = np.linspace(-2 * np.pi, 2 * np.pi, 500)
        r = a * (1 - e**2) / (1 + e * np.cos(t))

        positions = np.array([r[j] * np.cos(t[j]) * u + r[j] * np.sin(t[j]) * v for j in range(len(t))])

        # Only take half of the orbit and make the first position the same as the last to close the orbit
        positions = positions[:len(positions) // 2]
        positions = np.append(positions, [positions[0]], axis=0)

        return positions
