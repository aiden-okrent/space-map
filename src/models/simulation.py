import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Tuple, Union

from dateutil import tz
from matplotlib.pylab import f
from PySide6.QtCore import QTimer, Slot
from skyfield.api import load
from skyfield.timelib import Time, Timescale


class SimulationStatus(Enum):
    STOPPED = auto()
    RUNNING = auto()
    PAUSED = auto()
    ERROR = auto()

    def __str__(self) -> str:
        return super().__str__().capitalize()

class SimulationSingleton(type):
    _instances: Dict[type, Any] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class Simulation(metaclass=SimulationSingleton):
    def __init__(self, controller=None) -> None:
        self.status = SimulationStatus.STOPPED
        self.epoch = datetime.datetime.now(tz=tz.tzutc())
        self.speed = 1.0
        self.maxSpeed = 99.0
        self.ts = load.timescale()
        self.timer = QTimer()
        self.timer.timeout.connect(self._run)

    def start(self) -> None:
        if not self.timer.isActive():
            self._setStatus(SimulationStatus.RUNNING)

    def stop(self) -> None:
        if self.timer.isActive():
            self.timer.stop()
            self._setStatus(SimulationStatus.STOPPED)

    def pause(self) -> None:
        if self.timer.isActive():
            self.timer.stop()
            self._setStatus(SimulationStatus.PAUSED)

    def resume(self) -> None:
        if not self.timer.isActive():
            self._setStatus(SimulationStatus.RUNNING)

    def setSpeed(self, speed: float) -> None:
        self.speed = min(max(speed, -self.maxSpeed), self.maxSpeed)
        if self.status == SimulationStatus.RUNNING:
            self.timer.setInterval(1000 / abs(self.speed) if self.speed != 0 else self.speed)

    def loadEpoch(self, epoch: datetime.datetime) -> None:
        self.epoch = epoch

    def now_Time(self) -> Time:
        return self.ts.utc(self.epoch)

    def now_datetime(self) -> datetime.datetime:
        return self.epoch

    @Slot()
    def _run(self) -> None:
        time_increment = datetime.timedelta(seconds=(1 if self.speed >= 0 else -1))
        self.epoch += time_increment * abs(self.speed)
        print(f"Running sim at {self.speed:.2f}x, Current Time={self._strftime()}  ", end="\r", flush=True)

    def _setStatus(self, newStatus: SimulationStatus) -> None:
        if self.status != newStatus:
            if newStatus == SimulationStatus.RUNNING and self.status in {SimulationStatus.STOPPED, SimulationStatus.PAUSED}:
                self.timer.start(1000 / abs(self.speed))
            self.status = newStatus

    def _strftime(self) -> str:
        format = "%Y-%m-%d %I:%M:%S %p %Z"
        return self.epoch.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal()).strftime(format)
