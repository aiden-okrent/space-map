#
from PySide6.QtCore import QObject, Signal


class Model3D(QObject):
    dataChanged = Signal()

    def __init__(self, controller):
        self.controller = controller
