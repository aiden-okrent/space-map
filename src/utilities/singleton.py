# singleton.py
#
# Singleton pattern for the following classes:

# controller.py ApplicationController
class ControllerSingleton:
    __instance = None
    def __new__(cls, controller):
        if ControllerSingleton.__instance is None:
            ControllerSingleton.__instance = object.__new__(cls)
            ControllerSingleton.__instance.controller = controller
        return ControllerSingleton.__instance

    def get_controller(self):
        return self.controller

# model/timescale.py Timescale
class TimescaleSingleton:
    __instance = None
    def __new__(cls, timescale):
        if TimescaleSingleton.__instance is None:
            TimescaleSingleton.__instance = object.__new__(cls)
            TimescaleSingleton.__instance.timescale = timescale
        return TimescaleSingleton.__instance

    def get_timescale(self):
        return self.timescale

# model/earth.py Earth
class EarthSingleton:
    __instance = None
    def __new__(cls, earth):
        if EarthSingleton.__instance is None:
            EarthSingleton.__instance = object.__new__(cls)
            EarthSingleton.__instance.earth = earth
        return EarthSingleton.__instance

    def get_earth(self):
        return self.earth

# view/mainView.py MainView
class MainViewSingleton:
    __instance = None
    def __new__(cls, main_view):
        if MainViewSingleton.__instance is None:
            MainViewSingleton.__instance = object.__new__(cls)
            MainViewSingleton.__instance.main_view = main_view
        return MainViewSingleton.__instance

    def get_main_view(self):
        return self.main_view

# view/map3DView.py Map3DView
class Map3DViewSingleton:
    __instance = None
    def __new__(cls, map_3d_view):
        if Map3DViewSingleton.__instance is None:
            Map3DViewSingleton.__instance = object.__new__(cls)
            Map3DViewSingleton.__instance.map_3d_view = map_3d_view
        return Map3DViewSingleton.__instance

    def get_map_3d_view(self):
        return self.map_3d_view

# view/screen2DView.py Screen2DView
class Screen2DViewSingleton:
    __instance = None
    def __new__(cls, screen_2d_view):
        if Screen2DViewSingleton.__instance is None:
            Screen2DViewSingleton.__instance = object.__new__(cls)
            Screen2DViewSingleton.__instance.screen_2d_view = screen_2d_view
        return Screen2DViewSingleton.__instance

    def get_screen_2d_view(self):
        return self.screen_2d_view