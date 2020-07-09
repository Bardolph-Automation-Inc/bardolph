import logging
import time

from lifxlan.errors import WorkflowException

from bardolph.lib.color import rounded_color

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
            logging.warning("In set_color(): {}".format(ex))

    def get_color(self):
        try:
            return self._impl.get_color()
        except WorkflowException as ex:
            logging.warning("In get_color(): {}".format(ex))
        return [-1] * 4

    def set_zone_color(self, first_zone, last_zone, color, duration):
        try:
            self._impl.set_zone_color(
                first_zone, last_zone, rounded_color(color), duration)
        except WorkflowException as ex:
            logging.warning("In set_zone_color(): {}".format(ex))

    def get_color_zones(self, first_zone=None, last_zone=None):
        try:
            return self._impl.get_color_zones(first_zone, last_zone)
        except WorkflowException as ex:
            logging.warning("In get_color_zones(): {}".format(ex))

    def set_power(self, power, duration, rapid=True):
        try:
            return self._impl.set_power(round(power), duration, rapid)
        except WorkflowException as ex:
            logging.warning("In set_power(): {}".format(ex))

    def get_power(self):
        try:
            return self._impl.get_power()
        except WorkflowException as ex:
            logging.warning("In get_power(): {}".format(ex))
        return -1
