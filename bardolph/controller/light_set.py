#!/usr/bin/env python

import logging
import threading
import time

import lifxlan

from ..lib.color import average_color
from ..lib.injection import bind_instance, inject
from ..lib.i_lib import Settings

from . import i_controller


class LightSet(i_controller.LightSet):
    the_instance = None

    def __init__(self):
        self._light_dict = {}
        self._groups = {}
        self._locations = {}
        self._num_successful_discovers = 0
        self._num_failed_discovers = 0
        self._last_discover = None

    def __len__(self):
        return self.get_count()

    @classmethod
    def configure(cls):
        if LightSet.the_instance is None:
            LightSet.the_instance = LightSet()

    @classmethod
    def get_instance(cls):
        return LightSet.the_instance

    @inject(Settings)
    def discover(self, settings):
        logging.debug("discover()")
        default_num = int(settings.get_value('default_num_lights', 0))
        num_expected = None if default_num == 0 else default_num
        try:
            light_list = lifxlan.LifxLAN(num_expected).get_lights()
            new_dict = {}
            for light in light_list:
                new_dict[light.get_label()] = light
            self._light_dict = new_dict
            self._last_discover = time.localtime()

            self._groups = LightSet._build_set(
                light_list, lifxlan.device.Device.get_group)
            self._locations = LightSet._build_set(
                light_list, lifxlan.device.Device.get_location)
        except lifxlan.errors.WorkflowException as ex:
            logging.error("Error during discovery {}".format(ex))
            return False

        actual = len(self._light_dict)
        if num_expected is not None and actual < num_expected:
            logging.warning(
                "Expected {} devices, found {}".format(num_expected, actual))
            return False
        return True

    @classmethod
    def _build_set(cls, light_list, fn):
        # Produces a dictionary keyed on group or location name, pointing to
        # a list of (lifxlan) light objects.
        sets = {}
        for light in light_list:
            set_name = fn(light)
            if set_name in sets:
                sets[set_name].append(light)
            else:
                sets[set_name] = [light]
        return sets

    @property
    def light_names(self):
        """ list of strings """
        return self._light_dict.keys()

    @property
    def lights(self):
        """ list of Lights. """
        return self._light_dict.values()

    @property
    def group_names(self):
        """ list of strings """
        return self._groups.keys()

    @property
    def location_names(self):
        """ list of strings """
        return self._locations.keys()

    @property
    def count(self):
        return len(self._light_dict)

    @property
    def last_discover(self):
        return self._last_discover

    @property
    def successful_discovers(self):
        return self._num_successful_discovers

    @property
    def failed_discovers(self):
        return self._num_failed_discovers

    def get_light(self, name):
        """ returns an instance of lifxlan.Light, or None if it's not there """
        return self._light_dict.get(name, None)

    def get_group(self, name):
        """ list of Lights """
        return self._groups.get(name, [])

    def get_location(self, name):
        """ list of Lights. """
        return self._locations.get(name, [])

    @inject(Settings)
    def set_color(self, color, duration, settings):
        num_expected = int(settings.get_value('default_num_lights', 0))
        lifx = lifxlan.LifxLAN(num_expected)
        lifx.set_color_all_lights(color, duration, True)
        return True

    def get_color(self):
        """ Returns arithmetic mean of each color setting. """
        return average_color(
            list(self.get_lifxlan().get_color_all_lights().values()))

    def set_power(self, power_level, duration):
        self.get_lifxlan().set_power_all_lights(power_level, duration, True)
        return True

    def get_power(self):
        """ Returns True if at least one bulb is on. """
        for state in self.get_lifxlan().get_power_all_lights().values():
            if state:
                return True
        return False

    @inject(Settings)
    def get_lifxlan(self, settings):
        num_expected = int(settings.get_value('default_num_lights', 0))
        return lifxlan.LifxLAN(num_expected)


def start_light_refresh():
    logging.info("Starting refresh thread.")
    threading.Thread(
        target=light_refresh, name='rediscover', daemon=True).start()


@inject(Settings)
def light_refresh(settings):
    success_sleep_time = float(settings.get_value('refresh_sleep_time'))
    failure_sleep_time = float(settings.get_value('failure_sleep_time'))
    complete_success = False

    while True:
        lights = LightSet.get_instance()
        try:
            complete_success = lights.discover()
            lights._num_successful_discovers += 1
        except lifxlan.errors.WorkflowException as ex:
            logging.warning("Error during discovery {}".format(ex))
            lights._num_failed_discovers += 1

        time.sleep(
            success_sleep_time if complete_success else failure_sleep_time)


@inject(Settings)
def configure(settings):
    LightSet.configure()
    lights = LightSet.get_instance()
    bind_instance(lights).to(i_controller.LightSet)
    lights.discover()

    single = bool(settings.get_value('single_light_discover', False))
    if not single:
        start_light_refresh()
