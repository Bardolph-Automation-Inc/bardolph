import logging
import threading
import time

from bardolph.controller import i_controller
from bardolph.lib.color import rounded_color
from bardolph.lib import i_lib
from bardolph.lib.injection import bind_instance, inject, provide
from bardolph.lib.param_helper import param_bool, param_color, param_32
from bardolph.lib.sorted_list import SortedList


class LightSet(i_controller.LightSet):
    """
    All lights (inistances of i_controller.Light) are stored in _light_dict,
    keyed on the light's name.

    Locations and groups are stored in _location_dict (key is location name)
    and _group_dict (key is group name). Each value in the location or group
    dict is a list of strings containing light names.
    """
    def __init__(self):
        self._lights = {}
        self._light_names = SortedList()
        self._groups = {}
        self._locations = {}
        self._num_successful_discovers = 0
        self._num_failed_discovers = 0

    @inject(i_controller.LightApi)
    def discover(self, light_api):
        logging.debug('start discover. so far, successes = {}, fails = {}'
                      .format(self._num_successful_discovers,
                              self._num_failed_discovers))
        try:
            for light in light_api.get_lights():
                light_name = light.get_name()
                self._light_names.add(light_name)
                self._lights[light_name] = light
                LightSet._update_memberships(
                    light, light.get_group(), self._groups)
                LightSet._update_memberships(
                    light, light.get_location(), self._locations)
        except i_controller.LightException as ex:
            self._num_failed_discovers += 1
            logging.warning("In discover():\n{}".format(ex))
            return False

        self._num_successful_discovers += 1
        return True

    def refresh(self):
        self.discover()
        self._garbage_collect()

    @staticmethod
    def _update_memberships(light, name, target_dict):
        """
        Update the group and location dictionaries with a light's current group
        and location.

        light : i_controller.Light
            The light to be updated in the group and location dictionaries.
        name : str
            The name of the group or location the light belongs to.
        target_dict : dict
            The dictionary, either groups or locations, that is to hold a
            reference to the light.
        """
        LightSet._remove_memberships(light, target_dict)
        if name not in target_dict:
            target_dict[name] = SortedList(light.get_name())
        else:
            target_dict[name].add(light.get_name())

    @staticmethod
    def _remove_memberships(light, target_dict):
        # Remove the light from from the set_dict (groups or locations) that
        # it belongs to.
        to_be_deleted = []

        # From each group or location within the dict, remove the light.
        # Delete the group or location if it gets down to zero members.
        for list_name, light_list in target_dict.items():
            light_list.remove(light.get_name())
            if len(light_list) == 0:
                to_be_deleted.append(list_name)
        for list_name in to_be_deleted:
            del target_dict[list_name]

    @inject(i_lib.Settings)
    def _garbage_collect(self, settings):
        # Get rid of a light's proxy if it hasn't responded for a while.
        logging.debug("garbage collect, currently have {} lights"
                      .format(len(self._lights)))
        max_age = int(settings.get_value('light_gc_time', 20 * 60))
        target_lights = []
        for light in self._lights.values():
            if light.get_age() > max_age:
                LightSet._remove_memberships(light, self._groups)
                LightSet._remove_memberships(light, self._locations)
                target_lights.append(light.get_name())
        for light_name in target_lights:
            logging.debug("_garbage_collect() deleting {}".format(light_name))
            self._light_names.remove(light_name)
            self._lights[light_name] = None
            del self._lights[light_name]

    def get_lights(self):
        return list(self._lights.values())

    def get_light_count(self) -> int:
        return len(self._lights)

    def get_light_names(self) -> SortedList:
        """ SortedList of strings """
        return self._light_names

    def get_light(self, light_name):
        """ instance of i_controller.Light or None """
        return self._lights.get(light_name)

    def get_group_names(self) -> SortedList:
        """ list of strings """
        return SortedList(self._groups.keys())

    def get_group_lights(self, group_name):
        """ list of light names or None """
        return self._groups.get(group_name)

    def get_location_names(self) -> SortedList:
        """ list of strings, each containing a location name """
        return SortedList(self._locations.keys())

    def get_location_lights(self, loc_name):
        """ list of light names or None """
        return self._locations.get(loc_name)

    @inject(i_controller.LightApi)
    def set_color_all_lights(self, color, duration, light_api):
        color = param_color(color)
        duration = param_32(duration)
        light_api.set_color_all_lights(rounded_color(color), duration)
        return True

    @inject(i_controller.LightApi)
    def set_power_all_lights(self, power_level, duration, light_api):
        power_level = param_bool(power_level)
        duration = param_32(duration)
        light_api.set_power_all_lights(power_level, duration)
        return True

    def get_successful_discovers(self):
        return self._num_successful_discovers

    def get_failed_discovers(self):
        return self._num_failed_discovers


def _start_light_refresh():
    logging.debug("Starting refresh thread.")
    threading.Thread(
        target=_light_refresh, name='discovery', daemon=True).start()


def _light_refresh():
    settings = provide(i_lib.Settings)
    success_sleep_time = float(
        settings.get_value('refresh_sleep_time', 600))
    failure_sleep_time = float(
        settings.get_value('failure_sleep_time', success_sleep_time))
    complete_success = False

    while True:
        time.sleep(
            success_sleep_time if complete_success else failure_sleep_time)
        light_set = provide(i_controller.LightSet)
        try:
            complete_success = light_set.refresh()
        except i_controller.LightException as ex:
            logging.warning("Error during discovery {}".format(ex))


@inject(i_lib.Settings)
def configure(settings):
    light_set = LightSet()
    light_set.discover()
    if not bool(settings.get_value('single_light_discover', False)):
        _start_light_refresh()

    bind_instance(light_set).to(i_controller.LightSet)
