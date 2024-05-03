#
import datetime

from PySide6.QtCore import QDateTime, QSize, Qt
from PySide6.QtWidgets import (
    QDateTimeEdit,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QToolBar,
    QWidget,
)


class MainToolBar(QToolBar):
    def __init__(self, parent, controller):
        super().__init__('Main Toolbar', parent)
        self.parent = parent
        self.controller = controller

        self.setMovable(False)
        self.setFloatable(False)
        self.setAllowedAreas(Qt.ToolBarArea.TopToolBarArea)
        self.setOrientation(Qt.Orientation.Horizontal)

        self.addTools()

    def addTools(self):
        self.addAction('Start Sim', self.controller.startSim)
        self.addAction('Stop Sim', self.controller.stopSim)

        setSimEpochWidget = QWidget()
        setSimEpochLayout = QHBoxLayout()
        setSimEpochWidget.setLayout(setSimEpochLayout)
        setSimEpochLayout.addWidget(QLabel('Epoch:'))
        setSimEpochDatetime = QDateTimeEdit()
        setSimEpochDatetime.setDisplayFormat('MMMM d, yyyy h:mm:ss AP')
        setSimEpochDatetime.setCalendarPopup(True)
        setSimEpochDatetime.setDateTimeRange(QDateTime(1957, 10, 4, 0, 0, 0), QDateTime(2056, 10, 4, 0, 0, 0)) # TLE max epoch range
        setSimEpochDatetime.setDateTime(self.controller.getSimEpoch())
        setSimEpochDatetime.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        setSimEpochDatetime.setButtonSymbols(QDateTimeEdit.ButtonSymbols.UpDownArrows)
        setSimEpochDatetime.setStyleSheet('QDateTimeEdit { padding: 0px; }')
        setSimEpochDatetime.dateTimeChanged.connect(lambda dt: self.controller.setSimEpoch(dt.toPython()))
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
        setSimSpeedSpinBox.valueChanged.connect(self.controller.setSimSpeed)
        setSimSpeedLayout.addWidget(setSimSpeedSpinBox)
        self.addWidget(setSimSpeedWidget)

