import json
import os
import sys
from argparse import ArgumentParser
from pathlib import Path
from urllib.parse import quote

import geopandas
import matplotlib.pyplot as plt
from geodatasets import get_path, get_url
from shapely.geometry import Point
from skyfield.api import load, wgs84

from .geocodeAPI import fromLatLon
from .mapComponents import MapComponents

ne_10m_admin_0_countries = geopandas.read_file('src/assets/geodata/Natural_Earth_quick_start/10m_cultural/ne_10m_admin_0_countries.shp')
ne_10m_geography_marine_polys = geopandas.read_file('src/assets/geodata/ne_10m_geography_marine_polys/ne_10m_geography_marine_polys.shp')
ne_50m_admin_0_countries = geopandas.read_file('src/assets/geodata/ne_50m_admin_0_countries/ne_50m_admin_0_countries.shp')

""" # 10m_cultural Shapefiles
ne_10m_admin_0_countries = geopandas.read_file('src/assets/geodata/Natural_Earth_quick_start/10m_cultural/ne_10m_admin_0_countries.shp')
ne_10m_admin_0_boundary_lines_land = geopandas.read_file('src/assets/geodata/Natural_Earth_quick_start/10m_cultural/ne_10m_admin_0_boundary_lines_land.shp')


admin_0_disputed_areas = geopandas.read_file('src/assets/geodata/Natural_Earth_quick_start/10m_cultural/ne_10m_admin_0_disputed_areas.shp')
admin_1_states_provinces = geopandas.read_file('src/assets/geodata/Natural_Earth_quick_start/10m_cultural/ne_10m_admin_1_states_provinces.shp')
admin_1_states_provinces_lakes = geopandas.read_file('src/assets/geodata/Natural_Earth_quick_start/10m_cultural/ne_10m_admin_1_states_provinces_lakes.shp')
admin_2_counties_lakes = geopandas.read_file('src/assets/geodata/Natural_Earth_quick_start/10m_cultural/ne_10m_admin_2_counties_lakes.shp')
boundary_lines_disputed_areas = geopandas.read_file('src/assets/geodata/Natural_Earth_quick_start/10m_cultural/ne_10m_admin_0_boundary_lines_disputed_areas.shp')
boundary_lines_land = geopandas.read_file('src/assets/geodata/Natural_Earth_quick_start/10m_cultural/ne_10m_admin_0_boundary_lines_land.shp')
parks_and_protected_lands_area = geopandas.read_file('src/assets/geodata/Natural_Earth_quick_start/10m_cultural/ne_10m_parks_and_protected_lands_area.shp')
populated_places = geopandas.read_file('src/assets/geodata/Natural_Earth_quick_start/10m_cultural/ne_10m_populated_places.shp')
roads = geopandas.read_file('src/assets/geodata/Natural_Earth_quick_start/10m_cultural/ne_10m_roads.shp')
urban_areas = geopandas.read_file('src/assets/geodata/Natural_Earth_quick_start/10m_cultural/ne_10m_urban_areas.shp')

# 10m_physical Shapefiles
ne_10m_lakes = geopandas.read_file('src/assets/geodata/Natural_Earth_quick_start/10m_physical/ne_10m_lakes.shp')

antarctic_ice_shelves_lines = geopandas.read_file('src/assets/geodata/Natural_Earth_quick_start/10m_physical/ne_10m_antarctic_ice_shelves_lines.shp')
coastline = geopandas.read_file('src/assets/geodata/Natural_Earth_quick_start/10m_physical/ne_10m_coastline.shp')
lakes = geopandas.read_file('src/assets/geodata/Natural_Earth_quick_start/10m_physical/ne_10m_lakes.shp')
rivers_lake_centerlines = geopandas.read_file('src/assets/geodata/Natural_Earth_quick_start/10m_physical/ne_10m_rivers_lake_centerlines.shp')
ocean = geopandas.read_file('src/assets/geodata/Natural_Earth_quick_start/10m_physical/ne_10m_ocean.shp')
glaciated_areas = geopandas.read_file('src/assets/geodata/Natural_Earth_quick_start/10m_physical/ne_10m_glaciated_areas.shp')


# 10m_geography_marine Shapefiles
ne_10m_geography_marine_polys = geopandas.read_file('src/assets/geodata/ne_10m_geography_marine_polys/ne_10m_geography_marine_polys.shp')


# 10m_ Shapefiles
ne_10m_coastline = geopandas.read_file('src/assets/geodata/ne_10m_physical_building_blocks_all/ne_10m_coastline.shp')
ne_10m_land_ocean_label_points = geopandas.read_file('src/assets/geodata/ne_10m_physical_building_blocks_all/ne_10m_land_ocean_label_points.shp')
ne_10m_land_ocean_seams = geopandas.read_file('src/assets/geodata/ne_10m_physical_building_blocks_all/ne_10m_land_ocean_seams.shp')
ne_10m_minor_islands_coastline = geopandas.read_file('src/assets/geodata/ne_10m_physical_building_blocks_all/ne_10m_minor_islands_coastline.shp')
ne_10m_minor_islands_label_points = geopandas.read_file('src/assets/geodata/ne_10m_physical_building_blocks_all/ne_10m_minor_islands_label_points.shp')

ne_10m_land = geopandas.read_file('src/assets/geodata/ne_10m_land/ne_10m_land.shp')
ne_50m_admin_0_countries = geopandas.read_file('src/assets/geodata/ne_50m_admin_0_countries/ne_50m_admin_0_countries.shp')



Culture Datasets
ne_10m_admin_0_disputed_areas:                  The boundaries of disputed areas at the admin level 0.
ne_10m_admin_1_states_provinces:                The boundaries of states and provinces at the admin level 1.
ne_10m_admin_1_states_provinces_lakes:          The boundaries of states and provinces at the admin level 1, including lakes.
ne_10m_admin_2_counties_lakes:                  The boundaries of counties at the admin level 2, including lakes.
ne_10m_admin_0_boundary_lines_disputed_areas:   The boundary lines of disputed areas at the admin level 0.
ne_10m_admin_0_boundary_lines_land:             The boundary lines of land at the admin level 0.
ne_10m_parks_and_protected_lands_area:          The areas of parks and protected lands.
ne_10m_populated_places:                        The locations of populated places.
ne_10m_roads:                                   All roads on Earth.
ne_10m_urban_areas:                             The boundaries of all urban areas such as cities.

Physical Datasets
ne_10m_antarctic_ice_shelves_lines: The boundary lines of Antarctic ice shelves.
ne_10m_coastline: The coastline.
ne_10m_lakes: The boundaries of lakes.
ne_10m_rivers_lake_centerlines: The centerlines of rivers and lakes.
ne_10m_ocean: The entire ocean area of the world in one polygon.
ne_10m_glaciated_areas: The boundaries of glaciated areas.

Miscellaneous Datasets
ne_10m_geography_marine_polys: The boundaries of marine areas.

Physical Datasets
ne_10m_physical_building_blocks_all:

"""
ne_50m_physical_land = geopandas.read_file('src/assets/geodata/ne_50m_physical/ne_50m_land.shp')
ne_50m_physical_ocean = geopandas.read_file('src/assets/geodata/ne_50m_physical/ne_50m_ocean.shp')

ne_50m_geography_marine_polys = geopandas.read_file('src/assets/geodata/Natural_Earth_quick_start/50m_physical/ne_50m_geography_marine_polys.shp')
ne_50m_admin_0_boundary_lines_maritime_indicator = geopandas.read_file('src/assets/geodata/Natural_Earth_quick_start/50m_cultural/ne_50m_admin_0_boundary_lines_maritime_indicator.shp')
ne_10m_admin_0_label_points = geopandas.read_file('src/assets/geodata/ne_10m_cultural_building_blocks_all/ne_10m_admin_0_label_points.shp')
script_dir = Path(__file__).resolve().parent.parent.parent
#earth_texture_path = script_dir / "assets" / "images" / "land_ocean_ice_2048.jpg"
earth_texture_path = script_dir / "assets" / "images" / "solarsystemscope.com" / "2k_earth_daymap.jpg"


class GeoDataService:
    def __init__(self):
        self.parser = ArgumentParser(description="Service Geo Data Handler")
        self.parser.add_argument("--locate", type=float, help="Locate the coordinates on Earth.")
        self.parser.add_argument("--coords", type=float, help="Enters coordinates in Lon,Lat format.", nargs=2)
        # add a new argument to the parser to display the map
        self.parser.add_argument("--map", action="store_true", help="Display the map of countries and oceans.")


    def locate_Coordinates(self, lon, lat):
        if not self.validate_coordinates(lat, lon):
            print("Invalid coordinates: ", lat, lon)
            return
        return self.check_location_land_or_sea(lon, lat)

    def check_Country(self, lon, lat):
        point = Point(lon, lat)
        for country in ne_50m_admin_0_countries:
            if country.contains(point):
                return country['ADMIN']

    def check_location_land_or_sea(self, lon, lat):
        point = Point(lon, lat)

        if ne_10m_geography_marine_polys.contains(point).any():
            return 'Ocean'
        elif ne_10m_admin_0_countries.contains(point).any():
            address = self.check_Country(lat, lon)
            return 'Land', address
        else:
            return 'Not Land nor Ocean'

    def validate_coordinates(self, lat, lon):
        """
        Validates the given longitude and latitude coordinates.

        Parameters:
        lon (float): Longitude of the location in decimal format.
        lat (float): Latitude of the location in decimal format.

        Returns:
        bool: True if the coordinates are valid, False otherwise.
        """
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return True
        return False

    def decimal_to_dms(self, lat, lon):
        # Latitude
        lat_direction = "N" if lat >= 0 else "S"
        lat_deg = int(abs(lat))
        lat_min = int((abs(lat) - lat_deg) * 60)
        lat_sec = (abs(lat) - lat_deg - lat_min/60) * 3600

        # Longitude
        lon_direction = "E" if lon >= 0 else "W"
        lon_deg = int(abs(lon))
        lon_min = int((abs(lon) - lon_deg) * 60)
        lon_sec = (abs(lon) - lon_deg - lon_min/60) * 3600

        # Formatting to "DD°MM'SS.S\"D"
        lat_result = f"{lat_deg}°{lat_min:02}'{lat_sec:.1f}\"{lat_direction}"
        lon_result = f"{lon_deg}°{lon_min:02}'{lon_sec:.1f}\"{lon_direction}"

        return f"{lat_result} {lon_result}"

    def initMap(self):
        fig, ax = plt.subplots(figsize=(10, 10))

        ax.imshow(plt.imread(earth_texture_path), extent=[-180, 180, -90, 90])
        ne_50m_admin_0_countries.boundary.plot(ax=ax, color='black', linewidth=0.25)
        #ne_50m_geography_marine_polys.boundary.plot(ax=ax, color='black', linestyle='--', linewidth=0.25)

        map = MapComponents(fig, ax, None)
        return map

    def display_map(self, map, labels=False):

        if labels:
            for x, y, label in zip(ne_50m_admin_0_countries.geometry.centroid.x, ne_50m_admin_0_countries.geometry.centroid.y, ne_50m_admin_0_countries['ADMIN']):
                map.ax.text(x, y, label, fontsize=6, ha='center', va='center')
        return map

    def handle_dateline(self, longitudes, latitudes):
        """
        Insert None values into longitude and latitude arrays where the trajectory crosses the dateline.
        """
        new_lons = []
        new_lats = []

        # Assume the first point doesn't cross the dateline
        new_lons.append(longitudes[0])
        new_lats.append(latitudes[0])

        for i in range(1, len(longitudes)):
            # Check if we've crossed the dateline
            if longitudes[i-1] is not None and longitudes[i] is not None:
                if abs(longitudes[i] - longitudes[i-1]) > 180:
                    # Insert None to "break" the line plot
                    new_lons.append(None)
                    new_lats.append(None)

            new_lons.append(longitudes[i])
            new_lats.append(latitudes[i])

        return new_lons, new_lats



if __name__ == "__main__":
    service = GeoDataService()
    args = service.parser.parse_args()

    if args.locate:
        if args.coords:
            lon, lat = args.coords
            print(service.locate_Coordinates(lon, lat))
        else:
            print("locate: Please provide coordinates.")
    if args.map:
        map = service.initMap()
        service.display_map(map)
