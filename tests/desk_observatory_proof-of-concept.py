from skyfield.api import Topos, load
from datetime import datetime

# Your current location's longitude and latitude
longitude = 84.5826111111111  # Example: 84.5826111111111 for Kennesaw, GA
latitude = 34.039794444444446  # Example: 34.039794444444446 for Kennesaw, GA

# Load satellite TLE data
#stations_url = 'http://celestrak.com/NORAD/elements/stations.txt'
#satellites = load.tle_file(stations_url)

satellite_categories_menu = {
    "Special-Interest Satellites": [
        "Last 30 Days' Launches",
        "Space Stations",
        "100 (or so) Brightest",
        "Active Satellites",
        "Analyst Satellites",
        "Russian ASAT Test Debris (COSMOS 1408)",
        "Chinese ASAT Test Debris (FENGYUN 1C)",
        "IRIDIUM 33 Debris",
        "COSMOS 2251 Debris"
    ],
    "Weather & Earth Resources Satellites": [
        "Weather",
        "Earth Resources",
        "Search & Rescue (SARSAT)",
        "Disaster Monitoring",
        "Tracking and Data Relay Satellite System (TDRSS)",
        "ARGOS Data Collection System",
        "Planet",
        "Spire"
    ],
    "Communications Satellites": [
        "Active Geosynchronous",
        "GEO Protected Zone",
        "GEO Protected Zone Plus",
        "Intelsat",
        "SES",
        "Iridium",
        "Iridium NEXT",
        "Starlink",
        "OneWeb",
        "Orbcomm",
        "Globalstar",
        "Swarm",
        "Amateur Radio",
        "Experimental Comm",
        "Other Comm",
        "SatNOGS",
        "Gorizont",
        "Raduga",
        "Molniya"
    ],
    "Navigation Satellites": [
        "GNSS",
        "GPS Operational",
        "GLONASS Operational",
        "Galileo",
        "Beidou",
        "Satellite-Based Augmentation System (WAAS/EGNOS/MSAS)",
        "Navy Navigation Satellite System (NNSS)",
        "Russian LEO Navigation"
    ],
    "Scientific Satellites": [
        "Space & Earth Science",
        "Geodetic",
        "Engineering",
        "Education"
    ],
    "Miscellaneous Satellites": [
        "Miscellaneous Military",
        "Radar Calibration",
        "CubeSats",
        "Other Satellites"
    ]
}

query_text_mapping = {
    "Last 30 Days' Launches": "last-30-days",
    "Space Stations": "stations",
    "100 (or so) Brightest": "visual",
    "Active Satellites": "active",
    "Analyst Satellites": "analyst",
    "Russian ASAT Test Debris (COSMOS 1408)": "1982-092",
    "Chinese ASAT Test Debris (FENGYUN 1C)": "1999-025",
    "IRIDIUM 33 Debris": "iridium-33-debris",
    "COSMOS 2251 Debris": "cosmos-2251-debris",
    "Weather": "weather",
    "NOAA": "noaa",
    "GOES": "goes",
    "Earth Resources": "resource",
    "Search & Rescue (SARSAT)": "sarsat",
    "Disaster Monitoring": "dmc",
    "Tracking and Data Relay Satellite System (TDRSS)": "tdrss",
    "ARGOS Data Collection System": "argos",
    "Planet": "planet",
    "Spire": "spire",
    "Active Geosynchronous": "geo",
    "GEO Protected Zone": "gpz",
    "GEO Protected Zone Plus": "gpz-plus",
    "Intelsat": "intelsat",
    "SES": "ses",
    "Iridium": "iridium",
    "Iridium NEXT": "iridium-NEXT",
    "Starlink": "starlink",
    "OneWeb": "oneweb",
    "Orbcomm": "orbcomm",
    "Globalstar": "globalstar",
    "Swarm": "swarm",
    "Amateur Radio": "amateur",
    "Experimental Comm": "x-comm",
    "Other Comm": "other-comm",
    "SatNOGS": "satnogs",
    "Gorizont": "gorizont",
    "Raduga": "raduga",
    "Molniya": "molniya",
    "GNSS": "gnss",
    "GPS Operational": "gps-ops",
    "GLONASS Operational": "glo-ops",
    "Galileo": "galileo",
    "Beidou": "beidou",
    "Satellite-Based Augmentation System (WAAS/EGNOS/MSAS)": "sbas",
    "Navy Navigation Satellite System (NNSS)": "nnss",
    "Russian LEO Navigation": "musson",
    "Space & Earth Science": "science",
    "Geodetic": "geodetic",
    "Engineering": "engineering",
    "Education": "education",
    "Miscellaneous Military": "military",
    "Radar Calibration": "radar",
    "CubeSats": "cubesat",
    "Other Satellites": "other"
}


tle_url = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=weather&FORMAT=tle'

query = ''
format = 'tle'

# a menu select to choose a category to query, where if the supercategory is selected, the subcategories are all used
print("Satellite Categories:")
for i, category in enumerate(satellite_categories_menu):
    print(f"{i+1}. {category}")

selected_category = input("Select a category number: ")
if selected_category.isdigit() and int(selected_category) in range(1, len(satellite_categories_menu)+1):
    selected_category_index = int(selected_category) - 1
    selected_category = list(satellite_categories_menu.keys())[selected_category_index]
    selected_subcategories = satellite_categories_menu[selected_category]
    print(f"{selected_category}: Select a subcategory number")
    for i, subcategory in enumerate(selected_subcategories):
        print(f"{i+1}. {subcategory}")
    selected_subcategory = input("Select a subcategory number: ")
    if selected_subcategory.isdigit() and int(selected_subcategory) in range(1, len(selected_subcategories)+1):
        selected_subcategory_index = int(selected_subcategory) - 1
        query = query_text_mapping[selected_subcategories[selected_subcategory_index]]  # Set the query as the mapped string
    else:
        print("Invalid subcategory number selected.")
else:
    print("Invalid category number selected.")

# Set the TLE URL based on the query and format
tle_url = f'https://celestrak.org/NORAD/elements/gp.php?GROUP={query}&FORMAT={format}'
satellites = load.tle_file(tle_url, filename='queried_satellites.txt', reload=True)

# Use current date and time or specify a datetime
ts = load.timescale()
#t = ts.now()  # or use ts.utc(2024, 4, 2, 18, 0, 0) for specific time
t = ts.utc(2024, 4, 15, 22, 30, 0)

# Your location
observer = Topos(latitude_degrees=latitude, longitude_degrees=longitude)

# Iterate through satellites to find which are above a given elevation angle
for sat in satellites:
    difference = sat - observer
    topocentric = difference.at(t)
    alt, az, distance = topocentric.altaz()

    if alt.degrees > 0:  # Checking if the satellite is above the horizon
        print(f"\033[92m{sat.name} is above the horizon\033[0m")
    else:
        print(f"\033[91m{sat.name.lower()}\033[0m")

# Note: This is a simple visibility check. You can add distance constraints as needed.
