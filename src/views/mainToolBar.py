#
import datetime
from typing import TYPE_CHECKING

from PySide6.QtCore import QDateTime, QObject, QSize, Qt, QTimer, Signal, Slot
from PySide6.QtWidgets import (
    QDateTimeEdit,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QToolBar,
    QWidget,
)

if TYPE_CHECKING:
    from src.controllers.controller import ApplicationController
    from src.models.simulation import Simulation


class MainToolBar(QToolBar):

    Controller: 'ApplicationController'
    Simulation: 'Simulation'

    def __init__(self, parent, Controller: 'ApplicationController'):
        super().__init__('Main Toolbar', parent)
        self.parent = parent
        self.Controller = Controller
        self.Simulation = Controller.Simulation

        self.setMovable(False)
        self.setFloatable(False)
        self.setAllowedAreas(Qt.ToolBarArea.TopToolBarArea)
        self.setOrientation(Qt.Orientation.Horizontal)

        self.addTools()

    def addTools(self):
        self.addAction('Start', self.Controller.startSim)
        self.addAction('Stop', self.Controller.stopSim)

        setSimEpochWidget = QWidget()
        setSimEpochLayout = QHBoxLayout()
        setSimEpochWidget.setLayout(setSimEpochLayout)
        setSimEpochLayout.addWidget(QLabel('Epoch:'))
        setSimEpochDatetime = QDateTimeEdit()
        setSimEpochDatetime.setDisplayFormat('MMMM d, yyyy h:mm:ss AP')
        setSimEpochDatetime.setCalendarPopup(True)
        setSimEpochDatetime.setDateTimeRange(QDateTime(1957, 10, 4, 0, 0, 0), QDateTime(2056, 10, 4, 0, 0, 0)) # TLE max epoch range
        setSimEpochDatetime.setDateTime(self.Controller.getSimEpoch())
        setSimEpochDatetime.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        setSimEpochDatetime.setButtonSymbols(QDateTimeEdit.ButtonSymbols.UpDownArrows)
        setSimEpochDatetime.setStyleSheet('QDateTimeEdit { padding: 0px; }')
        setSimEpochDatetime.dateTimeChanged.connect(lambda dt: self.Controller.setSimEpoch(dt.toPython()))
        setSimEpochLayout.addWidget(setSimEpochDatetime)
        self.addWidget(setSimEpochWidget)

        setSimSpeedWidget = QWidget()
        setSimSpeedLayout = QHBoxLayout()
        setSimSpeedWidget.setLayout(setSimSpeedLayout)
        setSimSpeedLayout.addWidget(QLabel('Speed:'))
        setSimSpeedSpinBox = QDoubleSpinBox()
        setSimSpeedSpinBox.setRange(-100.0, 100.0)
        setSimSpeedSpinBox.setSingleStep(0.25)
        setSimSpeedSpinBox.setValue(1.0)
        setSimSpeedSpinBox.setDecimals(2)
        setSimSpeedSpinBox.setAccelerated(True) # arrow keys will change the value
        setSimSpeedSpinBox.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        setSimSpeedSpinBox.valueChanged.connect(self.Controller.setSimSpeed)
        setSimSpeedLayout.addWidget(setSimSpeedSpinBox)
        self.addWidget(setSimSpeedWidget)

        self.addAction('Toggle Orbits', lambda: self.Controller.toggleOrbitVisibility())
        self.addAction('Toggle Hidden', lambda: self.Controller.toggleHidden())

        addSatelliteWidget = QWidget()
        addSatelliteLayout = QHBoxLayout()
        addSatelliteWidget.setLayout(addSatelliteLayout)
        addSatelliteLayout.addWidget(QLabel('Add:'))
        addSatelliteTextEdit = QLineEdit()  # Changed QTextEdit to QLineEdit
        addSatelliteTextEdit.setPlaceholderText('Enter Query')
        #addSatelliteTextEdit.setMaxLength(5)
        addSatelliteTextEdit.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        addSatelliteTextEdit.editingFinished.connect(lambda: self.Controller.searchSatellites(addSatelliteTextEdit.text(), True))
        addSatelliteLayout.addWidget(addSatelliteTextEdit)
        self.addWidget(addSatelliteWidget)

        removeSatelliteWidget = QWidget()
        removeSatelliteLayout = QHBoxLayout()
        removeSatelliteWidget.setLayout(removeSatelliteLayout)
        removeSatelliteLayout.addWidget(QLabel('Remove:'))
        removeSatelliteTextEdit = QLineEdit()
        removeSatelliteTextEdit.setPlaceholderText('Enter Query')
        removeSatelliteTextEdit.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        removeSatelliteTextEdit.editingFinished.connect(lambda: self.Controller.searchSatellites(removeSatelliteTextEdit.text(), False))
        removeSatelliteLayout.addWidget(removeSatelliteTextEdit)
        self.addWidget(removeSatelliteWidget)

        self.Simulation.epochChanged.connect(lambda dt: setSimEpochDatetime.setDateTime(dt))