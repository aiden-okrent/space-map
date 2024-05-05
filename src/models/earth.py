import os
import sys
from math import cos, radians, sin
from typing import Tuple

import numpy as np
from skyfield.timelib import Time
from skyfield.toposlib import Geoid


class Earth(Geoid):
    """Earth model inheriting from Skyfield's Geoid class. Standard WGS84 Earth parameters are used at a given scale.

    Compatible with SimTime class for time-dependent calculations such as GMST, solar position, seasons, etc.
    """
    def __init__(self):
        super().__init__('Earth', 6378137.0, 298.257223563) # WGS84 Geoid
        self.scale = 0.001 # Scale factor for Earth's radius
        self.GM = 398600.4418 #* self.scale**3 # Standard gravitational parameter of Earth [km^3/s^2]
        self.radius.km = self.radius.km * self.scale # Convert Earth's radius to scaled units

    def getGMST_at(self, time: Time) -> float:
        """Get the Greenwich Mean Sidereal Time (GMST) at a given time.

        Args:
            time (Time): Time to calculate the GMST at.

        Returns:
            float: Greenwich Mean Sidereal Time (GMST) at the given time in degrees.
        """
        return time.gmst * 15 # GMST is in hours, convert to degrees

    def latlon_to_position(self, lat: float, lon: float) -> np.ndarray:
        """Convert latitude and longitude to a position on the Earth's surface.

        Args:
            lat (float): Latitude in degrees.
            lon (float): Longitude in degrees.

        Returns:
            np.ndarray: Position on the Earth's surface in ECEF coordinates [x, y, z] in km.
        """

        # Convert latitude and longitude to ECEF coordinates
        x = self.radius.km * cos(radians(lat)) * cos(radians(lon))
        y = self.radius.km * cos(radians(lat)) * sin(radians(lon))
        z = self.radius.km * sin(radians(lat))

        return np.array([x, y, z])