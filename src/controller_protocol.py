from typing import Protocol


class ControllerProtocol(Protocol):
    def some_controller_method(self) -> None:
        pass
    def refresh_combobox(self):
        pass
    def track_Satellite(self):
        pass
    def display_2D_map(self):
        pass

    def sat_combobox_activated(self, index):
        pass
    def get_satellite_dict(self):
        pass
    def setCurrentSatellite(self, satellite):
        pass
    def get_current_satellite_translation(self):
        pass
    def toggle_quality(self):
        pass
    def toggle_scene():
        pass