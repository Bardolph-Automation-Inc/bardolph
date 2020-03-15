#!/usr/bin/env python

import logging
import threading
import time

import lifxlan

from ..controller.i_controller import Lifx
from ..lib.injection import bind_instance, inject
from ..lib.i_lib import Settings

from . import i_controller
from .light import Light


class LightSet(i_controller.LightSet):
    """
    Groups and locations are stored in dictionaries of set() objects. Each
    dictionary is keyed on group or location name. The value
    associated with a group or location name is a set of Light objects.
    """
    the_instance = None

    def __init__(self):
        self._light_dict = {}
        self._group_dict = {}
        self._location_dict = {}
        self._num_successful_discovers = 0
        self._num_failed_discovers = 0
        self._last_discover = None

    def __len__(self):
        return self.get_count()

    @classmethod
    def configure(cls):
        LightSet.the_instance = LightSet()

    @classmethod
    def get_instance(cls):
        return LightSet.the_instance

    @inject(Lifx)
    def discover(self, lifx):
        logging.info("discover()")
        self._last_discover = time.time()

        try:
            for lifx_light in lifx.get_lights():
                light = Light(lifx_light)
                self._light_dict[light.name] = light
                LightSet._update_memberships(
                    light, light.group, self._group_dict)
                LightSet._update_memberships(
                    light, light.location, self._location_dict)
        except lifxlan.errors.WorkflowException as ex:
            logging.warning("In discover():\n{}".format(ex))
            return False
        return True

    def refresh(self):
        logging.debug("refresh()")
        if self.discover():
            self._num_successful_discovers += 1
        else:
            self._num_failed_discovers += 1
        self._garbage_collect()
        self._last_discover = time.time()

    @classmethod
    def _update_memberships(cls, light, current_set_name, set_dict):
        if current_set_name not in set_dict:
            # New set
            LightSet._remove_memberships(light, set_dict)
            set_dict[current_set_name] = set([light])
        elif light not in set_dict[current_set_name]:
            # Changed set or newer light object has same name
            LightSet._remove_memberships(light, set_dict)
            set_dict[current_set_name].add(light)

    @classmethod
    def _remove_memberships(cls, light, set_dict):
        # Remove the light from every set in set_dict that it belongs to.
        target_set_names = []
        for set_name in set_dict.keys():
            the_set = set_dict[set_name]
            target_light = None
            for member in the_set:
                if member.name == light.name:
                    target_light = member
                    break
            if target_light is not None:
                the_set.discard(target_light)
                if len(the_set) == 0:
                    target_set_names.append(set_name)
        for set_name in target_set_names:
            del set_dict[set_name]

    @inject(Settings)
    def _garbage_collect(self, settings):
        # Get rid of a light's proxy if it hasn't responded for a while.
        max_age = int(settings.get_value('light_gc_time', 20 * 60))
        target_lights = []
        for light_name in self._light_dict.keys():
            light = self._light_dict[light_name]
            if light.age > max_age:
                LightSet._remove_memberships(light, self._group_dict)
                LightSet._remove_memberships(light, self._location_dict)
                target_lights.append(light_name)
        for light_name in target_lights:
            logging.debug("_garbage_collect() deleting {}".format(light_name))
            del self._light_dict[light_name]

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
        return self._group_dict.keys()

    @property
    def location_names(self):
        """ list of strings """
        return self._location_dict.keys()

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
        """ returns an instance of i_lib.Light, or None if it's not there """
        return self._light_dict.get(name, None)

    def get_group(self, name):
        """ list of Lights """
        return self._group_dict.get(name, None)

    def get_location(self, name):
        """ list of Lights. """
        return self._location_dict.get(name, None)

    @inject(Lifx)
    def set_color(self, color, duration, lifx):
        lifx.set_color_all_lights(color, duration)
        return True

    @inject(Lifx)
    def set_power(self, power_level, duration, lifx):
        lifx.set_power_all_lights(power_level, duration)
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
            lights._num_successful_discovers += 1
        except lifxlan.errors.WorkflowException as ex:
            logging.warning("Error during discovery {}".format(ex))
            lights._num_failed_discovers += 1


@inject(Settings)
def configure(settings):
    LightSet.configure()
    lights = LightSet.get_instance()
    bind_instance(lights).to(i_controller.LightSet)
    lights.discover()

    single = bool(settings.get_value('single_light_discover', False))
    if not single:
        start_light_refresh()
