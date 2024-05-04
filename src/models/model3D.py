#
import numpy as np
from PySide6.QtCore import QObject, Signal

from src.models.satellite import Satellite
from src.services.texture_service import TextureService


class Model3D(QObject):
    dataChanged = Signal()

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.TextureService = TextureService()
        self.data = {
            'lights': [
                {'name': 'sun', 'translation': (1000, 0, 0), 'ambient': (0.2, 0.2, 0.2, 1), 'diffuse': (1, 1, 1, 1), 'specular': (1, 1, 1, 1), 'enabled': True},
            ],
            'stars': {'texture_key': 'stars', 'texture_quality': 'low', 'texture_offset': (0, 0, 0), 'translation': (0, 0, 0), 'rotation4f': (0, 0, 0, 1), 'radius': 1000, 'slices': 16, 'stacks': 16, 'visible': True, 'colorf4': (1, 1, 1, 1)},
            'earth': {'texture_key': 'earth', 'texture_quality': 'low', 'texture_offset': (0.75, 0, 0), 'translation': (0, 0, 0), 'rotation4f': self.controller.Earth.tilt, 'radius': 1, 'slices': 16, 'stacks': 16, 'visible': True, 'colorf4': (1, 1, 1, 1)},
            'XYZAxis': {'lineWidth': 3, 'lines': [
                {'color4f': (1, 0, 0, 1), 'vertices': [(0, 0, 0), (1, 0, 0)], 'length': 1, 'translation': (-1, -1, -1), 'rotation4f': (0, 0, 0, 1)}, # X Axis is Red
                {'color4f': (0, 1, 0, 1), 'vertices': [(0, 0, 0), (0, 1, 0)], 'length': 1, 'translation': (-1, -1, -1), 'rotation4f': (0, 0, 1, 0)}, # Y Axis is Green
                {'color4f': (0, 0, 1, 1), 'vertices': [(0, 0, 0), (0, 0, 1)], 'length': 1, 'translation': (-1, -1, -1), 'rotation4f': (0, 1, 0, 0)} # Z Axis is Blue (up)
            ]},
            'poles': {'cylinders': [
                {'color4f': (1, 0, 0, 1), 'translation': (0, 0, 1), 'rotation4f': (0, 0, 1, 0), 'height': 0.2, 'radius': 0.02}, # Red North Pole
                {'color4f': (0, 0, 1, 1), 'translation': (0, 0, -1), 'rotation4f': (180, 0, 1, 0), 'height': 0.2, 'radius': 0.02} # Blue South Pole
            ]},
            'satellites': []
        }

        # gluCylinder arguments: (quadric, base radius, top radius, height, slices, stacks)

    def getData(self):
        return self.data.copy()

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
        for sat in self.data['satellites']:
            if sat.satnum == satnum:
                sat.update(data)
                self.dataChanged.emit()
                break

    def addSatellite(self, satellite: Satellite):
        self.data['satellites'].append(satellite)
        self.dataChanged.emit()

    def removeSatellite(self, satnum):
        for sat in self.data['satellites']:
            if sat.satnum == satnum:
                self.data['satellites'].remove(sat)
                self.dataChanged.emit()
                break

    def getTexture(self, key):
        item = self.data[key]
        return self.TextureService.getTexture(item['texture_quality'], item['texture_key'])

