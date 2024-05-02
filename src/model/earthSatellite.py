import datetime

from skyfield.api import EarthSatellite as SkyfieldSatellite
from skyfield.elementslib import osculating_elements_of
from skyfield.timelib import Time


class EarthSatellite(SkyfieldSatellite): # Inherit from EarthSatellite
    """Custom Satellite class to extend the Skyfield EarthSatellite class with additional functionality.
    """
    def __init__(self, line1, line2, name, **kwargs):
        super().__init__(line1, line2, name)
        self.name = name
        self.id = self.model.satnum

        def epochValid_at(self, datetime: datetime.datetime, margin: int = 7) -> bool:
            """Check if the epoch of the satellite is valid at the given time with a given margin.

            Args:
                datetime (datetime.datetime): Time to check if the epoch is valid at.
                margin (int, optional): Number of days before and after the epoch to consider valid. Defaults to 7.

            Returns:
                bool: True if the epoch is valid at the given time, False otherwise.
            """

            epoch = self.epoch.utc_datetime() # Get the epoch of the satellite in UTC
            time = datetime.astimezone(datetime.timezone.utc) # Convert the given time to UTC

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