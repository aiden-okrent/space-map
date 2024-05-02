import os

from skyfield.timelib import Time
from skyfield.toposlib import Geoid


class Earth(Geoid):
    """Earth model inheriting from Skyfield's Geoid class. Standard WGS84 Earth parameters are used at a given scale.
    """
    def __init__(self):
        super().__init__('Earth', 6378137.0, 298.257223563) # WGS84 Geoid
        self.GM = 398600.4418 # Standard gravitational parameter of Earth [km^3/s^2]
        self.axialTilt = 23.439291 # Earth's axial tilt [degrees]

    def getGMST_at(self, time: Time) -> float:
        """Get the Greenwich Mean Sidereal Time (GMST) at a given time.

        Args:
            time (Time): Time to calculate the GMST at.

        Returns:
            float: Greenwich Mean Sidereal Time (GMST) at the given time in degrees.
        """
        return time.gmst * 15 # GMST is in hours, convert to degrees

    def getQuality(self, quality: str = "medium") -> dict:
        """Get the textures for the Earth model at a given quality.

        Args:
            quality (str, optional): Quality of the textures. Defaults to "medium".

        Returns:
            dict: Dictionary containing the paths to the textures for the Earth model.
        """

        high = {
            "earth_triangles": 128,
            "earth_daymap": "blue_marble_NASA_land_ocean_ice_8192.png",
            "earth_clouds": "8k_earth_clouds.jpg",
            "stars_milky_way": "8k_stars_milky_way.jpg"
        }

        medium = {
            "earth_triangles": 64,
            "earth_daymap": "land_ocean_ice_2048.jpg",
            "earth_clouds": "2k_earth_clouds.jpg",
            "stars_milky_way": "2k_stars_milky_way.jpg"
        }

        low = {
            "earth_triangles": 32,
            "earth_daymap": "land_shallow_topo_350.jpg",
            "earth_clouds": "2k_earth_clouds.jpg",
            "stars_milky_way": "2k_stars_milky_way.jpg"
        }


        textures = {
            "high": high,
            "medium": medium,
            "low": low
        }[quality]

        # Build the full path to the textures but only for strings, leave the rest as is
        return {key: os.path.join("assets", "textures", value) if isinstance(value, str) else value for key, value in textures.items()}

