#

import asyncio
import datetime
import os
import socket
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.controllers.controller import ApplicationController

from config.paths import TLE

from src.models.satellite import Satellite
from src.models.object3D import Object3D


class SatelliteFactory:
    """Factory class to manage, fetch, and build Satellite objects from TLE data."""

    Controller: 'ApplicationController'

    def __init__(self, Controller: 'ApplicationController'):
        super().__init__()
        self.Controller = Controller
        self.model = Controller.model

    def getPath(self, satnum):
        """Get the path to the TLE file for a given satnum.

        Args:
            satnum (str): The Catalog ID of the satellite.

        Raises:
            ValueError: If no Catalog ID is provided.

        Returns:
            str: The path to the TLE file.
        """
        if satnum:
            for filename in os.listdir(TLE):
                if str(satnum) in filename:
                    return os.path.join(TLE, filename)
            return None
        else:
           print("No Catalog ID provided.")
           return None

    def listTLE(self):
        """List all TLE files in the TLE directory.

        Returns:
            dict: Dictionary containing the Catalog ID and the filename of each TLE file in the directory.
        """
        tle_dict = {}
        for filename in os.listdir(TLE):
            with open(os.path.join(TLE, filename), 'r') as file:
                tle_data = file.readlines()
                tle_dict[tle_data[0].strip()] = filename.replace(".tle", "")
        return tle_dict

    def openTLE(self, path: str):
        """Open a TLE file and return the data.

        Args:
            path (str): The path to the TLE file.

        Raises:
            ValueError: If no TLE path is provided.

        Returns:
            list: The TLE data as a list of strings for each line.
        """
        if path:
            with open(path, 'r') as file:
                tle_data = file.readlines()
                return tle_data
        else:
            print("No TLE path provided.")
            return None

    def fetchTLE(self, satnum: str):
        """Download TLE data from Celestrak for a given Catalog ID.

        Args:
            satnum (str): The Catalog ID of the satellite.

        Raises:
            FileNotFoundError: If the TLE file is not found after downloading.
            ValueError: If no TLE data is found for the Catalog ID.
            ValueError: If no satellite is found in the Celestrak database for the Catalog ID.

        Returns:
            list: The TLE data as a list of strings for each line.
        """
        if not satnum:
            return None
        import urllib.request

        async def download_tle_data(satnum: str):
            url = "https://celestrak.org/NORAD/elements/gp.php?CATNR=" + str(satnum) + "&FORMAT=TLE"
            try:
                socket.setdefaulttimeout(8)
                response = await asyncio.get_event_loop().run_in_executor(None, urllib.request.urlopen, url)
                tle_data = await asyncio.get_event_loop().run_in_executor(None, response.read)
                with open(os.path.join(TLE, str(satnum) + ".tle"), 'wb') as file:
                    file.write(tle_data)
            except Exception as e:
                print("Error occurred while loading TLE file:", str(e))

        asyncio.run(download_tle_data(satnum))
        file = self.getPath(satnum)
        if file:
            tle_data = self.openTLE(file)
            if not tle_data:
                print("No TLE data found for satnum: " + str(satnum), "in path: " + file)
                return None
            else:
                if "No GP data found" in tle_data:
                    os.remove(file)
                    print("No satellite found in Celestrak database for satnum: " + str(satnum))
                    return None
                else:
                    return tle_data

    def listDir(self):
        """List all Catalog IDs of satellites with TLE files in the TLE directory.

        Returns:
            list: List of Catalog IDs of satellites with TLE files.
        """
        satnums = [int()]
        for filename in os.listdir(TLE):
            satnum = filename.replace(".tle", "")
            satnums.append(int(satnum))
        return satnums

    def searchDir(self, text: str):
        if text == "":
            return None

        if text.isdigit():
            satnums = [int(filename.replace(".tle", "")) for filename in os.listdir(TLE) if text == filename.replace(".tle", "")]
        else:
            satnums = [int(filename.replace(".tle", "")) for filename in os.listdir(TLE) if text.lower() in open(os.path.join(TLE, filename)).read().lower()]
        satnums = [int(text)] if satnums == [] else satnums

        return satnums

    '''
    CURTIS
    1 59507U 98067WG  24125.41361547  .00045442  00000+0  67851-3 0  9999
    2 59507  51.6343 172.0553 0001518  93.7234 266.3931 15.54580231  3654

    '''

    def new(self, satnum: int):
        """Create a new Satellite object from TLE data.

        Args:
            satnum (int): The Catalog ID of the satellite.

        Returns:
            Satellite: The Satellite object created from the TLE data.
        """

        print("Building Satellite object for Catalog ID: " + str(satnum))
        if not satnum:
            print("No satnum provided.")
            return None

        path = self.getPath(satnum)
        if not path:
            print("No existing TLE file found for satnum " + str(satnum), "downloading new TLE file from Celestrak database.")
            tle_data = self.fetchTLE(satnum)
            path = self.getPath(satnum)
        else:
            tle_data = self.openTLE(path)

        if not tle_data == None:
            satellite = Satellite(parent=self.model.eci, Controller=self.Controller, line1=tle_data[1], line2=tle_data[2], name=tle_data[0].strip())
            print("Satellite built with Catalog ID: " + str(satnum))
            if not satellite.epochValid_at(datetime.datetime.now()):
                print("Epoch is invalid for satellite with catalog ID: " + str(satnum), "within a margin of " + str(14), "days. Requesting fresh TLE data.")
                tle_data = self.fetchTLE(satnum)
                satellite = Satellite(parent=self.model.eci, Controller=self.Controller, line1=tle_data[1], line2=tle_data[2], name=tle_data[0].strip())
            return satellite
        else:
            print("Failed to build Satellite object for Catalog ID: " + str(satnum), "because the TLE data returned None.")
            return None


# example usage
# satellite_factory = SatelliteFactory()
# satellite = satellite_factory.new("25544")
# print(satellite.epoch.utc_datetime())
