from abc import ABC, abstractmethod


class LightException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LightApi(ABC):
    @abstractmethod
    def get_lights(self):
        pass

    @abstractmethod
    def set_color_all_lights(self, color, duration):
        pass

    @abstractmethod
    def set_power_all_lights(self, power_level, duration):
        pass


class LightSet(ABC):
    @abstractmethod
    def discover(self):
        pass

    @abstractmethod
    def refresh(self):
        pass

    @abstractmethod
    def get_light_names(self):
        pass

    @abstractmethod
    def get_light(self, light_name):
        pass

    @abstractmethod
    def get_group_names(self):
        pass

    @abstractmethod
    def get_group_lights(self, group_name):
        pass

    @abstractmethod
    def get_location_names(self):
        pass

    @abstractmethod
    def get_location_lights(self, loc_name):
        pass

    @abstractmethod
    def set_color_all_lights(self, color, duration):
        pass

    @abstractmethod
    def set_power_all_lights(self, power_level, duration):
        pass


class Light(ABC):
    @abstractmethod
    def get_uid(self) -> int:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_group(self) -> str:
        pass

    @abstractmethod
    def get_location(self) -> str:
        pass

    @abstractmethod
    def get_height(self) -> int:
        pass

    @abstractmethod
    def get_width(self) -> int:
        pass

    @abstractmethod
    def is_color(self) -> bool:
        pass

    @abstractmethod
    def get_age(self) -> float:
        pass

    @abstractmethod
    def get_color(self):
        pass

    @abstractmethod
    def set_color(self, color, duration) -> None:
        pass

    @abstractmethod
    def get_power(self) -> int:
        pass

    @abstractmethod
    def set_power(self, power, duration) -> None:
        pass


class MultizoneLight(Light):
    @abstractmethod
    def get_zone_colors(self, first_zone, last_zone):
        pass

    @abstractmethod
    def set_zone_colors(self, first_zone, last_zone, color, duration):
        pass


class MatrixLight(Light):
    @abstractmethod
    def get_matrix(self):
        pass

    @abstractmethod
    def set_matrix(self, matrix, duration):
        pass
