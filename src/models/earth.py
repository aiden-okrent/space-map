import os

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
