import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Union

from dateutil import tz
from matplotlib.pylab import f
from PySide6.QtCore import QObject, QTimer, Signal, Slot
from skyfield.api import load
from skyfield.timelib import Time, Timescale

from src.utilities.singleton import Singleton

if TYPE_CHECKING:
    from src.controllers.controller import ApplicationController
    from src.models.earth import Earth

from PySide6.QtCore import Signal


class SimulationStatus(Enum):
    STOPPED = auto()
    RUNNING = auto()
    PAUSED = auto()
    ERROR = auto()

    def __str__(self) -> str:
        return super().__str__().capitalize()

class Simulation(QObject):
    epochChanged: Signal = Signal(datetime.datetime)

    Controller: 'ApplicationController'
    Earth: 'Earth'

    def __init__(self, Controller: 'ApplicationController'):
        super().__init__()
        self.Controller = Controller
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
        self.epochChanged.emit(self.epoch)

    def now_Time(self) -> Time:
        return self.ts.utc(self.epoch.replace(tzinfo=tz.tzutc()))

    def now_datetime(self) -> datetime.datetime:
        return self.epoch

    @Slot()
    def _run(self) -> None:
        time_increment = datetime.timedelta(seconds=(1 if self.speed >= 0 else -1))
        self.epoch += time_increment * abs(self.speed)
        self.epochChanged.emit(self.epoch)

    def _setStatus(self, newStatus: SimulationStatus) -> None:
        if self.status != newStatus:
            if newStatus == SimulationStatus.RUNNING and self.status in {SimulationStatus.STOPPED, SimulationStatus.PAUSED}:
                self.timer.start(1000 / abs(self.speed))
            self.status = newStatus

    def _strftime(self) -> str:
        format = "%Y-%m-%d %I:%M:%S %p %Z"
        return self.epoch.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal()).strftime(format)
