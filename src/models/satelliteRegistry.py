#
from src.models.satellite import Satellite
from PySide6.QtCore import QObject, Signal

class SatelliteRegistry(QObject):

    satellites: dict[int, 'Satellite']
    satellites = {}
    updated: Signal = Signal()

    def __init__(self):
        super().__init__()

    def add(self, satnum: int, satellite: Satellite):
        self.satellites[satnum] = satellite
        self.updated.emit()

    def clear(self):
        self.satellites.clear()
        self.updated.emit()

    def remove(self, satnum: int):
        del self.satellites[satnum]
        self.updated.emit()

    def get(self, satnum: int):
        return self.satellites[satnum]

    def update(self):
        for satnum in self.satellites.keys():
            self.satellites[satnum].updateCache()
        self.updated.emit()

    def list(self):
        return self.satellites.keys()