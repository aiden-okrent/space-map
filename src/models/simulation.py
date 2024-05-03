import datetime
import threading
from enum import Enum, auto
from time import sleep
from typing import Any, Dict, List, Tuple, Union

import keyboard
from dateutil import tz
from matplotlib.pylab import f
from skyfield.api import load
from skyfield.timelib import Time, Timescale


class SimulationStatus(Enum):
    STOPPED = auto()
    RUNNING = auto()
    PAUSED = auto()
    ERROR = auto()

    def __str__(self) -> str:
        return super().__str__().capitalize()


class Simulation():
    def __init__(self, controller, epoch: datetime.datetime = None, speed: float = 1.0) -> None:
        super().__init__()
        self.status = SimulationStatus.STOPPED

        self.epoch = epoch or datetime.datetime.now(tz=tz.tzutc())  # current time in the simulation (UTC)
        self.speed = speed  # multiplier for the speed of the simulation

        self.maxSpeed = 99.0  # max speed

        self.ts = load.timescale()  # used for 'Time' objects
        self.lock = threading.Lock()
        self.thread = threading.Thread

    def start(self) -> None:
        with self.lock:
            self._setStatus(SimulationStatus.RUNNING)

    def stop(self) -> None:
        with self.lock:
            self._setStatus(SimulationStatus.STOPPED)

    def pause(self) -> None:
        with self.lock:
            self._setStatus(SimulationStatus.PAUSED)

    def resume(self) -> None:
        with self.lock:
            self._setStatus(SimulationStatus.RUNNING)

    def setSpeed(self, speed: float) -> None:
        with self.lock:
            if speed >= 0:
                self.speed = min(speed, self.maxSpeed)
            else:
                self.speed = max(speed, -self.maxSpeed)

    def loadEpoch(self, epoch: datetime.datetime) -> None:
        with self.lock:
            self.epoch = epoch

    def now(self) -> datetime.datetime:
        """Get the current time in the simulation as a datetime object."""
        return self.epoch

    def _run(self) -> None:
        try:
            while self.status != SimulationStatus.STOPPED:
                if self.status == SimulationStatus.RUNNING:
                    time_increment = datetime.timedelta(seconds=(1 if self.speed >= 0 else -1))
                    self.epoch += time_increment * abs(self.speed)
                    sleep(1 / abs(self.speed))
                    print(f"Running sim at {self.speed:.2f}x, Current Time={self._strftime()}  ", end="\r", flush=True)
                elif self.status == SimulationStatus.PAUSED:
                    sleep(1 / abs(self.speed) if self.speed != 0 else 1)
                    print(f"Running sim Paused at Current Time={self._strftime()}", end="\r", flush=True)
        except Exception as e:
            self._setStatus(SimulationStatus.ERROR)
            print(f"Error: {e}")

    def _setStatus(self, newStatus: SimulationStatus) -> None:  # state machine for simulation
        if self.status == newStatus:
            return
        if self.status == SimulationStatus.ERROR:
            raise RuntimeError("Simulation is in an error state, all operations are halted and must be reset.")

        if newStatus == SimulationStatus.RUNNING:
            if self.status == SimulationStatus.STOPPED:
                self.status = SimulationStatus.RUNNING
                self.thread = threading.Thread(target=self._run, daemon=True)
                self.thread.start()
                print(f"\nSimulation started at {self._strftime()}")
            elif self.status == SimulationStatus.PAUSED:
                self.status = SimulationStatus.RUNNING

        elif newStatus == SimulationStatus.STOPPED:
            if self.status == SimulationStatus.RUNNING or self.status == SimulationStatus.PAUSED:
                self.status = SimulationStatus.STOPPED
                if self.thread.is_alive():
                    self.thread.join()
                print(f"\nSimulation stopped at {self._strftime()}")

        elif newStatus == SimulationStatus.PAUSED:
            if self.status == SimulationStatus.RUNNING:
                self.status = SimulationStatus.PAUSED

    def _strftime(self) -> str:
        format = "%Y-%m-%d %I:%M:%S %p %Z"
        return self.epoch.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal()).strftime(format)