import json
import os
import re
import sys
from argparse import ArgumentParser
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from numpy import add
from pandas import cut
from skyfield.api import EarthSatellite, load, wgs84


class TrackerService:
    def __init__(self):
        self.parser = ArgumentParser(description="Service Satellite Tracker")
        self.parser.add_argument("--query", metavar="SATELLITE", type=str)
        self.parser.add_argument("--locate", metavar="SATELLITE", type=str)
        self.parser.add_argument("--scan", metavar="ADDRESS", type=str)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))

        json_file_path = os.path.join(
            project_root, "assets", "config", "satellite_families.json"
        )

        self.simtime = 0

        with open(json_file_path, "r") as f:
            families = json.load(f)
            self.families = [
                {**family, "query": family["query"].upper(), "name": family["name"].upper()} for family in families
            ]
            print(f"Loaded {len(self.families)} satellite families.")

    def fetch_satellite_by_name(self, sat_name):
        lines = self.load_tle_data_if_fresh(sat_name)
        if lines:
            #print("Using cached TLE data.")
            return [wgs84.satellite(lines[1], lines[2], lines[0], load.timescale())]

        print("Fetching new TLE data.")
        if any(sat_name.lower() == family["query"].lower() for family in self.families):
            print(f"'{sat_name}' is a family")
            # get the query from the name
            url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=" + quote(sat_name)
        else:
            print(f"Satellite {sat_name} is not a family")
            url = "https://celestrak.org/NORAD/elements/gp.php?NAME=" + quote(sat_name)

        response = load.tle_file(url, reload=True, filename=os.path.join("src/core/services/tle_cache", sat_name + ".tle"))
        if response:
            for sat in response:
                sat_file_path = os.path.join("src/core/services/tle_cache", f"{sat.name}.tle")
                self.save_tle_data(sat.name, [sat.name, sat.model.line1, sat.model.line2])
                print(f"Saved TLE data to {sat_file_path}")
        return response

    def locate_Satellite(self, satellite_name):
        satellite = self.fetch_or_use_local_tle(satellite_name)
        if not satellite:
            return

        ts = load.timescale()
        t = ts.now()

        # Limit the number of satellites to process with min() to avoid IndexError
        icrf = satellite.at(t)
        subpoint = wgs84.subpoint(icrf)
        lat = subpoint.latitude.degrees
        lon = subpoint.longitude.degrees

        land_or_ocean = self.GeoDataService.locate_Coordinates(lon, lat)
        if land_or_ocean:
            if land_or_ocean == "Ocean":
                dms_coords = self.GeoDataService.decimal_to_dms(lat, lon)
                print(f"{satellite_name} is currently over the ocean at {dms_coords}")
            elif land_or_ocean == "Land":
                #address = fromLatLon(lat, lon)
                print(f"{satellite_name} is currently over Land")
        else:
            print(f"{satellite_name} is currently over the coordinates {lat, lon}")

        # Assuming plot_trajectory_on_map is designed to handle a single satellite
        map = self.GeoDataService.initMap()
        self.plot_trajectory_on_map(satellite, satellite_name, 1, 3, 2, map)

    def plot_trajectory_on_map(self, satellite, satellite_name, past_hours=1, future_hours=1, mins_per_step=1, map=None):
        # Load timescale
        ts = load.timescale()
        map = self.GeoDataService.display_map(map)

        # Generate the trajectory points once
        current_time = ts.now()
        # Generate a range of times around the current time for plotting the trajectory
        minutes_range = np.arange(-past_hours * 60, future_hours * 60, mins_per_step)
        # Convert minutes to days for arithmetic with Time objects
        days_range = minutes_range / 1440  # There are 1440 minutes in a day
        times = [current_time + delta for delta in days_range]
        geocentric_positions = [satellite.at(time) for time in times]
        subpoints = [wgs84.subpoint(pos) for pos in geocentric_positions]
        lons = [subpoint.longitude.degrees for subpoint in subpoints]
        lats = [subpoint.latitude.degrees for subpoint in subpoints]

        # Handle dateline
        lons, lats = self.GeoDataService.handle_dateline(lons, lats)

        # Plot static trajectory
        map.ax.plot(lons, lats, '-', markersize=2, color='grey', label=f'Trajectory of {satellite_name}')

        # Initialize current position marker
        current_pos_marker, = map.ax.plot([], [], 'ro', label=f'Current Position of {satellite_name}')
        current_line, = map.ax.plot([], [], '-', color='red', markersize=2)
        # simple textbox to the right of the title
        textbox = map.ax.text(1.05, 0.95, '', transform=map.ax.transAxes, va='top')

        def update(frame):
            # Calculate the new current position
            current_time = ts.now()
            geocentric = satellite.at(current_time)
            subpoint = wgs84.subpoint(geocentric)
            current_lon = subpoint.longitude.degrees
            current_lat = subpoint.latitude.degrees
            idx1, idx2 = find_segment_indices(times, current_time)
            segment_lons = lons[idx1:idx2]
            segment_lats = lats[idx1:idx2]
            segment_lons, segment_lats = self.GeoDataService.handle_dateline(segment_lons, segment_lats)
            if segment_lons and segment_lats:
                segment_lons, segment_lats = self.GeoDataService.handle_dateline(segment_lons, segment_lats)

                current_line.set_data(segment_lons, segment_lats)

                # Update the current position marker
                current_pos_marker.set_data(subpoint.longitude.degrees, subpoint.latitude.degrees)

                # Update the textbox with the result from GeoDataService
                result = self.GeoDataService.locate_Coordinates(current_lon, current_lat)
                textbox.set_text(result)

            return current_pos_marker,

        def find_segment_indices(times, current_time):
            # Assuming times is a list of Skyfield Time objects
            current_time_tt = current_time.tt

            # Find closest index to the current time
            closest_idx = min(range(len(times)), key=lambda i: abs(times[i].tt - current_time_tt))

            # Define a wider range around the closest index
            # This example adds and subtracts a fixed number of indices to widen the segment
            # Adjust these values as needed for your specific scenario
            segment_width = 15  # Number of indices to include on each side of the closest point

            past_idx = max(closest_idx - segment_width, 0)  # Ensure past_idx is not less than 0
            future_idx = min(closest_idx + segment_width, len(times) - 1)  # Ensure future_idx is within bounds

            return past_idx, future_idx

        # Create an animation that updates the current position
        ani = FuncAnimation(map.fig, update, frames=range(len(times)), interval=1000, blit=False)
        map.ax.set_xlabel('Longitude (degrees)')
        map.ax.set_ylabel('Latitude (degrees)')
        map.ax.set_title(f'Predicted Trajectory of {satellite_name}')
        map.ax.legend()
        map.ax.grid(True)

        plt.show()

    # use the geo data service display map to display the location of the satellite
    def show_on_map(self, lat, lon):
        map = self.GeoDataService.initMap()
        map = self.GeoDataService.display_map(map)
        map.ax.plot(lon, lat, 'ro')
        # Customizations
        map.ax.set_title('Earth Map: Countries and Maritime Boundaries')
        map.ax.legend()
        map.ax.set_axis_off()
        plt.show()

    def save_tle_data(self, satellite_name, tle_lines):
        """Save TLE data to a file."""
        file_path = os.path.join("tle_cache", f"{satellite_name}.tle")
        print(f"Saving TLE data to {file_path}")
        with open(file_path, "w") as file:
            file.write(satellite_name + "\n")
            for line in tle_lines[1:]:  # Assuming tle_lines[0] is the satellite name
                file.write(line + "\n")

    def fetch_or_use_local_tle(self, satellite_name, max_age_days=2):
        """Fetch new TLE data if the local file is older than max_age_days, otherwise use the local file."""
        file_path = os.path.join('src/core/services/tle_cache', f"{satellite_name}.tle")

        def is_tle_fresh(file_path):

            with open(file_path, "r") as file:
                lines = file.readlines()
            tle_line1 = lines[1].strip()
            epoch_str = tle_line1[18:32]
            day_of_year, fractional_day = epoch_str.split('.')
            year = int("20" + epoch_str[:2])  # Assuming TLEs are for post-2000 satellites
            date = datetime(year, 1, 1, tzinfo=timezone.utc) + timedelta(days=int(day_of_year)-1)
            time = timedelta(days=float("0." + fractional_day))
            tle_datetime = date + time
            return (datetime.now(timezone.utc) - tle_datetime) <= timedelta(days=max_age_days)

        if os.path.exists(file_path) and is_tle_fresh(file_path):
            with open(file_path, "r") as file:
                lines = file.readlines()
            print(f"Using fresh local TLE data for {satellite_name}")

            '''will this work if the tle file looks like this ?

            STARLINK-1007
            1 44713U 19074A   24103.28263811  .00001393  00000+0  11234-3 0  9990
            2 44713  53.0547  72.9074 0001439  97.5939 262.5213 15.06412623243788
            STARLINK-1008
            1 44714U 19074B   24103.32780202  .00001055  00000+0  89684-4 0  9994
            2 44714  53.0546  72.7044 0001422  92.2969 267.8183 15.06404768243796

            will this work if the tle file looks like that?'''


            earth_satellites = []
            for i in range(0, min(20*3, len(lines)), 3):
                sat_name = lines[i].strip()
                tle_line1 = lines[i+1].strip()
                tle_line2 = lines[i+2].strip()
                earth_satellite = EarthSatellite(tle_line1, tle_line2, sat_name, load.timescale())
                earth_satellites.append(earth_satellite)
                print(f"Loaded TLE data for {sat_name}: {tle_line1}")
            return earth_satellites
        else:
            try:
                print(f"Fetching TLE data for {satellite_name}")
                earth_satellite = self.fetch_satellite_by_name(satellite_name)
                if earth_satellite:
                    self.save_tle_data(satellite_name, [sat.name for sat in earth_satellite] + [sat.model.line1 for sat in earth_satellite] + [sat.model.line2 for sat in earth_satellite])
                return earth_satellite
            except Exception as e:
                print(f"Error fetching or using local TLE for {satellite_name}: {e}, path = {file_path}")
                return None

    def query_CelesTrak(self, query_text, num_satellites=5):
        query_text = query_text.upper()
        family = next(
            (family for family in self.families if family["query"] == query_text or family["name"] == query_text),
            None,
        )

        resp = []
        if family:
            print(f"Fetching data for satellite family: {family['name']}")
            resp = self.fetch_satellites_by_family(family["query"])
        else:
            print(f"Searching for satellites named: {query_text}")
            resp = self.fetch_satellite_by_name(query_text)

        if resp:
            print(f"Found {len(resp)}, displaying first {num_satellites}.")
            return resp
        else:
            print("No satellites found with name:", query_text)
            return None

    def load_tle_data_if_fresh(self, satellite_name, max_age_hours=2):
        """Load TLE data from a file if it's fresh enough."""
        file_path = os.path.join("tle_cache", f"{quote(satellite_name)}.tle")
        if os.path.exists(file_path):
            file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_age < timedelta(hours=max_age_hours):
                with open(file_path, "r") as file:
                    lines = file.readlines()
                return lines
        return None

    # methods to use with the opengl_widgets
    # convert the lat and lon to a 3D point
    def convert_lat_lon_alt_to_3D(self, lat, lon, alt):
        return wgs84.latlon(lat, lon, alt)

    # convert the 3D point to a lat and lon
    def convert_3D_to_lat_lon(self, point):
        return wgs84.to_geocentric(point)

    # get the current position of the satellite
    def get_current_position(self, satellite):
        ts = load.timescale()
        t = ts.now()
        return satellite.at(t)

    # get the subpoint of the satellite
    def get_subpoint(self, position):
        return wgs84.subpoint(position)

    def getTime(self):
        ts = load.timescale()
        if self.simtime == 0:
            self.simtime = ts.now()
            self.initial_time = self.simtime
        else:
            self.simtime += timedelta(minutes=1)
        return ts.now() # self.simtime

    def calculate_satellite_position_at_time(self, satellite, time):
        # if satellite is a list
        if isinstance(satellite, list):
            points = []
            for sat in satellite:
               icrf = sat.at(time)
               subpoint = wgs84.subpoint(icrf)
               lat = subpoint.latitude.degrees
               lon = subpoint.longitude.degrees
               alt = subpoint.elevation.km
               point = self.convert_lat_lon_alt_to_3D(lat, lon, alt)
               points.append(point)
            return points
        else:
            icrf = satellite.at(time)
            subpoint = wgs84.subpoint(icrf)
            lat = subpoint.latitude.degrees
            lon = subpoint.longitude.degrees
            alt = subpoint.elevation.km
            point = self.convert_lat_lon_alt_to_3D(lat, lon, alt)
            return [point]

    def calculate_orbit_points_around_globe(self, satellite):
        ts = load.timescale()
        t = ts.now()

        icrf = satellite.at(t)
        subpoint = wgs84.subpoint(icrf)
        lat = subpoint.latitude.degrees
        lon = subpoint.longitude.degrees
        alt = subpoint.elevation.km

        current_time = ts.now()
        minutes_per_step = 1 # minutes
        start_time = -13 # hours
        end_time = 13 # hours
        minutes_range = np.arange(start_time * 60, end_time * 60, minutes_per_step)
        days_range = minutes_range / 1440

        times = [current_time + delta for delta in days_range]
        geocentric_positions = [satellite.at(time) for time in times]
        subpoints = [wgs84.subpoint(pos) for pos in geocentric_positions]
        lons = [subpoint.longitude.degrees for subpoint in subpoints]
        lats = [subpoint.latitude.degrees for subpoint in subpoints]
        alts = [subpoint.elevation.km for subpoint in subpoints]

        # turn the lons and lats and alts into 3D points
        points = [self.convert_lat_lon_alt_to_3D(lat, lon, alt) for lat, lon, alt in zip(lats, lons, alts)]
        return points



def JSONtoDictionary(file_path):
    file_path = Path(file_path)
    print(file_path)

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            if file_path.suffix == ".json":
                return json.load(file)
            else:
                raise ValueError(
                    f"Invalid file format: {file_path}. Expected JSON file."
                )
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON from file: {file_path}. Error: {str(e)}")


if __name__ == "__main__":
    service = TrackerService()
    args = service.parser.parse_args()

    if args.query:
        service.query_CelesTrak(args.query)
    if args.locate:
        service.locate_Satellite(args.locate)