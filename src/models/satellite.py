import datetime

import numpy as np
from skyfield.api import EarthSatellite
from skyfield.elementslib import osculating_elements_of
from skyfield.timelib import Time

from src.models.simulation import Simulation


class Satellite(EarthSatellite): # Inherit from skyfield's EarthSatellite class
    """Custom Satellite class to extend the Skyfield EarthSatellite class with additional functionality.
    """
    def __init__(self, line1, line2, name, **kwargs):
        super().__init__(line1, line2, name)
        self.name = name
        self.satnum = self.model.satnum
        #self.sim = Simulation(self)
        print("Satellite")

        self.data = {
            'name': self.name,
            'satnum': self.satnum,
            'epoch': self.epoch.utc_datetime(),
            'position': self.at(self.epoch).position.km,
            'orbitalPath': {'vertices': self.orbitalPath(), 'color4f': [1.0, 1.0, 1.0, 1.0], 'lineWidth': 1.0},
        }

    def update(self, data):
        for key, value in data.items():
            setattr(self, key, value)

    def getData(self):
        return self.data.copy()

    def epochValid_at(self, time: datetime.datetime, margin: int = 7) -> bool:
        """Check if the epoch of the satellite is valid at the given time with a given margin.

        Args:
            datetime (datetime.datetime): Time to check if the epoch is valid at.
            margin (int, optional): Number of days before and after the epoch to consider valid. Defaults to 7.

        Returns:
            bool: True if the epoch is valid at the given time, False otherwise.
        """
        if isinstance(time, Time):
            time = time.utc_datetime()
        elif isinstance(time, datetime.datetime):
            time = time

        epoch = self.epoch.utc_datetime() # Get the epoch of the satellite in UTC
        time = datetime.datetime.fromtimestamp(time.timestamp(), tz=datetime.timezone.utc) # Convert the given time to UTC

        # if time is before epoch margin
        if time < epoch - datetime.timedelta(days=margin):
            return False
        # if time is after epoch margin
        if time > epoch + datetime.timedelta(days=margin):
            return False
        return True

    def orbitalElements_at(self, time: Time) -> dict:
        """Get the mean orbital elements of the satellite's orbit at the given time.

        Returns:
            dict: Dictionary containing the mean orbital elements of the satellite's orbit at the given time.
        """
        tleElements = { # basic elements incuded in the 2-line element set
            'epoch': self.epoch.utc_datetime(),
            'inclination': self.model.inclo,
            'right_ascension': self.model.nodeo,
            'eccentricity': self.model.ecco,
            'argument_of_perigee': self.model.argpo,
            'mean_anomaly': self.model.mo,
            'mean_motion': self.model.no_kozai,
            'revolution_number': self.model.revnum
        }

        sgp4Elements = osculating_elements_of(self.at(time), reference_frame=None, gm_km3_s2=None) # advanced elements calculated by SGP4

        return {**tleElements, **sgp4Elements} # Merge the two dictionaries

    def orbitalPath(self) -> np.ndarray:
        # Calculate the elements of the osculating satellite's orbit
        elements = osculating_elements_of(self.at(self.epoch), reference_frame=None, gm_km3_s2=None)
        a = elements.semi_major_axis.km
        e = elements.eccentricity
        i = elements.inclination.radians
        Omega = elements.longitude_of_ascending_node.radians
        omega = elements.argument_of_periapsis.radians
        b = elements.semi_minor_axis.km

        u = np.array([
            np.cos(Omega) * np.cos(omega) - np.sin(Omega) * np.sin(omega) * np.cos(i),
            np.sin(Omega) * np.cos(omega) + np.cos(Omega) * np.sin(omega) * np.cos(i),
            np.sin(omega) * np.sin(i)
        ])

        v = np.array([
            -np.cos(Omega) * np.sin(omega) - np.sin(Omega) * np.cos(omega) * np.cos(i),
            -np.sin(Omega) * np.sin(omega) + np.cos(Omega) * np.cos(omega) * np.cos(i),
            np.cos(omega) * np.sin(i)
        ])

        # Sample the orbit to get positions
        t = np.linspace(-2 * np.pi, 2 * np.pi, 500)
        r = a * (1 - e**2) / (1 + e * np.cos(t))

        positions = np.array([r[j] * np.cos(t[j]) * u + r[j] * np.sin(t[j]) * v for j in range(len(t))])

        # Only take half of the orbit and make the first position the same as the last to close the orbit
        positions = positions[:len(positions) // 2]
        positions = np.append(positions, [positions[0]], axis=0)

        return positions
