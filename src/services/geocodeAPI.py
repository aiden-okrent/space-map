# works to connect geolocation
import re

import requests
from skyfield.api import wgs84

geocodeAPIKey = str("660f1b4f58e8c145039911yozfcf7df")  # my personal API key


def fromAddress(address):
    """
    Forward geocodes the given address using the geocode API.

    Args:
        address (str): The address to be geocoded.

    Returns:
        dict: A dictionary containing the geocoded information.

    """
    url = f"https://geocode.maps.co/search?q={address}&api_key={geocodeAPIKey}"
    response = requests.get(url)
    if response.status_code == 200:
        return dict(response.json())



def fromLatLon(lat, lon):
    """
    Reverse geocodes the given latitude and longitude coordinates.

    Args:
        lat (float): The latitude coordinate.
        lon (float): The longitude coordinate.

    Returns:
        dict: A dictionary containing the reverse geocoded information.

    """
    url = f"https://geocode.maps.co/reverse?lat={lat}&lon={lon}&api_key={geocodeAPIKey}"
    response = requests.get(url)
    if response.status_code == 200:
        resp = dict(response.json())
        address_info = resp.get('address', {})

        if address_info:
            road = address_info.get('road')
            country = address_info.get('country')
            if road:
                street_address = f"{address_info.get('road')} {address_info.get('county')}, {address_info.get('state')}, {address_info.get('postcode')}, {address_info.get('country')}"
                return street_address
            else:
                return country
        elif resp.get('error'):
            return resp.get('error')

def fromSubpoint(subpoint):
    lon = float(subpoint.longitude)
    lat = float(subpoint.latitude)
    return fromLatLon(lat, lon)