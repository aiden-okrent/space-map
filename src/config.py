# config.py
from pathlib import Path

# Get the directory of the current script
script_dir = Path(__file__).resolve().parent

# construct full paths to all directories
CORE_DIR = script_dir / "core"
GUI_DIR = script_dir / "gui"
UTILS_DIR = script_dir / "utils"
ASSETS_DIR = script_dir / "assets"
CONFIG_DIR = ASSETS_DIR / "config"
stylesheet_path = CONFIG_DIR / "stylesheet.json"
satellite_list_items_path = CONFIG_DIR / "satellite_query_category_types.json"
map_textures = ASSETS_DIR / "images" / "solarsystemscope.com"

earth_texture_path = script_dir / "assets" / "images" / "blue_marble_NASA_land_ocean_ice_8192.png"
star_texture_path = script_dir / "assets" / "images" / "TychoSkymapII.t4_08192x04096.jpg"

geocodeAPIKey = str("660f1b4f58e8c145039911yozfcf7df")

"""
Forward Geocode (Convert human-readable address to coordinates):
https://geocode.maps.co/search?q=address&api_key=660f1b4f58e8c145039911yozfcf7df

Reverse Geocode (Convert coordinates to human-readable address):
https://geocode.maps.co/reverse?lat=latitude&lon=longitude&api_key=660f1b4f58e8c145039911yozfcf7df

Replace {address}, {latitude} and {longitude} with the values to geocode.

NOTE: Our API endpoints return JSON data by default. For different formats, append "&format={format}", where {format} is one of the following: xml, json, jsonv2, geojson, geocodejson.
"""
