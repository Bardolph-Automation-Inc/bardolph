import logging
import threading
import time

from bardolph.controller import i_controller
from bardolph.lib import i_lib
from bardolph.lib.color import rounded_color
from bardolph.lib.injection import bind_instance, inject, provide
from bardolph.lib.param_helper import param_32, param_bool, param_color
from bardolph.lib.sorted_list import SortedDict, SortedList


class _MemberListSet:
    """
    Manage members of groups or locations using light names.
    """
    _empty_list: SortedList[str] = SortedList()

    def __init__(self):
        self._lists: SortedDict[str, str] = SortedDict()

    def get_names(self) -> SortedList[str]:
        return SortedList.from_list(self._lists.keys())

    def get_light_names(self, list_name) -> SortedList[str]:
        return self._lists.get(list_name) or self._empty_list

    def set_membership(self, light_name: str, list_name: str) -> None:
        if self._lists.has(list_name, light_name):
            return
        self.clear_existing(light_name)
        self._lists.add(list_name, light_name)

    def clear_existing(self, light_name: str) -> None:
        self._lists.remove_from_all(light_name)


class LightSet(i_controller.LightSet):
    _run_discover = False

    def __init__(self):
        self._lights: dict[str, i_controller.Light] = {}
        self._groups = _MemberListSet()
        self._locations = _MemberListSet()
        self._lock = threading.RLock()

    @inject(i_controller.LightApi)
    def discover(self, light_api: i_controller.LightApi) -> bool:
        self._run_discover = True
        with self._lock:
            try:
                for light in light_api.get_lights():
                    name = light.get_name()
                    self._lights[name] = light
                    self._groups.set_membership(name, light.get_group())
                    self._locations.set_membership(name, light.get_location())
            except i_controller.LightException as ex:
                logging.warning("In discover():\n{}".format(ex))
                return False
        return True

    def refresh(self) -> None:
        self.discover()
        self._garbage_collect()

    def stop_discover(self) -> None:
        self._run_discover = False

    @inject(i_lib.Settings)
    def _garbage_collect(self, settings: i_lib.Settings) -> None:
        """
        Get rid of a light's proxy if it hasn't responded for a while.
        """
        logging.debug("garbage collection")

        # Seconds
        max_age = int(settings.get_value('light_gc_time', 5 * 60))

        with self._lock:
            to_be_deleted = [light for light in self._lights.values()
                             if light.get_age() > max_age]
            for light in to_be_deleted:
                name = light.get_name()
                if name in self._lights:
                    del self._lights[name]
                self._groups.clear_existing(name)
                self._locations.clear_existing(name)

    def get_light_names(self) -> SortedList[str]:
        return SortedList.from_list(self._lights.keys())

    def get_light(self, light_name) -> i_controller.Light | None:
        return self._lights.get(light_name)

    def get_group_names(self) -> SortedList[str]:
        return self._groups.get_names()

    def get_group_lights(self, group_name) -> list[i_controller.Light]:
        return self._groups.get_light_names(group_name)

    def get_location_names(self) -> SortedList[str]:
        return self._locations.get_names()

    def get_location_lights(self, loc_name) -> SortedList[str]:
        return self._locations.get_light_names(loc_name)

    @inject(i_controller.LightApi)
    def set_color_all_lights(
            self, color, duration, light_api: i_controller.LightApi) -> bool:
        color = param_color(color)
        duration = param_32(duration)
        light_api.set_color_all_lights(rounded_color(color), duration)
        return True

    @inject(i_controller.LightApi)
    def set_power_all_lights(
            self,
            power_level,
            duration,
            light_api: i_controller.LightApi) -> bool:
        power_level = param_bool(power_level)
        duration = param_32(duration)
        light_api.set_power_all_lights(power_level, duration)
        return True


def _start_light_refresh():
    logging.debug("Starting refresh thread.")
    threading.Thread(
        target=_light_refresh, name='discovery', daemon=True).start()


def _light_refresh() -> None:
    settings = provide(i_lib.Settings)

    # Seconds
    success_sleep_time = float(
        settings.get_value('refresh_sleep_time', 5 * 60))
    failure_sleep_time = float(
        settings.get_value('failure_sleep_time', success_sleep_time))
    complete_success = False

    while LightSet._run_discover:
        time.sleep(
            success_sleep_time if complete_success else failure_sleep_time)
        light_set = provide(LightSet)
        try:
            complete_success = light_set.refresh()
        except i_controller.LightException as ex:
            logging.warning("Error during discovery {}".format(ex))


@inject(i_lib.Settings)
def configure(settings: i_lib.Settings) -> None:
    """
    Set up an instance of LightSet as a singleton.
    """
    light_set = LightSet()
    light_set.discover()
    if not bool(settings.get_value('single_light_discover', False)):
        _start_light_refresh()

    bind_instance(light_set).to(i_controller.LightSet)
