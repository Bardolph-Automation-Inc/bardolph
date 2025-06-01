import logging

from lifxlan.errors import WorkflowException
from lifxlan.msgtypes import (GetDeviceChain, GetTileState64, SetTileState64,
                              StateDeviceChain, StateTileState64)

from bardolph.controller import i_controller, light
from bardolph.controller.color_matrix import ColorMatrix
from bardolph.lib.param_helper import param_16, param_32, param_color
from bardolph.lib.retry import tries

_MAX_TRIES = 3


class Light(light.Light):
    def __init__(self, impl):
        super().__init__(
            impl.get_label(), impl.get_group(), impl.get_location())
        self._impl = impl
        self.product_features = impl.get_product_features()
        self._is_color = self.product_features.get('color', False)

    def is_color(self):
        return self._is_color

    @tries(_MAX_TRIES, WorkflowException, [-1] * 4)
    def get_color(self):
        return self._impl.get_color()

    @tries(_MAX_TRIES, WorkflowException)
    def set_color(self, color, duration):
        color = param_color(color)
        duration = param_32(duration)
        self._impl.set_color(color, duration, True)

    @tries(_MAX_TRIES, WorkflowException)
    def get_power(self) -> int:
        return round(self._impl.get_power())

    @tries(_MAX_TRIES, WorkflowException)
    def set_power(self, power, duration, rapid=True):
        power = param_16(power)
        duration = param_32(duration)
        return self._impl.set_power(power, duration, rapid)


class MultizoneLight(Light, i_controller.MultizoneLight):
    def __init__(self, impl, num_zones=None):
        super().__init__(impl)
        self._num_zones = num_zones or len(self.get_zone_colors())

    def get_height(self) -> int:
        return 1

    def get_width(self) -> int:
        return self._num_zones

    @tries(_MAX_TRIES, WorkflowException)
    def get_zone_colors(self, first_zone=None, last_zone=None):
        if first_zone is not None:
            first_zone = param_16(first_zone)
        if last_zone is not None:
            last_zone = param_16(first_zone)
        return self._impl.get_color_zones(first_zone, last_zone)

    @tries(_MAX_TRIES, WorkflowException)
    def set_zone_colors(self, first_zone, last_zone, color, duration) -> None:
        # Unknown why this happens.
        if not hasattr(self._impl, 'set_zone_color'):
            logging.error(
                'No set_zone_color for light of type', type(self._impl))
        else:
            color = param_color(color)
            first_zone = param_16(first_zone)
            last_zone = param_16(last_zone)
            duration = param_32(duration)
            self._impl.set_zone_color(first_zone, last_zone, color, duration)


class MatrixLight(Light, i_controller.MatrixLight):
    def __init__(self, impl, height=None, width=None):
        super().__init__(impl)
        self._height = height
        self._width = width
        if self._width is None or self._height is None:
            self._get_size()

    @tries(_MAX_TRIES, WorkflowException)
    def _get_size(self) -> None:
        result = self._impl.req_with_resp(GetDeviceChain, StateDeviceChain)
        tile = result.tile_devices[result.start_index]
        self._width = tile.get('width', 0)
        self._height = tile.get('height', 0)

    def get_height(self) -> int:
        return self._height

    def get_width(self) -> int:
        return self._width

    @tries(_MAX_TRIES, WorkflowException)
    def set_matrix(self, matrix, duration=0) -> None:
        payload = {
            "tile_index": 0,
            "length": 1,
            "colors": matrix.get_colors(),
            "duration": param_32(duration),
            "reserved": 0,
            "x": 0,
            "y": 0,
            "width": self._width,
            "height": self._height}
        self._impl.fire_and_forget(SetTileState64, payload, num_repeats=1)

    @tries(_MAX_TRIES, WorkflowException)
    def get_matrix(self) -> ColorMatrix:
        payload = {
            "tile_index": 0,
            "length": 1,
            "reserved": 0,
            "x": 0,
            "y": 0,
            "width": self._width,
            "height": self._height}
        colors = self._impl.req_with_resp(
            GetTileState64, StateTileState64, payload).colors
        return ColorMatrix.new_from_iterable(self._height, self._width, colors)
