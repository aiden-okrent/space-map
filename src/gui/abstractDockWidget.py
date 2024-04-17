from PySide6.QtCore import QEvent, QPoint, QSettings, QSize, Qt
from PySide6.QtWidgets import QApplication, QDockWidget, QMainWindow, QWidget

'''        TODO: Create an abstract dock widget class as the base for all dock widgets
        it should be hidden by default and only shown if thats set
        it should have methods to toggle features such as movable, closable, floating, resizable, respecting defaults set when created
        it should have a simple method for use in a dock menu to show/hide the dock widget
        it should use a similar method as abstractwindows to save and restore settings for itself as a dock widget
        maybe abstract dock widget should be a subclass of abstract window? it could just override the save and restore settings methods...
            but it wouldnt have much else in common with abstract window, so it will be its own AbstractDockWidget class

        it needs to have a method to control any widgets inside to inform of closing, resizing, floating, moving, so that they can react accordingly
            for example, openglwidgets need to pause rendering while being moved
            and all widgets need to save their settings when the dock widget is closed/hidden
'''

# An abstract class to serve as the base for all dock widgets in the application
class AbstractDockWidget(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.settings = QSettings()
        self.settingsGroup = "default"

        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable) # make dock widget movable by default
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable) # make dock widget closable by default
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetVerticalTitleBar) # make dock widget title bar vertical by default

        self.setWidget(QWidget()) # set a default widget for the dock widget
        self.widget().addAction("Test Action")
        self.widget().addAction("Test Action 2")
        self.widget().addAction("Test Action 3")

    def resize(self, size: QSize) -> None:
        print("resize", size)
        return super().resize(size)

    def move(self, position: QPoint) -> None:
        print("move", position)
        return super().move(position)

    def featuresChanged(self, features: QDockWidget.DockWidgetFeature) -> None:
        print("features changed", features)
        return super().featuresChanged(features)

    def dockLocationChanged(self, area: Qt.DockWidgetArea) -> None:
        print("dock location changed", area)
        return super().dockLocationChanged(area)

    '''
        inherited methods from QDockWidget:
            setWidget(self, widget: QWidget) -> None
            featuresChanged(self, features: QDockWidget.DockWidgetFeatures) -> None
            setAllowedAreas(self, areas: Qt.DockWidgetArea) -> None
            setFeatures(self, features: QDockWidget.DockWidgetFeatures) -> None
            setFloating(self, floating: bool) -> None
            setHidden(self, hidden: bool) -> None
            setAllowedAreas(self, areas: Qt.DockWidgetArea)
            setFeatures(self, features: QDockWidget.DockWidgetFeatures)
            setFloating(self, floating: bool)
            setHidden(self, hidden: bool)

            closeEvent(self, event)

    '''