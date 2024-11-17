class LightException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LightApi:
    def get_lights(self): pass
    def set_color_all_lights(self, color, duration): pass
    def set_power_all_lights(self, power_level, duration): pass


class LightSet:
    def discover(self): pass
    def refresh(self): pass
    def get_lights(self): pass
    def get_light_count(self): pass
    def get_light_names(self): pass
    def get_light(self, light_name): pass
    def get_group_names(self): pass
    def get_group_lights(self, group_name): pass
    def get_location_names(self): pass
    def get_location_lights(self, loc_name): pass
    def set_color_all_lights(self, color, duration): pass
    def set_power_all_lights(self, power_level, duration): pass
    def get_successful_discoveries(self): pass
    def get_failed_discoveries(self): pass


class Light:
    def get_name(self) -> str: pass
    def get_group(self) -> str: pass
    def get_location(self) -> str: pass
    def get_age(self) -> float: pass
    def get_color(self): pass
    def set_color(self, color, duration) -> None: pass
    def get_power(self) -> int: pass
    def set_power(self, power, duration) -> None: pass


class MultizoneLight(Light):
    def get_zone_colors(self, first_zone, last_zone): pass
    def set_zone_colors(self, first_zone, last_zone, color, duration): pass


class MatrixLight(Light):
    def get_matrix(self): pass
    def set_matrix(self, matrix, duration): pass
