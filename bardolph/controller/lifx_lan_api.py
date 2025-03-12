import logging

import lifxlan

from bardolph.controller import i_controller, lifx_lan_light
from bardolph.lib import i_lib
from bardolph.lib.injection import bind, inject
from bardolph.lib.param_helper import param_color, param_16, param_32


class LifxLanApi(i_controller.LightApi):
    @inject(i_lib.Settings)
    def __init__(self, settings):
        num_expected = settings.get_value('default_num_lights', None)
        self._lifxlan = lifxlan.LifxLAN(num_expected)

    @inject(i_lib.Settings)
    def get_lights(self, settings):
        try:
            lights = [
                self._build_light(impl) for impl in self._lifxlan.get_lights()]
        except lifxlan.errors.WorkflowException as ex:
            logging.error("In get_lights(): {}".format(ex))
            raise i_controller.LightException(ex)

        expected = settings.get_value('default_num_lights', None)
        if expected is not None:
            actual = len(lights)
            if actual < expected:
                logging.info(
                    "Expected {} devices, found {}".format(expected, actual))
        return lights

    def set_color_all_lights(self, color, duration):
        color = param_color(color)
        self._lifxlan.set_color_all_lights(color, param_32(duration), True)

    def set_power_all_lights(self, power_level, duration):
        self._lifxlan.set_power_all_lights(
            param_16(power_level), param_32(duration), True)

    def _build_light(self, impl):
        features = impl.get_product_features()
        product_name = impl.get_product_name()
        if features.get('multizone', False):
            return lifx_lan_light.MultizoneLight(impl)
        elif impl.get_product_features().get('matrix', False):
            return lifx_lan_light.MatrixLight(impl)
        return lifx_lan_light.Light(impl)


def configure():
    bind(LifxLanApi).to(i_controller.LightApi)
