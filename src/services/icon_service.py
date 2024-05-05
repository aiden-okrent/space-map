#
import os

from config.paths import ASSETS
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QImage, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer


class IconService:
    """ Icon Service Class, responsible for retrieving and unpacking svg icons for the application."""
    def __init__(self) -> None:
        pass

    def getIcon(self, name: str, color: Qt.GlobalColor):
        """ Returns a QIcon object from a svg file in the 'assets\icons' directory."""
        svg = os.path.join(ASSETS, 'icons', name)
        if not os.path.exists(svg):
            return None
        return self.build(svg, color)

    def build(self, iconPath, color: Qt.GlobalColor):
        """Build a QIcon from an svg file."""
        px = 512
        icon = QIcon(str(iconPath))
        pixmap = QPixmap(icon.pixmap(px, px))
        renderer = QSvgRenderer(iconPath)
        pixmap = QPixmap(px, px)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), color)
        painter.end()
        return QIcon(pixmap)