import logging

import lifxlan

from . import i_controller
from ..lib import i_lib
from ..lib.injection import bind, inject

class Lifx(i_controller.Lifx):
    @inject(i_lib.Settings)
    def __init__(self, settings):
        num_expected = settings.get_value('default_num_lights', None)
        self._lifxlan = lifxlan.LifxLAN(num_expected)
    
    @inject(i_lib.Settings)
    def get_lights(self, settings):
        lights = self._lifxlan.get_lights()
        expected = settings.get_value('default_num_lights', None)
        if expected is not None:
            actual = len(lights)
            if actual < expected:
                logging.warning(
                    "Expected {} devices, found {}".format(expected, actual))
        return lights
    
    def set_color_all_lights(self, color, duration):
        self._lifxlan.set_color_all_lights(color, duration, True)
    
    def set_power_all_lights(self, power_level, duration):
        self._lifxlan.set_power_all_lights(power_level, duration, True)


def configure():
    bind(Lifx).to(i_controller.Lifx)
