import requests
from PyQt6 import QtCore
from PyQt6.QtCore import QDate, QTime
from PyQt6.QtWidgets import (
    QDateEdit,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

import config


class InfoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        infoLabel = QLabel("Info")
        layout.addWidget(infoLabel)

        self.infoText = QTextEdit()
        self.infoText.setReadOnly(True)
        self.infoText.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        layout.addWidget(self.infoText)
        self.setText(
            "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna a."
        )

    def setText(self, info):
        self.infoText.setText(info)

    def clearText(self):
        self.infoText.clear()


class LocationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.apiKey = config.geocodeAPIKey
        self.lat = -84.56537605292901  # Example: 84.5826111111111 for Kennesaw, GA
        self.lon = 34.023438520758205  # Example: 34.039794444444446 for Kennesaw, GA
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        group = QGroupBox("Location")
        layout.addWidget(group)

        groupLayout = QVBoxLayout(group)

        addressLayout = QHBoxLayout()
        addressLabel = QLabel("Address:")
        addressLayout.addWidget(addressLabel)
        self.addressInput = QLineEdit()
        addressLayout.addWidget(self.addressInput)
        groupLayout.addLayout(addressLayout)

        lonLayout = QHBoxLayout()
        lonLabel = QLabel("Lon:")
        lonLayout.addWidget(lonLabel)
        self.lonInput = QLineEdit()
        lonLayout.addWidget(self.lonInput)
        groupLayout.addLayout(lonLayout)

        latLayout = QHBoxLayout()
        latLabel = QLabel("Lat:")
        latLayout.addWidget(latLabel)
        self.latInput = QLineEdit()
        latLayout.addWidget(self.latInput)
        groupLayout.addLayout(latLayout)

        self.setLocationButton = QPushButton("Set Location")
        groupLayout.addWidget(self.setLocationButton)
        self.setLocationButton.clicked.connect(self.setLocation)

        self.addressInput.setText("Kennesaw State University")
        self.setLocation()

    def getLocation(self):
        return self.lonInput.text(), self.latInput.text()

    def setLocation(self):
        if self.addressInput.text() != "":
            location = self.getWebLocation(self.addressInput.text())
            if location is not None:
                self.lat, self.lon = location
        else:
            self.lon = self.lonInput.text()
            self.lat = self.latInput.text()

        self.lonInput.setText(str(self.lon))
        self.latInput.setText(str(self.lat))

    def clearLocation(self):
        self.lonInput.clear()
        self.latInput.clear()
        self.addressInput.clear()

    def getWebLocation(self, address):
        try:
            response = requests.get(
                f"https://geocode.maps.co/search?q={address}&key={self.apiKey}"
            )
            response.raise_for_status()  # Check for HTTP errors
            data = response.json()
            for item in data:
                lat = item.get("lat", None)
                lon = item.get("lon", None)
                if lat is not None and lon is not None:
                    self.lat = lat
                    self.lon = lon
            return self.lon, self.lat
        except requests.exceptions.RequestException as e:
            print(f"Error occurred during web request: {e}")
            return None
        except ValueError as e:
            print(f"Error occurred while parsing JSON response: {e}")
            return None


class TimeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        group = QGroupBox("Time")
        layout.addWidget(group)

        groupLayout = QHBoxLayout(group)

        self.date = QDateEdit()
        groupLayout.addWidget(self.date)

        self.time = QTimeEdit()
        groupLayout.addWidget(self.time)

        self.setTimeButton = QPushButton("Set Time")
        groupLayout.addWidget(self.setTimeButton)

        # default to the current date and time
        self.setTime(QDate.currentDate(), QTime.currentTime())

    def getTime(self):
        return self.date.date(), self.time.time()

    def setTime(self, date, time):
        self.date.setDate(date)
        self.time.setTime(time)

    def clearTime(self):
        self.date.clear()
        self.time.clear()


class StatusButtonWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        statusLabel = QLabel("Status")
        layout.addWidget(statusLabel)

        self.statusButton = QPushButton("Start")
        layout.addWidget(self.statusButton)

    def setStatus(self, status):
        self.statusButton.setText(status)

    def getStatus(self):
        return self.statusButton.text()

    def clearStatus(self):
        self.statusButton.clear()


class TrackingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # displays a 3d globe
        self.globe = QLabel()
        layout.addWidget(self.globe)

        """main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_widget.setStyleSheet("font-family: 'Courier New';")

        title = QLabel("Select a category of satellite to query:")
        title.setAlignment(Qt.AlignmentFlag.AlignTop)
        title.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)

        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Sidebar setup
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        toolbar_title = QLabel("Satellite Tracker")
        toolbar_title.setStyleSheet(
            "font-weight: bold; font-size: 16px; margin-bottom: 10px;"
        )
        sidebar_layout.addWidget(toolbar_title)

        location_label = QLabel("Query from:")
        sidebar_layout.addWidget(location_label)

        lon_layout = QHBoxLayout()
        lon_label = QLabel("Longitude:")
        self.lon_input = QLineEdit()
        self.lon_input.setPlaceholderText("Longitude")
        lon_layout.addWidget(lon_label)
        lon_layout.addWidget(self.lon_input)
        sidebar_layout.addLayout(lon_layout)

        sidebar_layout.addStretch()  # flex spacer to push button to bottom

        self.confirm_section_title = QLabel("Tracking: none")
        self.confirm_section_title.setWordWrap(True)
        self.confirm_section_title.setStyleSheet(
            "font-weight: bold; font-size: 14px; margin-top: 20px;"
        )
        sidebar_layout.addWidget(self.confirm_section_title)

        confirm_button = QPushButton("Submit")
        confirm_button.setStyleSheet("padding: 10px; font-size: 14px;")
        sidebar_layout.addWidget(confirm_button)
        # confirm_button.clicked.connect()

        sidebar.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
        )

        main_layout = QHBoxLayout(main_widget)
        # page_layout = QVBoxLayout(main_layout)
        # main_layout.addWidget(title)
        main_layout.addWidget(self.main_splitter)
        main_layout.addWidget(sidebar)

        """


class DoubleListMenuWidget(QWidget):
    """
    This class represents a widget that displays two lists side by side. The interaction model is such that selecting an item in the left list updates the right list with corresponding items.

    Must be initialized with a dictionary of list items. The data model for this widget is a dictionary where:
    - The keys represent items in the left list.
    - The values are items, dictionaries with the following keys:
        - "name": the name of the item
        - "query": the query to be executed when the item is selected
    """

    def __init__(self, parent=None, item_dict: dict[str, list[dict[str, str]]] = {}):
        super().__init__(parent)
        self.item_dict = item_dict
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout(self)

        self.leftList = QListWidget()
        self.leftList.addItems(self.item_dict.keys())
        self.leftList.itemClicked.connect(self.updateRightList)
        layout.addWidget(self.leftList)

        self.rightList = QListWidget()
        self.rightList.itemClicked.connect(self.onRightListItemClicked)
        layout.addWidget(self.rightList)

    def updateRightList(self, selectedLeftListItem: QListWidgetItem):
        leftItemKey = selectedLeftListItem.text()
        self.rightList.clear()
        rightItems = self.item_dict[leftItemKey]

        for item in rightItems:
            QListWidgetItem(item["name"], self.rightList)

    def onRightListItemClicked(self, item):
        print(f"Tracking: {item.text()}")
