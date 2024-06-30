#
import numpy as np
from typing import List, Tuple
from OpenGL import GL, GLU
from skyfield.timelib import Time
from PySide6.QtCore import QObject


# Class Object3D
class Object3D(QObject):
    def __init__(self, parent: "Object3D" = None):
        QObject.__init__(self)
        self.parent: Object3D = parent
        self.children: list[Object3D] = []
        self.is_visible: bool = True
        self.color = (1.0, 1.0, 1.0, 1.0)

        self.position = np.array([0.0, 0.0, 0.0])  # (x, y, z)
        self.rotation = (0.0, 0.0, 0.0, 1.0)  # (angle, x, y, z)

        parent.add_child(self) if parent else None

    def add_child(self, child: "Object3D"):
        self.children.append(child)
        child.parent = self

    def translate(self, x: float, y: float, z: float):
        self.position += np.array([x, y, z])

    def rotate(self, angle: float, x: float, y: float, z: float):
        self.rotation = (angle, x, y, z)

    def world_position(self):
        if self.parent:
            return self.parent.world_position() + self.position
        else:
            return self.position

    def world_rotation(self):
        if self.parent:
            return self.parent.world_rotation() + self.rotation
        else:
            return self.rotation

    def draw(self, time: Time):
        GL.glPushMatrix()
        GL.glTranslatef(*self.world_position())
        GL.glRotatef(*self.rotation)
        GL.glColor4f(*self.color)

        quadric = GLU.gluNewQuadric()
        GLU.gluSphere(quadric, 1, 32, 32)
        GLU.gluDeleteQuadric(quadric)

        for child in self.children:
            child.draw(time)
        GL.glPopMatrix()


from math import cos, radians, sin
import numpy as np
from skyfield.timelib import Time
from skyfield.toposlib import Geoid
from src.models.object3D import Object3D
from PySide6.QtGui import QMatrix4x4


class Earth(Geoid, Object3D):
    def __init__(self, parent: Object3D):
        Object3D.__init__(self, parent)  # Earth sphere
        Geoid.__init__(self, "WGS84", 6378137.0, 0.0033528)  # WGS84 geoid
        self.GM = 398600.4418  # Standard gravitational parameter of Earth [km^3/s^2]
        self.scale_factor = 0.001  # Scale factor to convert km to meters
        self.radius.km = (
            self.radius.km * self.scale_factor
        )  # Convert Earth radius to meters

        self.is_visible = True
        self.color = (0.0, 0.0, 1.0, 1.0)  # Blue

    @property
    def get_world_transform(self, time: Time) -> QMatrix4x4:
        self.rotate(self.getGMST_at(time), 0, 0, 1)
        super().get_world_transform(time)
        # that overrides the inherited method from Object3D to rotate the Earth object to the current GMST before returning the new world transform.

    def getGMST_at(self, time: Time) -> float:
        return time.gmst * 15

    def latlon_to_position(self, lat: float, lon: float) -> np.ndarray:
        x = self.radius.km * cos(radians(lat)) * cos(radians(lon))
        y = self.radius.km * cos(radians(lat)) * sin(radians(lon))
        z = self.radius.km * sin(radians(lat))
        return np.array([x, y, z])  # Return ECEF coordinates
