import logging
import time

from lifxlan.errors import WorkflowException

from bardolph.lib.color import rounded_color
from bardolph.lib.retry import tries


_MAX_TRIES = 3


class LightException(Exception):
    def __init__(self, cause):
        super().__init__('Exception from light API {}'.format(cause))
        self._cause = cause

    @property
    def cause(self):
        return self._cause


class Light:
    def __init__(self, lifx_light):
        self._impl = lifx_light
        self._name = lifx_light.get_label()
        self._group = lifx_light.get_group()
        self._location = lifx_light.get_location()
        self._multizone = lifx_light.supports_multizone()
        self._birth = time.time()

    def __repr__(self):
        fmt = 'Light(_name="{}", _group="{}", _location="{}", _multizone={}, '
        fmt += ' _birth={})'
        rep = fmt.format(
            self._name, self._group, self._location, self._multizone,
            self._birth)
        return rep

    @property
    def group(self):
        return self._group

    @property
    def location(self):
        return self._location

    @property
    def name(self):
        return self._name

    @property
    def multizone(self):
        return self._multizone

    def get_age(self):
        #seconds
        return time.time() - self._birth

    def set_color(self, color, duration, rapid=True):
        try:
            self._impl.set_color(rounded_color(color), duration, rapid)
        except WorkflowException as ex:
            logging.warning(ex)

    def get_color(self):
        try:
            return self._impl.get_color()
        except WorkflowException as ex:
            logging.warning(ex)
        return [-1] * 4

    @tries(_MAX_TRIES, WorkflowException)
    def set_zone_color(self, first_zone, last_zone, color, duration) -> None:
        # Unknown why this happens.
        if not hasattr(self._impl, 'set_zone_color'):
            logging.error(
                'No set_zone_color for light of type', type(self._impl))
        else:
            self._impl.set_zone_color(
                first_zone, last_zone, rounded_color(color), duration)

    @tries(_MAX_TRIES, WorkflowException)
    def get_color_zones(self, first_zone=None, last_zone=None):
        return self._impl.get_color_zones(first_zone, last_zone)

    @tries(_MAX_TRIES, WorkflowException)
    def set_power(self, power, duration, rapid=True):
        return self._impl.set_power(round(power), duration, rapid)

    @tries(_MAX_TRIES, WorkflowException)
    def get_power(self):
        return self._impl.get_power()
