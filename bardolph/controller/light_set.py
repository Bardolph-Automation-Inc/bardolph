#!/usr/bin/env python

import logging
import threading
import time

import lifxlan

from bardolph.lib.color import rounded_color
from bardolph.lib.injection import bind_instance, inject
from bardolph.lib.sorted_list import SortedList
from bardolph.lib.i_lib import Settings

from .i_controller import Lifx
from . import i_controller
from .light import Light

class LightSet(i_controller.LightSet):
    """
    The lights are stored in _light_dict, keyed on light name. Locations and
    groups are stored in _location_dict and _group_dict as lists of strings
    containing light names.
    """
    the_instance = None

    def __init__(self):
        self._light_dict = {}
        self._group_dict = {}
        self._location_dict = {}
        self._light_names = SortedList()
        self._num_successful_discovers = 0
        self._num_failed_discovers = 0

    @staticmethod
    def configure():
        LightSet.the_instance = LightSet()

    @staticmethod
    def get_instance():
        return LightSet.the_instance

    @inject(Lifx)
    def discover(self, lifx):
        logging.debug('start discover. so far, successes = {}, fails = {}'
                      .format(self._num_successful_discovers,
                              self._num_failed_discovers))
        try:
            for lifx_light in lifx.get_lights():
                light = Light(lifx_light)
                self._light_dict[light.name] = light
                self._light_names.add(light.name)
                LightSet._update_memberships(
                    light, light.group, self._group_dict)
                LightSet._update_memberships(
                    light, light.location, self._location_dict)
        except lifxlan.errors.WorkflowException as ex:
            self._num_failed_discovers += 1
            logging.warning("In discover():\n{}".format(ex))
            return False

        self._num_successful_discovers += 1
        return True

    def refresh(self):
        self.discover()
        self._garbage_collect()

    @staticmethod
    def _update_memberships(light, current_set_name, set_dict):
        LightSet._remove_memberships(light, set_dict)
        if current_set_name not in set_dict:
            set_dict[current_set_name] = SortedList(light.name)
        else:
            set_dict[current_set_name].add(light.name)

    @staticmethod
    def _remove_memberships(light, set_dict):
        # Remove the light from every set in set_dict that it belongs to.
        target_set_names = []
        for list_name in set_dict.keys():
            the_list = set_dict[list_name]
            the_list.remove(light.name)
            if len(the_list) == 0:
                target_set_names.append(list_name)
        for set_name in target_set_names:
            del set_dict[set_name]

    @inject(Settings)
    def _garbage_collect(self, settings):
        # Get rid of a light's proxy if it hasn't responded for a while.
        logging.debug("garbage collect, currently have {} lights"
                      .format(len(self._light_dict)))
        max_age = int(settings.get_value('light_gc_time', 20 * 60))
        target_lights = []
        for light in self._light_dict.values():
            if light.get_age() > max_age:
                LightSet._remove_memberships(light, self._group_dict)
                LightSet._remove_memberships(light, self._location_dict)
                target_lights.append(light.name)
        for light_name in target_lights:
            logging.debug("_garbage_collect() deleting {}".format(light_name))
            self._light_names.remove(light_name)
            self._light_dict[light_name] = None
            del self._light_dict[light_name]

    @property
    def light_names(self) -> SortedList:
        """ list of strings """
        return self._light_names

    @property
    def group_names(self):
        """ list of strings """
        return SortedList(self._group_dict.keys())

    @property
    def location_names(self):
        """ list of strings """
        return SortedList(self._location_dict.keys())

    @property
    def count(self):
        return len(self._light_list)

    @property
    def successful_discovers(self):
        return self._num_successful_discovers

    @property
    def failed_discovers(self):
        return self._num_failed_discovers

    def get_light(self, name):
        """ returns an instance of i_lib.Light, or None if it's not there """
        return self._light_dict.get(name)

    def get_group(self, name):
        """ list of light names """
        return self._group_dict.get(name)

    def get_location(self, name):
        """ list of light names. """
        return self._location_dict.get(name)

    @inject(Lifx)
    def set_color(self, color, duration, lifx):
        lifx.set_color_all_lights(rounded_color(color), duration)
        return True

    @inject(Lifx)
    def set_power(self, power_level, duration, lifx):
        lifx.set_power_all_lights(round(power_level), duration)
        return True


def start_light_refresh():
    logging.debug("Starting refresh thread.")
    threading.Thread(
        target=light_refresh, name='rediscover', daemon=True).start()


@inject(Settings)
def light_refresh(settings):
    success_sleep_time = float(
        settings.get_value('refresh_sleep_time', 600))
    failure_sleep_time = float(
        settings.get_value('failure_sleep_time', success_sleep_time))
    complete_success = False

    while True:
        time.sleep(
            success_sleep_time if complete_success else failure_sleep_time)
        lights = LightSet.get_instance()
        try:
            complete_success = lights.refresh()
        except lifxlan.errors.WorkflowException as ex:
            logging.warning("Error during discovery {}".format(ex))


@inject(Settings)
def configure(settings):
    LightSet.configure()
    lights = LightSet.get_instance()
    bind_instance(lights).to(i_controller.LightSet)
    lights.discover()

    single = bool(settings.get_value('single_light_discover', False))
    if not single:
        start_light_refresh()
