#

import os
import sys

if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

ASSETS = os.path.join(BASE_PATH, 'assets')
ICONS = os.path.join(ASSETS, 'icons')
TEXTURES = os.path.join(ASSETS, 'textures')

DATA = os.path.join(BASE_PATH, 'data')
TLE = os.path.join(DATA, 'tle')