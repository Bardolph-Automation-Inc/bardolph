import logging
import time

from lifxlan.errors import WorkflowException
from lifxlan.msgtypes import GetTileState64, SetTileState64, StateTileState64

from bardolph.controller import i_controller, light
from bardolph.controller.candle_color_matrix import CandleColorMatrix
from bardolph.lib.param_helper import param_16, param_32, param_color
from bardolph.lib.retry import tries

_MAX_TRIES = 3


class Light(light.Light):
    def __init__(self, impl):
        super().__init__(
            impl.get_label(), impl.get_group(), impl.get_location())
        self._impl = impl

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


class CandleLight(Light, i_controller.MatrixLight):
    """
    The size of the matrix is fixed at 5x6. There is no control over what area
    is affected; only the entire matrix can be set or retrieved.

    The "x", "y", and "tile_index" parameters in the payload are intended only
    for so-called tile devices and have no purpose in this context.
    """

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
            "width": 5,
            "height": 6}
        self._impl.fire_and_forget(SetTileState64, payload, num_repeats=1)

    @tries(_MAX_TRIES, WorkflowException)
    def get_matrix(self) -> CandleColorMatrix:
        payload = {
            "tile_index": 0,
            "length": 1,
            "reserved": 0,
            "x": 0,
            "y": 0,
            "width": 5,
            "height": 6}
        colors = self._impl.req_with_resp(
            GetTileState64, StateTileState64, payload).colors
        return CandleColorMatrix.new_from_iterable(colors)
