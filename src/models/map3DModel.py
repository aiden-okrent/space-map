#
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.controllers.controller import ApplicationController

import numpy as np
from PySide6.QtCore import QObject, Signal
from src.models.object3D import Object3D
from src.models.texture_gl import TextureGL
from src.models.earth import Earth


class Object3DList(QObject):
    objects: list["Object3D"]
    updated: Signal = Signal()

    def __init__(self):
        super().__init__()
        self.objects = []

    def add(self, obj: "Object3D"):
        self.objects.append(obj)
        self.updated.emit()

    def clear(self):
        self.objects.clear()
        self.updated.emit()

    def remove(self, obj: "Object3D"):
        self.objects.remove(obj)
        self.updated.emit()

    def list(self):
        return self.objects

    def update(self):
        for obj in self.objects:
            obj.attributeChanged.emit()
        self.updated.emit()


class Map3DModel(QObject):
    dataChanged: Signal = Signal()

    def __init__(self, Controller: "ApplicationController"):
        super().__init__()

        print("Initializing Map3DModel")

        self.Controller = Controller
        self.Simulation = Controller.sim
        self.objects = Controller.objects

        self.quality = "low"

        self.root = Object3D(
            None
        )  # International Celestial Reference System (ICRS) frame
        self.root.scale = 0.001  # scale factor to convert km to meters

        self.eci = Object3D(
            self.root
        )  # Earth-Centered Inertial (ECI) frame accounting for Earth's Obliquity
        self.eci.rotate(
            23.439291, 0, 1, 0
        )  # rotate the ECI frame to account for Earth's Obliquity

        self.earth = Earth(
            self.eci
        )  # Earth object which rotates with the Earth's Sidereal Time (GMST)

        self.objects.append(self.root)
        self.objects.append(self.eci)
        self.objects.append(self.earth)

    @property
    def data(self):
        earthRadius = self.earth.radius.km
        return {
            "dataChanged": self.dataChanged,
            "lights": [
                {
                    "name": "sun",
                    "translation": (100 * earthRadius, 0, 0),
                    "ambient": (0.2, 0.2, 0.2, 1),
                    "diffuse": (1, 1, 1, 1),
                    "specular": (1, 1, 1, 1),
                    "enabled": True,
                },
            ],
            "stars": {
                "texture": "stars",
                "quality": self.quality,
                "texture_offset": (0, 0, 0),
                "translation": (0, 0, 0),
                "rotation4f": (0, 0, 0, 1),
                "radius": 150 * earthRadius,
                "slices": 16,
                "stacks": 16,
                "visible": True,
                "colorf4": (1, 1, 1, 1),
            },
            "rotations": {
                "earth_Oblique": (23.439291, 0, 1, 0),
                "earth_Spin": (
                    self.earth.getGMST_at(self.Simulation.now_Time()),
                    0,
                    0,
                    1,
                ),
            },
            "earth": {
                "texture": "earth",
                "quality": self.quality,
                "texture_offset": (0.75, 0, 0),
                "translation": (0, 0, 0),
                "rotation4f": (0, 0, 0, 0),
                "radius": earthRadius,
                "slices": 32,
                "stacks": 32,
                "visible": True,
                "colorf4": (1, 1, 1, 1),
            },
            "XYZAxis": {
                "lineWidth": 3,
                "visible": True,
                "lines": [
                    {
                        "color4f": (1, 0, 0, 1),
                        "vertices": [(0, 0, 0), (1, 0, 0)],
                        "length": earthRadius,
                        "translation": (-earthRadius, -earthRadius, -earthRadius),
                        "rotation4f": (0, 0, 0, 1),
                    },  # X Axis is Red
                    {
                        "color4f": (0, 1, 0, 1),
                        "vertices": [(0, 0, 0), (0, 1, 0)],
                        "length": earthRadius,
                        "translation": (-earthRadius, -earthRadius, -earthRadius),
                        "rotation4f": (0, 0, 1, 0),
                    },  # Y Axis is Green
                    {
                        "color4f": (0, 0, 1, 1),
                        "vertices": [(0, 0, 0), (0, 0, 1)],
                        "length": earthRadius,
                        "translation": (-earthRadius, -earthRadius, -earthRadius),
                        "rotation4f": (0, 1, 0, 0),
                    },  # Z Axis is Blue (up)
                ],
            },
            "poles": {
                "cylinders": [
                    {
                        "color4f": (1, 0, 0, 1),
                        "translation": (0, 0, earthRadius),
                        "rotation4f": (0, 0, 1, 0),
                        "height": 0.2 * earthRadius,
                        "radius": 0.02 * earthRadius,
                    },  # Red North Pole
                    {
                        "color4f": (0, 0, 1, 1),
                        "translation": (0, 0, -earthRadius),
                        "rotation4f": (180, 0, 1, 0),
                        "height": 0.2 * earthRadius,
                        "radius": 0.02 * earthRadius,
                    },  # Blue South Pole
                ]
            },
        }
