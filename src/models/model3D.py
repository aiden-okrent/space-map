#
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
            'stars': {'texture': self.TextureService.getTexture('low', 'stars'), 'radius': 5, 'slices': 32, 'stacks': 32, 'visible': True, 'colorf4': (1, 1, 1, 1)},
            'earth': {'texture': self.TextureService.getTexture('low', 'earth'), 'radius': 1, 'slices': 32, 'stacks': 32, 'visible': True, 'colorf4': (1, 1, 1, 1)},
            'satellites': []
        }

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

