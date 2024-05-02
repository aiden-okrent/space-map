#
import datetime as dt_module
from collections import OrderedDict, namedtuple
from datetime import date, datetime, time, timedelta, timezone, tzinfo
from time import strftime, struct_time
from typing import Any, Dict, List, Tuple, Union, override

from dateutil import tz
from numpy import array, concatenate, linspace, ndarray, nonzero, searchsorted
from skyfield.api import load
from skyfield.timelib import Time, Timescale


class SimTime(Timescale):
    """
    SimTime class provides methods for time-related operations used universally throughout the simulation to calculate orbits, positions, and other time-dependent functions.

    There are two modes of operation:
        A. Live time mode: The epoch dynamically updates to match the system time.
        B. Simulated time mode: The epoch is used as a reference point for manipulating the simulation time.

    In simulated time mode, methods are available to manipulate the simulation time, while in live time mode, time is immutable.

    The SimTime class can be instantiated with a specific reference epoch for simulated time or it can default to live time mode.
    """
    def __init__(self, epoch: Union[None, datetime] = None, tz: str = "UTC") -> None:
        """Initialize the Time class with a reference epoch for simulated time mode, or default to live time mode.

        Args:
            epoch (Union[None, datetime], optional): Reference epoch for simulated time mode. Defaults to None.
            tz (str, optional): Timezone to use for the time. Defaults to "UTC".
        """
        super().__init__()
        self.epoch = epoch
        self.tz = tz
        self.ts = load.timescale()
        self.live = True if epoch is None else False

    @override
    def now(self) -> Time:
        """Get the current time in the simulation.
        If in live mode, the system time is used. If in simulated mode, the current time is calculated based on the simulation.

        Returns:
            Time: Current time in the simulation.
        """
        return self.ts.now()