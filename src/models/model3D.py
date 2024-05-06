#
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.controllers.controller import ApplicationController
    from src.models.earth import Earth
    from src.models.simulation import Simulation

import numpy as np
from PySide6.QtCore import QObject, Signal

from src.models.satellite import Satellite
from src.services.texture_service import TextureService


class Model3D(QObject):
    dataChanged: Signal = Signal()

    Controller: 'ApplicationController'
    Earth: 'Earth'
    Simulation: 'Simulation'

    def __init__(self, Controller: 'ApplicationController'):
        super().__init__()
        self.Controller = Controller
        self.Earth = Controller.Earth
        self.Simulation = Controller.Simulation

        self.TextureService = TextureService()
        self.quality = 'low'

        self._satellites = []

    @property
    def data(self):
        scale = self.Earth.scale
        earthRadius = self.Earth.radius.km
        return {
                'lights': [
                {'name': 'sun', 'translation': (100 * earthRadius, 0, 0), 'ambient': (0.2, 0.2, 0.2, 1), 'diffuse': (1, 1, 1, 1), 'specular': (1, 1, 1, 1), 'enabled': True},
            ],
            'stars': {
                'texture': 'stars',
                'texture_quality': self.quality,
                'texture_offset': (0, 0, 0),
                'translation': (0, 0, 0),
                'rotation4f': (0, 0, 0, 1),
                'radius': 150 * earthRadius,
                'slices': 16,
                'stacks': 16,
                'visible': True,
                'colorf4': (1, 1, 1, 1)
            },
            'rotations': {
                'earth_Oblique': (23.439291, 0, 1, 0),
                'earth_Spin': (self.Earth.getGMST_at(self.Simulation.now_Time()), 0, 0, 1)
            },
            'earth': {
                'texture': 'earth',
                'texture_quality': self.quality,
                'texture_offset': (0.75, 0, 0),
                'translation': (0, 0, 0),
                'rotation4f': (0, 0, 0, 0),
                'radius': earthRadius,
                'slices': 32,
                'stacks': 32,
                'visible': True,
                'colorf4': (1, 1, 1, 1)
            },
            'XYZAxis': {
                'lineWidth': 3,
                'visible': True,
                'lines': [
                    {
                    'color4f': (1, 0, 0, 1),
                    'vertices': [(0, 0, 0), (1, 0, 0)],
                    'length': earthRadius,
                    'translation': (-earthRadius, -earthRadius, -earthRadius),
                    'rotation4f': (0, 0, 0, 1)
                    },  # X Axis is Red
                    {
                    'color4f': (0, 1, 0, 1),
                    'vertices': [(0, 0, 0), (0, 1, 0)],
                    'length': earthRadius,
                    'translation': (-earthRadius, -earthRadius, -earthRadius),
                    'rotation4f': (0, 0, 1, 0)
                    },  # Y Axis is Green
                    {
                    'color4f': (0, 0, 1, 1),
                    'vertices': [(0, 0, 0), (0, 0, 1)],
                    'length': earthRadius,
                    'translation': (-earthRadius, -earthRadius, -earthRadius),
                    'rotation4f': (0, 1, 0, 0)
                    }  # Z Axis is Blue (up)
                ]
            },
            'poles': {
                'cylinders': [
                    {
                    'color4f': (1, 0, 0, 1),
                    'translation': (0, 0, earthRadius),
                    'rotation4f': (0, 0, 1, 0),
                    'height': 0.2 * earthRadius,
                    'radius': 0.02 * earthRadius
                    },  # Red North Pole
                    {
                    'color4f': (0, 0, 1, 1),
                    'translation': (0, 0, -earthRadius),
                    'rotation4f': (180, 0, 1, 0),
                    'height': 0.2 * earthRadius,
                    'radius': 0.02 * earthRadius
                    }  # Blue South Pole
                ]
            },
            'satellites': self._satellites
        }

    def updateData(self, key, value):
        if key in self.data:
            self.data[key] = value
            self.dataChanged.emit()
        else:
            raise KeyError(f"Key '{key}' not found in data dictionary")

    def addData(self, key, value):
        self.data[key] = value
        self.dataChanged.emit()

    def removeData(self, key):
        if key in self.data:
            del self.data[key]
            self.dataChanged.emit()

    def updateSatellite(self, satnum, data):
        for sat in self._satellites:
            if sat.satnum == satnum:
                sat.update(data)
                self.dataChanged.emit()
                break

    def addSatellite(self, satellite: Satellite):
        self._satellites.append(satellite)
        print(f"Added satellite {satellite.name} to 3D model")
        self.dataChanged.emit()

    def removeSatellite(self, satellite: Satellite):
        self._satellites.remove(satellite)
        print(f"Removed satellite {satellite.name} from 3D model")
        self.dataChanged.emit()

    def getTexture(self, key):
        item = self.data[key]
        return self.TextureService.getTexture(item['texture_quality'], item['texture'])

    def setQuality(self, quality):
        self.quality = quality
        self.dataChanged.emit()

