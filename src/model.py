'''
In MVC, the model is the part of the application that is responsible for managing the data.
It receives requests from the controller and returns the data to the controller.
The model is not aware of the view, so the data returned by the model is independent of the presentation.

For space-map, the Model has several components:
- Satellite: A class representing a satellite object. It holds all data related to a satellite and methods for basic calculations using it.
- Earth: A class representing the Earth globe and all parameters related to it, as well as methods for basic calculations with it.
- TLEManager: Manages TLE orbital data; Reading from file, validating Epoch, requesting new data from Celestrak, and building Satellite objects.
- Observer: A class representing an observer on the Earth's surface. It holds data such as location and methods for calculating satellite visibility.

'''

'''


Skyfield: Home • Table of Contents • Changelog • API Reference
Earth Satellites¶

Skyfield is able to predict the positions of Earth satellites by loading satellite orbital elements from Two-Line Element (TLE) files — published by organizations like CelesTrak — and running them through the SGP4 satellite propagation routine. But there several limitations to be aware of when using Skyfield to generate positions for artificial satellites in Earth orbit:

    Do not expect perfect agreement between any two pieces of software that are trying to predict satellite positions from TLE data files. As Vallado, Crawford, and Hujsak document in their crucial paper Revisiting Spacetrack Report #3, there are many slightly different versions of the basic satellite prediction algorithm circulating in the wild. Happily, Skyfield uses the corrected and updated version of the algorithm that they created as part of writing that report.

    Satellite positions have limited precision. Here’s what Revisiting Spacetrack Report #3 says in Appendix B:

        “The maximum accuracy for a TLE is limited by the number of decimal places in each field. In general, TLE data is accurate to about a kilometer or so at epoch and it quickly degrades.”

    Satellite elements go rapidly out of date. As explained below in Checking a TLE’s epoch, you will want to pay attention to the “epoch” — the date on which an element set is most accurate — of every TLE element set you use. Elements are only useful for a week or two on either side of the epoch date. For later dates, you will want to download a fresh set of elements. For earlier dates, you will want to pull an old TLE from the archives.

    A satellite’s orbital elements are in constant flux from effects like atmospheric drag, the Moon’s gravity, and its own propulsion. In particular, the true anomaly parameter can swing wildly for satellites with nearly circular orbits, because the reference point from which true anomaly is measured — the satellite’s perigee — can be moved by even slight perturbations to the orbit.

    Given the low accuracy of TLE elements, there is no point in calling the usual Skyfield observe() method that repeatedly re-computes an object’s position to account for the light-travel time to the observer. As we will see below, the difference is irrelevant for Earth satellites and not worth the added expense of re-computing the position several times in a row.

Note that even though several TLE elements have names that might remind you of Kepler orbital elements, like inclination and eccentricity, the SGP4 routine does not treat a satellite’s orbit as a simple ellipse, and will produce a different position than a Kepler orbit would.
Loading TLE element sets¶

Skyfield supports several approaches to loading TLE data.
Downloading a TLE file¶

You can find satellite element sets at the NORAD Two-Line Element Sets page of the Celestrak web site.

Beware that the two-line element (TLE) format is very rigid. The meaning of each character is based on its exact offset from the beginning of the line. You must download and use the element set’s text without making any change to its whitespace.

Skyfield loader objects offer a tle_file() method that can download and cache a file full of satellite elements from a site like Celestrak. A popular observing target for satellite observers is the International Space Station, which is listed in Celestrak’s stations.txt file:

from skyfield.api import load, wgs84

stations_url = 'http://celestrak.org/NORAD/elements/stations.txt'
satellites = load.tle_file(stations_url)
print('Loaded', len(satellites), 'satellites')

Loaded 60 satellites

Indexing satellites by name or number¶

If you want to operate on every satellite in the list that you have loaded from a file, you can use Python’s for loop. But if you instead want to select individual satellites by name or number, try building a lookup dictionary using Python’s dictionary comprehension syntax:

by_name = {sat.name: sat for sat in satellites}
satellite = by_name['ISS (ZARYA)']
print(satellite)

ISS (ZARYA) catalog #25544 epoch 2014-01-20 22:23:04 UTC

by_number = {sat.model.satnum: sat for sat in satellites}
satellite = by_number[25544]
print(satellite)

ISS (ZARYA) catalog #25544 epoch 2014-01-20 22:23:04 UTC

Performing a TLE query¶

In addition to offering traditional text files like stations.txt and active.txt, Celestrak supports queries that return TLE elements.

But be careful!

Because every query to Celestrak requests the same filename tle.php Skyfield will by default only download the first result. Your second, third, and all subsequent attempts to query Celestrak will simply return the contents of the tle.php file that’s already on disk — giving you the results of your first query over and over again.

Here are two easy remedies:

    Specify the argument reload=True, which asks Skyfield to always download new results even if there is already a file on disk. Every query will overwrite the file with new data.
    Or, specify a filename= argument so that each query’s result is saved to a file specific to that query. Each query result will be saved to disk with its own filename.

Here’s an example of the second approach — code that requests one specific satellite, saving the result to a file specific to the query:

n = 25544
url = 'https://celestrak.org/satcat/tle.php?CATNR={}'.format(n)
filename = 'tle-CATNR-{}.txt'.format(n)
satellites = load.tle_file(url, filename=filename)
print(satellites)

[<EarthSatellite ISS (ZARYA) catalog #25544 epoch 2020-11-07 22:23:09 UTC>]

The above code will download a new result each time it’s asked for a satellite that it hasn’t yet fetched. But note that when asked again for the same satellite, it will simply reload the existing file from disk unless reload=True is specified.
Loading a TLE file from a string¶

If your program has already loaded the text of a TLE file, and you don’t need Skyfield to handle the download for you, then you can turn it into a list of Skyfield satellites with the parse_tle_file() function. The function is a Python generator, so we use Python’s list() constructor to load all the satellites:

from io import BytesIO
from skyfield.iokit import parse_tle_file

f = BytesIO(stations_txt_bytes)
satellites = list(parse_tle_file(f))

If it’s simpler in your case, you can instead pass parse_tle_file() a simple list of lines.
Loading a single TLE set from strings¶

If your program already has the two lines of TLE data for a satellite and doesn’t need Skyfield to download and parse a Celestrak file, you can instantiate an EarthSatellite directly.

from skyfield.api import EarthSatellite

ts = load.timescale()
line1 = '1 25544U 98067A   14020.93268519  .00009878  00000-0  18200-3 0  5082'
line2 = '2 25544  51.6498 109.4756 0003572  55.9686 274.8005 15.49815350868473'
satellite = EarthSatellite(line1, line2, 'ISS (ZARYA)', ts)
print(satellite)

ISS (ZARYA) catalog #25544 epoch 2014-01-20 22:23:04 UTC

Checking a TLE’s epoch¶

The “epoch” date of a satellite element set is the all-important date and time for which the set of elements is most accurate, and before or after which they go rapidly out of date. You can access this value as an attribute of the object in case your program wants to check how old the elements are:

print(satellite.epoch.utc_jpl())

A.D. 2014-Jan-20 22:23:04.0004 UTC

If the epoch is too far in the past, you can provide tle_file() with the reload option to force it to download new elements even if the file is already on disk. (Note, though, that there is no guarantee that the new elements will be up-to-date if the source file is not frequently updated for the satellite you are interested in — so this pattern might make you download a new file on each run until the satellite’s elements are finally updated.)

t = ts.utc(2014, 1, 23, 11, 18, 7)

days = t - satellite.epoch
print('{:.3f} days away from epoch'.format(days))

if abs(days) > 14:
    satellites = load.tle_file(stations_url, reload=True)

2.538 days away from epoch

You can read T.S. Kelso on Twitter to follow along with the drama as various satellite element sets go out-of-date each month and await updates from their respective organizations.
Historical satellite element sets¶

To repeat the warning in the previous section: any particular satellite TLE set is only valid for a couple of weeks to either side of that TLE’s epoch.

That limitation unfortunately applies to the past as well as to the future. Just as today’s TLE for a satellite can only help you predict its position for a few weeks into the future, it will also be accurate for only a few weeks into the past. Whether the satellite has been performing active maneuvers, or merely coasting amidst the unpredictable magnetic fields and atmospheric drag of the near-Earth environment, a current TLE cannot predict the satellite’s position on a date in the distant past.

If you lack access to an archive of old TLE files, try searching the Internet Archive’s “Wayback Machine”:

https://archive.org/web/

Supply the URL of the current satellite catalog you downloaded and click “Browse History” and the Archive will display a calendar indicating whether any earlier versions of that same satellite catalog are in their archive. If so, then you should be able to download them to your machine and use them when you need historic satellite positions close to the old TLE’s epoch date.
Finding when a satellite rises and sets¶

Skyfield can search between a start time and an end time for each occasion on which a satellite’s altitude exceeds a specified number of degrees above the horizon. For example, here is how to determine how many times our example satellite rises above 30° of altitude over the span of a single day:

bluffton = wgs84.latlon(+40.8939, -83.8917)
t0 = ts.utc(2014, 1, 23)
t1 = ts.utc(2014, 1, 24)
t, events = satellite.find_events(bluffton, t0, t1, altitude_degrees=30.0)
event_names = 'rise above 30°', 'culminate', 'set below 30°'
for ti, event in zip(t, events):
    name = event_names[event]
    print(ti.utc_strftime('%Y %b %d %H:%M:%S'), name)

2014 Jan 23 06:25:37 rise above 30°
2014 Jan 23 06:26:58 culminate
2014 Jan 23 06:28:19 set below 30°
2014 Jan 23 12:54:56 rise above 30°
2014 Jan 23 12:56:27 culminate
2014 Jan 23 12:57:58 set below 30°

The satellite’s altitude exceeded 30° twice. For each such occasion, the method find_events() has determined not only the moment of greatest altitude — accurate to within a second or so — but also the time at which the satellite first crested 30° and the moment at which it dipped below it.

Beware that events might not always be in the order rise-culminate-set. Some satellites culminate several times between rising and setting.

By combining these results with the result of the is_sunlit() method (as described below in Find when a satellite is in sunlight), you can determine whether the satellite is in sunlight during these passes, or is eclipsed within the Earth’s shadow.

eph = load('de421.bsp')
sunlit = satellite.at(t).is_sunlit(eph)

for ti, event, sunlit_flag in zip(t, events, sunlit):
    name = event_names[event]
    state = ('in shadow', 'in sunlight')[sunlit_flag]
    print('{:22} {:15} {}'.format(
        ti.utc_strftime('%Y %b %d %H:%M:%S'), name, state,
    ))

2014 Jan 23 06:25:37   rise above 30°  in shadow
2014 Jan 23 06:26:58   culminate       in shadow
2014 Jan 23 06:28:19   set below 30°   in shadow
2014 Jan 23 12:54:56   rise above 30°  in sunlight
2014 Jan 23 12:56:27   culminate       in sunlight
2014 Jan 23 12:57:58   set below 30°   in sunlight

Finally, you will probably want to check the altitude of the Sun, so that you can ignore passes that happen during the daytime — unless you have some means of observing the satellite (by radio, for example) before it gets dark outside.
Generating a satellite position¶

Once Skyfield has identified the times at which a particular satellite is overhead, you will probably want to learn more about its position at those times.

The simplest form in which you can generate a satellite position is to call its at() method, which will return an (x,y,z) position relative to the Earth’s center in the Geocentric Celestial Reference System. (GCRS coordinates are based on even more precise axes than those of the old J2000 system.)

# You can instead use ts.now() for the current time
t = ts.utc(2014, 1, 23, 11, 18, 7)

geocentric = satellite.at(t)
print(geocentric.position.km)

[-3918.87650458 -1887.64838745  5209.08801512]

Satellite longitude, latitude, and height¶

Once you have computed a geocentric satellite position, you can use either of several wgs84 object methods to learn the satellite’s latitude, longitude, and height:

    latlon_of()
    height_of()
    geographic_position_of()

For example:

lat, lon = wgs84.latlon_of(geocentric)
print('Latitude:', lat)
print('Longitude:', lon)

Latitude: 50deg 14' 37.4"
Longitude: -86deg 23' 23.3"

Another wgs84 method computes the subpoint directly below the satellite — the point on the Earth with the same latitude and longitude as the satellite, but with a height above the WGS84 ellipsoid of zero:

    subpoint_of()

If you want the actual position of the ground beneath the satellite, you of course can’t assume that the position will be exactly at sea level. You’ll need to find a geographic library that lets you load a digital elevation model (DEM), then build a subpoint manually using the elevation returned for the satellite’s latitude and longitude.

elevation_m = 123.0
subpoint = wgs84.latlon(lat.degrees, lon.degrees, elevation_m)

Satellite altitude, azimuth, and distance¶

You might be most interested in whether the satellite is above or below the horizon from your own position as an observer, and in which direction to look for it. If you build an object to represent your latitude and longitude (as we did when we created the bluffton object above), you can use vector subtraction to ask “where will the satellite be relative to my location?”

difference = satellite - bluffton

Every time you call this vector sum’s at() method, it will compute the satellite’s position, then your own position, then subtract them. The result will be the position of the satellite relative to you as an observer. If you are interested you can access this relative position as plain (x,y,z) coordinates:

topocentric = difference.at(t)
print(topocentric.position.km)

[ 331.61901192  392.18492744 1049.7597825 ]

But the most popular approach is to ask the topocentric position for its altitude and azimuth. The altitude angle runs from 0° at the horizon to 90° directly overhead at the zenith. A negative altitude means the satellite is that many degrees below the horizon.

alt, az, distance = topocentric.altaz()

if alt.degrees > 0:
    print('The ISS is above the horizon')

print('Altitude:', alt)
print('Azimuth:', az)
print('Distance: {:.1f} km'.format(distance.km))

The ISS is above the horizon
Altitude: 16deg 16' 32.6"
Azimuth: 350deg 15' 20.4"
Distance: 1168.7 km

The azimuth is measured clockwise around the horizon, just like the degrees shown on a compass, from geographic north (0°) through east (90°), south (180°), and west (270°) before returning to the north and rolling over from 359° back to 0°.
Satellite right ascension and declination¶

If you are interested in where among the stars the satellite will be positioned, then — as with any other Skyfield position object — you can ask for its right ascension and declination, either relative to the fixed axes of the ICRF or else in the dynamical coordinate system of the date you specify.

ra, dec, distance = topocentric.radec()  # ICRF ("J2000")

print(ra)
print(dec)

03h 19m 07.97s
+63deg 55' 47.2"

ra, dec, distance = topocentric.radec(epoch='date')

print(ra)
print(dec)

03h 20m 22.42s
+63deg 58' 45.2"

See Positions to learn more about these possibilities.
Find a satellite’s range rate¶

If you’re interested in the Doppler shift of the radio signal from a satellite, you’ll want to know the rate at which the satellite’s range to your antenna is changing. To determine the rate, use the position method frame_latlon_and_rates() whose third return value will be the range and whose sixth return value will be the range’s rate of change.

Our example satellite culminates at around 20° above the horizon just after 11:20pm UTC. As expected, its range reaches a minimum during that minute and its range rate swaps from negative (drawing closer) to positive (moving away).

t = ts.utc(2014, 1, 23, 11, range(17, 23))
pos = (satellite - bluffton).at(t)
_, _, the_range, _, _, range_rate = pos.frame_latlon_and_rates(bluffton)

from numpy import array2string
print(array2string(the_range.km, precision=1), 'km')
print(array2string(range_rate.km_per_s, precision=2), 'km/s')

[1434.2 1190.5 1064.3 1097.3 1277.4 1553.6] km
[-4.74 -3.24 -0.84  1.9   3.95  5.14] km/s

I’ve chosen here to ask for coordinates in the observer’s alt-az frame of reference, but in fact the choice of coordinate system doesn’t matter if we’re going to ignore everything but the range and range rate: those two quantities should be independent of the orientation of the spherical coordinate system we choose.
Find when a satellite is in sunlight¶

A satellite is generally only visible to a ground observer when there is still sunlight up at its altitude. The satellite will visually disappear when it enters the Earth’s shadow and reappear when it emerges back into the sunlight. If you are planning to observe a satellite visually, rather than with radar or radio, you will want to know which satellite passes are in sunlight. Knowing a satellite’s sunlit periods is also helpful when modeling satellite power and thermal cycles as it goes in and out of eclipse.

Skyfield provides a simple geometric estimate for this through the is_sunlit() method. Given an ephemeris with which it can compute the Sun’s position, it will return True when the satellite is in sunlight and False otherwise.

eph = load('de421.bsp')
satellite = by_name['ISS (ZARYA)']

two_hours = ts.utc(2014, 1, 20, 0, range(0, 120, 20))
sunlit = satellite.at(two_hours).is_sunlit(eph)
print(sunlit)

[ True  True False False  True  True]

As usual, you can use Python’s zip() builtin if you want to loop across the times and corresponding values.

for ti, sunlit_i in zip(two_hours, sunlit):
    print('{}  {} is in {}'.format(
        ti.utc_strftime('%Y-%m-%d %H:%M'),
        satellite.name,
        'sunlight' if sunlit_i else 'shadow',
    ))

2014-01-20 00:00  ISS (ZARYA) is in sunlight
2014-01-20 00:20  ISS (ZARYA) is in sunlight
2014-01-20 00:40  ISS (ZARYA) is in shadow
2014-01-20 01:00  ISS (ZARYA) is in shadow
2014-01-20 01:20  ISS (ZARYA) is in sunlight
2014-01-20 01:40  ISS (ZARYA) is in sunlight

Find whether the Earth blocks a satellite’s view¶

The Earth looms large in the sky of an Earth-orbiting satellite. To plan an observation you may want to know when a given celestial object is blocked by the Earth and not visible from your satellite. Skyfield provides a simple geometric estimate for this through the is_behind_earth() method.

eph = load('de421.bsp')
earth, venus = eph['earth'], eph['venus']
satellite = by_name['ISS (ZARYA)']

two_hours = ts.utc(2014, 1, 20, 0, range(0, 120, 20))
p = (earth + satellite).at(two_hours).observe(venus).apparent()
sunlit = p.is_behind_earth()
print(sunlit)

[False False  True  True False False]

See the previous section for how to associate each of these True and False values with their corresponding time.
Avoid calling the observe method¶

When computing positions for the Sun, Moon, planets, and stars, Skyfield encourages a far more fussy approach than directly subtracting two vectors. In those cases, the user is encouraged to compute their current location with at() and then call the observe() method on the result so that Skyfield can correctly adjust the object’s position for the time it takes light to travel.

    This turns out to be expensive for Earth satellites, however, because the routines with which Skyfield computes satellite positions are not currently very fast.
    And it turns out to be useless, because satellites are too close and move far too slowly (at least compared to something like a planet) for the light travel time to make any difference.

How far off will your observations be if you simply subtract your position vector from the satellite’s vector, as encouraged above? Let’s try the alternative and measure the difference.

To use the observe() method, you need a position measured all the way from the Solar System Barycenter (SSB). To anchor both our observer location and that of the satellite to the SSB, we can use vector addition with an ephemeris that predicts the Solar System position of the Earth:

# OVERLY EXPENSIVE APPROACH - Compute both the satellite
# and observer positions relative to the Solar System
# barycenter ("ssb"), then call observe() to compensate
# for light-travel time.

t = ts.utc(2014, 1, 23, 11, 18, 7)
de421 = load('de421.bsp')
earth = de421['earth']
ssb_bluffton = earth + bluffton
ssb_satellite = earth + satellite
topocentric2 = ssb_bluffton.at(t).observe(ssb_satellite).apparent()

What difference has all of that work made? We can subtract the resulting positions to find out the distance between them:

# After all that work, how big is the difference, really?

difference_km = (topocentric2 - topocentric).distance().km
print('Difference between the two positions:')
print('{0:.3f} km'.format(difference_km))

difference_angle = topocentric2.separation_from(topocentric)
print('Angle between the two positions in the sky:')
print('{}'.format(difference_angle))

Difference between the two positions:
0.087 km
Angle between the two positions in the sky:
00deg 00' 04.6"

And there you have it!

While satellite positions are only accurate to about a kilometer anyway, accounting for light travel time only affected the position in this case by less than an additional tenth of a kilometer. This difference is not meaningful when compared to the uncertainty that is inherent in satellite positions to begin with, so you should neglect it and simply subtract GCRS-centered vectors instead as detailed above.
Detecting Propagation Errors¶

After building a satellite object, you can examine the epoch date and time when the TLE element set’s predictions are most accurate. The epoch attribute is a Time, so it supports all of the standard Skyfield date methods:

from skyfield.api import EarthSatellite

text = """
GOCE
1 34602U 09013A   13314.96046236  .14220718  20669-5  50412-4 0   930
2 34602 096.5717 344.5256 0009826 296.2811 064.0942 16.58673376272979
"""
lines = text.strip().splitlines()

sat = EarthSatellite(lines[1], lines[2], lines[0])
print(sat.epoch.utc_jpl())

A.D. 2013-Nov-10 23:03:03.9479 UTC

Skyfield is willing to generate positions for dates quite far from a satellite’s epoch, even if they are not likely to be meaningful. But it cannot generate a position beyond the point where the elements stop making physical sense. At that point, the satellite will return a position and velocity (nan, nan, nan) where all of the quantities are the special floating-point value nan which means not-a-number.

When a propagation error occurs and you get nan values, you can examine the message attribute of the returned position to learn the error that the SGP4 propagator encountered.

We can take as an example the satellite elements above. They are the last elements ever issued for GOCE, just before the satellite re-entered the atmosphere after an extended and successful mission. Because of the steep decay of its orbit, the elements are valid over an unusually short period — from just before noon on Saturday to just past noon on Tuesday:
_images/goce-reentry.png

By asking for GOCE’s position just before or after this window, we can learn about the propagation errors that are limiting this TLE set’s predictions:

geocentric = sat.at(ts.utc(2013, 11, 9))
print('Before:')
print(geocentric.position.km)
print(geocentric.message)

geocentric = sat.at(ts.utc(2013, 11, 13))
print('\nAfter:')
print(geocentric.position.km)
print(geocentric.message)

Before:
[nan nan nan]
mean eccentricity is outside the range 0.0 to 1.0

After:
[-5021.82658191   742.71506112  3831.57403957]
mrt is less than 1.0 which indicates the satellite has decayed

If you use a Time array to ask about an entire range of dates, then message will be a sequence filled in with None whenever the SGP4 propagator was successful and otherwise recording the propagator error:

from pprint import pprint

geocentric = sat.at(ts.utc(2013, 11, [9, 10, 11, 12, 13]))
pprint(geocentric.message)

['mean eccentricity is outside the range 0.0 to 1.0',
 None,
 None,
 None,
 'mrt is less than 1.0 which indicates the satellite has decayed']

Build a satellite with a specific gravity model¶

If your satellite elements are designed for another gravity model besides the default WGS72 model, then use the underlying sgp4 module to build the satellite. It will let you customize the choice of gravity model:

from sgp4.api import Satrec, WGS84
satrec = Satrec.twoline2rv(line1, line2, WGS84)
sat = EarthSatellite.from_satrec(satrec, ts)

Build a satellite from orbital elements¶

If you are starting with raw satellite orbital parameters instead of TLE text, you will want to interact directly with the sgp4 library that Skyfield uses for its low-level satellite calculations.

The underlying library provides access to a low-level constructor that builds a satellite model directly from numeric orbital parameters:

from sgp4.api import Satrec, WGS72

satrec = Satrec()
satrec.sgp4init(
    WGS72,           # gravity model
    'i',             # 'a' = old AFSPC mode, 'i' = improved mode
    5,               # satnum: Satellite number
    18441.785,       # epoch: days since 1949 December 31 00:00 UT
    2.8098e-05,      # bstar: drag coefficient (/earth radii)
    6.969196665e-13, # ndot: ballistic coefficient (radians/minute^2)
    0.0,             # nddot: second derivative of mean motion (radians/minute^3)
    0.1859667,       # ecco: eccentricity
    5.7904160274885, # argpo: argument of perigee (radians)
    0.5980929187319, # inclo: inclination (radians)
    0.3373093125574, # mo: mean anomaly (radians)
    0.0472294454407, # no_kozai: mean motion (radians/minute)
    6.0863854713832, # nodeo: right ascension of ascending node (radians)
)

If you need any more details, this sgp4init method is documented in the Providing your own elements section of the sgp4 library’s documentation on the Python Packaging Index.

To wrap this low-level satellite model in a Skyfield object, call this special constructor:

sat = EarthSatellite.from_satrec(satrec, ts)
print('Satellite number:', sat.model.satnum)
print('Epoch:', sat.epoch.utc_jpl())

Satellite number: 5
Epoch: A.D. 2000-Jun-27 18:50:24.0000 UTC

The result should be a satellite object that behaves exactly as though it had been loaded from TLE lines.

'''

import datetime
import os

from skyfield.api import EarthSatellite, load
from skyfield.toposlib import Geoid


class Satellite(EarthSatellite): # Inherit from EarthSatellite
    """Custom Satellite class to extend the Skyfield EarthSatellite class with metadata.
    """
    def __init__(self, catalog_id, line1, line2, name="Unnamed Satellite", metadata=None):
        print("Satellite object created for: " + name, "Catalog ID: " + catalog_id)
        super().__init__(line1, line2, name)
        self.catalog_id = catalog_id
        self.metadata = metadata if metadata is not None else {}

    def epoch_valid_at(self, time: datetime.datetime, margin: int = 14):
        """Check if the Satellite's epoch is valid at a given time, default margin for validity is 2 weeks before and after the epoch.

        Args:
            time (_type_): The time to check the epoch validity for.
            margin (int, optional): The number of days before and after the epoch to consider valid. Defaults to 14 (2 weeks).

        Returns:
            _Bool_: True if the time is within the margin of the epoch, False otherwise.
        """
        epoch = self.epoch.utc_datetime() # convert epoch to datetime in utc

        time = time.astimezone(datetime.timezone.utc) # convert time to utc

        # if time is before epoch margin
        if time < epoch - datetime.timedelta(days=margin):
            return False
        # if time is after epoch margin
        if time > epoch + datetime.timedelta(days=margin):
            return False
        return True


    def at(self, time):
        return super().at(time)

    def add_metadata(self, key, value):
        """Add metadata to the Satellite object.

        Args:
            key (str): The key to store the metadata under.
            value (_type_): The value to store in the metadata.
        """
        self.metadata[key] = value

    def latlon_at(self, time):
        """Convenient method to get the latitude, longitude, and elevation of the Satellite at a given time.

        Args:
            time (_type_): The time to calculate the position for.

        Returns:
            tuple: Latitude, Longitude, Elevation in degrees, degrees, km.
        """


        subpoint = self.at(time).subpoint()
        lat = subpoint.latitude.degrees
        lon = subpoint.longitude.degrees
        elevation = subpoint.elevation.km
        return lat, lon, elevation

    def get_metadata(self, key):
        """Get metadata from the Satellite object.

        Args:
            key (str): The key to get the metadata for.

        Returns:
            _type_: The metadata value.
        """
        return self.metadata.get(key, "Metadata not found")


class Earth():
    """Earth class for calculating lat/lon from geocentric coordinates, based off of standard wgs84 Earth parameters.
    """
    def __init__(self, controller):
        self.controller = controller
        super().__init__()
        self.geoid = Geoid('WGS84', 6378137.0, 298.257223563) # WGS84 Geoid

    def latlon_to_xyz(self, lat, lon, elevation):
        """Calculate the latitude and longitude of a point on the Earth's surface from geocentric coordinates.

        Args:
            lat (float): Latitude in radians.
            lon (float): Longitude in radians.
            elevation (float): Elevation in meters.

        Returns:
            tuple: Latitude and Longitude in degrees.
        """
        return self.geoid.latlon(lat, lon, elevation)



class TLEManager:
    """Manages TLE orbital data; Reading from file, validating Epoch, requesting new data from Celestrak, and building Satellite objects.
    """
    def __init__(self, controller, tle_data_dir: str = "src/data/tle_data"):
        super().__init__()
        self.controller = controller
        self.tle_data_dir = tle_data_dir
        if not os.path.exists(self.tle_data_dir):
            os.makedirs(self.tle_data_dir)

    def find_tle_file(self, catalog_id: str):
        """Find the TLE file for the given Catalog ID in the TLE data directory.

        Args:
            catalog_id (str): The Catalog ID of the satellite. Max length 24 characters.

        Raises:
            FileNotFoundError: If the TLE file is not found, raise an error.

        Returns:
            str: The path to the TLE file.
        """
        for filename in os.listdir(self.tle_data_dir):
            if catalog_id in filename:
                return os.path.join(self.tle_data_dir, filename)
        print("TLE file not found for catalog_id: " + catalog_id)
        return None

    def tle_exists(self, catalog_id: str):
        """Check if a TLE file exists for the given Catalog ID.

        Args:
            catalog_id (str): The Catalog ID of the satellite. Max length 24 characters.

        Returns:
            _Bool_: True if the TLE file exists, False otherwise.
        """
        path = self.find_tle_file(catalog_id)
        if path is not None:
            if os.path.exists(path):
                return True
            else:
                return False
        else:
            return False

    def read_tle(self, catalog_id: str):
        """Read TLE data from a file for the given Catalog ID.

        Args:
            catalog_id (str): The Catalog ID of the satellite. Max length 24 characters.

        Returns:
            list[str]: A list of TLE lines.
        """
        path = self.find_tle_file(catalog_id)
        if self.tle_exists(catalog_id):
            with open(path, 'r') as file:
                lines = file.readlines()
                return lines
        else:
            return None

    def download_tle(self, catalog_id: str):
        """Download a TLE file for the given Catalog ID from Celestrak and save it to the TLE data directory.

        Args:
            catalog_id (str): The Catalog ID of the satellite. Max length 24 characters.

        Raises:
            FileNotFoundError: If the TLE file is not found after downloading, raise an error.

        Returns:
            None
        """

        if not catalog_id:
            return None
        url = "https://celestrak.org/NORAD/elements/gp.php?CATNR=" + catalog_id + "&FORMAT=TLE"
        load.tle_file(url, reload=True, filename=os.path.join("src/data/tle_data", catalog_id + ".tle"))

        if not self.tle_exists(catalog_id):
            raise FileNotFoundError("Attempted to download TLE file for catalog_id: " + catalog_id + " but resulting file was not found.")

    def getSatellite(self, catalog_id: str):
        """Get a Satellite object for the given Catalog ID.

        Args:
            catalog_id (str): The Catalog ID of the satellite. Max length 24 characters.

        Raises:
            ValueError: If the catalog_id is invalid, raise an error.

        Returns:
            Satellite: A custom Satellite object.
        """
        if not catalog_id:
            raise ValueError("Invalid catalog_id")

        tle_data = self.read_tle(catalog_id)
        if not tle_data:
            self.download_tle(catalog_id)
            tle_data = self.read_tle(catalog_id)

        satellite = Satellite(catalog_id, tle_data[1], tle_data[2], name=tle_data[0].strip())
        if satellite:
            if not satellite.epoch_valid_at(datetime.datetime.now(), margin=14):
                print("Epoch not valid for catalog_id: " + catalog_id, "with margin: " + str(14))
                self.download_tle(catalog_id)
                tle_data = self.read_tle(catalog_id)
                satellite = Satellite(catalog_id, tle_data[1], tle_data[2], name=tle_data[0].strip())
            return satellite

class Observer():
    """Observer class for calculating satellite visibility from a given location.
    """
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
