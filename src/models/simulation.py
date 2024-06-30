import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Union

from dateutil import tz
from PySide6.QtCore import QObject, QTimer, Signal, Slot
from skyfield.api import load
from skyfield.timelib import Time, Timescale
from PySide6.QtCore import Signal
from src.utilities.singleton import Singleton

if TYPE_CHECKING:
    from src.controllers.controller import ApplicationController


class SimulationStatus(Enum):
    STOPPED = auto()
    RUNNING = auto()

    def __str__(self) -> str:
        return super().__str__().capitalize()


class Simulation(QObject):
    epochChanged: Signal = Signal(datetime.datetime)
    epochReset: Signal = Signal(datetime.datetime)
    speedChanged: Signal = Signal(float)

    Controller: "ApplicationController"

    def __init__(self, Controller: "ApplicationController"):
        super().__init__()

        print("Initializing Simulation")

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

    def resume(self) -> None:
        if not self.timer.isActive():
            self._setStatus(SimulationStatus.RUNNING)

    def setSpeed(self, speed: float) -> None:
        self.speed = min(max(speed, -self.maxSpeed), self.maxSpeed)
        if self.status == SimulationStatus.RUNNING:
            self.timer.setInterval(
                100 / abs(self.speed) if self.speed != 0 else self.speed
            )
        self.speedChanged.emit(self.speed)

    def loadEpoch(self, epoch: datetime.datetime) -> None:
        self.epoch = epoch.replace(tzinfo=tz.tzutc())

    def resetEpoch(self) -> None:
        self.epoch = datetime.datetime.now(tz=tz.tzutc())
        self.epochReset.emit(self.epoch)

    def now_Time(self) -> Time:
        return self.ts.utc(self.epoch.replace(tzinfo=tz.tzutc()))

    def now_datetime(self) -> datetime.datetime:
        return self.epoch

    def now_localtime(self) -> datetime.datetime:
        return self.epoch.replace(tzinfo=tz.tzlocal())

    @Slot()
    def _run(self) -> None:
        time_increment = datetime.timedelta(
            milliseconds=(100 if self.speed >= 0 else -1)
        )
        self.epoch += time_increment * abs(self.speed)
        self.epochChanged.emit(self.epoch)

    def _setStatus(self, newStatus: SimulationStatus) -> None:
        if self.status != newStatus:
            if (
                newStatus == SimulationStatus.RUNNING
                and self.status == SimulationStatus.STOPPED
            ):
                self.timer.start(100 / abs(self.speed))
            self.status = newStatus
