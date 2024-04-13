""" import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QListWidget, QListWidgetItem, QVBoxLayout, QHBoxLayout, QRadioButton, QSplitter, QSizePolicy, QLineEdit, QLabel, QPushButton)
from PyQt6.QtCore import Qt, QDateTime
import json
import os
from windows.displayWindow import DisplayWindow
from PyQt6.QtWidgets import QDateTimeEdit
from skyfield.api import Topos, load
from datetime import datetime


class ControlWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Satellite Tracker')
        self.setGeometry(100, 100, 900, 600)
        self.main_categories = {}
        self.load_categories()
        self.initUI()

        self.DisplayWindow = DisplayWindow()
        self.DisplayWindow.show()
        self.DisplayWindow.move(self.geometry().right() + 10, self.geometry().top())


    def load_categories(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(os.path.dirname(current_dir), 'sat_query_categories.json')
        with open(json_file_path, 'r') as f:
            self.main_categories = json.load(f)

    def initUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_widget.setStyleSheet("font-family: 'Courier New';")

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        self.setupLists(splitter)

        # Sidebar setup
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Ensure content aligns to top
        splitter.addWidget(sidebar)

        toolbar_title = QLabel("Satellite Tracker")
        toolbar_title.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        sidebar_layout.addWidget(toolbar_title)

        '''self.info_textbox = QLabel("Detailed information...")
        self.info_textbox.setWordWrap(True)
        sidebar_layout.addWidget(self.info_textbox)'''

        '''self.selected_sub_category_label = QLabel("Select a category to track:")
        sidebar_layout.addWidget(self.selected_sub_category_label)
        self.query_indicator = QLabel("Query:")
        sidebar_layout.addWidget(self.query_indicator)'''

        location_label = QLabel("Query from:")
        sidebar_layout.addWidget(location_label)

        lon_layout = QHBoxLayout()
        lon_label = QLabel("Longitude:")
        self.lon_input = QLineEdit()
        self.lon_input.setPlaceholderText("Longitude")
        lon_layout.addWidget(lon_label)
        lon_layout.addWidget(self.lon_input)
        sidebar_layout.addLayout(lon_layout)

        lat_layout = QHBoxLayout()
        lat_label = QLabel("Latitude:")
        self.lat_input = QLineEdit()
        self.lat_input.setPlaceholderText("Latitude")
        lat_layout.addWidget(lat_label)
        lat_layout.addWidget(self.lat_input)
        sidebar_layout.addLayout(lat_layout)

        # default to the location of Kennesaw State University
        longitude = -84.56537605292901  # Example: 84.5826111111111 for Kennesaw, GA
        latitude = 34.023438520758205  # Example: 34.039794444444446 for Kennesaw, GA
        self.lon_input.setText(str(longitude))
        self.lat_input.setText(str(latitude))

        time_label = QLabel("Date|Time:")
        sidebar_layout.addWidget(time_label)

        time_label = QLabel("Time:")
        sidebar_layout.addWidget(time_label)

        self.time_input = QDateTimeEdit()
        self.time_input.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.time_input.setDateTime(QDateTime.currentDateTime())
        sidebar_layout.addWidget(self.time_input)

        sidebar_layout.addStretch() # flex spacer to push button to bottom

        self.confirm_section_title = QLabel("Tracking: none")
        self.confirm_section_title.setWordWrap(True)
        self.confirm_section_title.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 20px;")
        sidebar_layout.addWidget(self.confirm_section_title)

        confirm_button = QPushButton("Submit")
        confirm_button.setStyleSheet("padding: 10px; font-size: 14px;")
        sidebar_layout.addWidget(confirm_button)
        confirm_button.clicked.connect(self.querySatellites)

        sidebar.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

    def setupLists(self, splitter):
        # Main categories list
        self.main_list = QListWidget()
        self.main_list.addItems(self.main_categories.keys())
        self.main_list.itemClicked.connect(self.updateSubCategories)
        splitter.addWidget(self.main_list)

        # Sub-categories list (initially empty)
        self.sub_list = QListWidget()
        splitter.addWidget(self.sub_list)
        self.sub_list.itemClicked.connect(self.categorySelected)

    def updateSubCategories(self, item):
        self.sub_list.clear()  # Clear previous items
        category_name = item.text()
        sub_categories = self.main_categories[category_name]

        for sub in sub_categories:
            widget_item = QListWidgetItem(sub['name'])
            self.sub_list.addItem(widget_item)

    def categorySelected(self, item):
        # Update the sidebar based on the selected sub-category
        self.confirm_section_title.setText(f"Targeting: \"{item.text()}\"")

    def presubmissionCheck(self):
        if self.main_list.currentItem() is None:
            return False
        if self.sub_list.currentItem() is None:
            return False
        return True

    def querySatellites(self):
        if not self.presubmissionCheck():
            DisplayWindow.clear_text(self.DisplayWindow)
            DisplayWindow.write_text(self.DisplayWindow, "Please select a category to track.")
            return
        DisplayWindow.clear_text(self.DisplayWindow)
        DisplayWindow.write_text(self.DisplayWindow, "Querying satellites...")

        for category in self.main_categories.values():
            for sub_category in category:
                if sub_category["name"] == self.sub_list.currentItem().text():
                    self.query = sub_category["query"]
                    break

        format = 'tle'
        tle_url = f'https://celestrak.org/NORAD/elements/gp.php?GROUP={self.query}&FORMAT={format}'
        satellites = load.tle_file(tle_url, filename='queried_satellites.txt', reload=True)
        ts = load.timescale()
        t = ts.now()
        observer = Topos(latitude_degrees=float(self.lat_input.text()), longitude_degrees=float(self.lon_input.text()))
        for sat in satellites:
            difference = sat - observer
            topocentric = difference.at(t)
            alt, az, distance = topocentric.altaz()

            text = ""
            if alt.degrees > 0:  # Checking if the satellite is above the horizon
                text = f"<span style='color: #00FF00;'>{sat.name} {alt.degrees}</span>"
            else:
                text = f"<span style='color: #FF0000;'>{sat.name} {alt.degrees}</span>"

            DisplayWindow.write_text(self.DisplayWindow, text) """
