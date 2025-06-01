import logging

from bardolph.controller import i_controller
from bardolph.controller.color_matrix import ColorMatrix
from bardolph.fakes.activity_monitor import Action, ActivityMonitor
from bardolph.lib.param_helper import (param_16, param_32, param_bool,
                                       param_color)


class Light(i_controller.Light):
    def __init__(self, name, group, location):
        super().__init__()
        self._age = 0.0
        self._name = name
        self._group = group
        self._location = location
        self._height = 1
        self._width = 1
        self._is_color = True
        self._power = 0
        self._color = [0, 0, 0, 0]

        self._set_color = None
        self._quiet = False
        self._monitor = ActivityMonitor()

    def __repr__(self):
        fmt = 'fake_light.Light(_name: "{}", _group: "{}", _location: "{}", '
        fmt += '_power: {}, _color: {})'
        return fmt.format(
            self._name, self._group, self._location, self._power, self._color)

    def get_name(self) -> str:
        return self._name

    def get_group(self) -> str:
        return self._group

    def get_location(self) -> str:
        return self._location

    def set_height(self, height: int) -> None:
        self._height = height

    def get_height(self) -> int:
        return self._height

    def set_width(self, width: int) -> None:
        self._width = width

    def get_width(self) -> int:
        return self._width

    def is_color(self) -> bool:
        return self._is_color

    def set_is_color(self, is_color: bool) -> None:
        self._is_color = is_color

    def get_age(self) -> float:
        return float(self._age)

    def get_color(self):
        self._monitor.log_call(Action.GET_COLOR, self._color)
        logging.info(
            'Get color from "{}": {}'.format(self._name, self._color))
        return self._color

    def set_color(self, color, duration=0):
        color = param_color(color)
        self._color = color
        self._set_color = color
        duration = param_32(duration)
        self._monitor.log_call(Action.SET_COLOR, color, duration)
        logging.info('Set color for "{}": {}, {}'.format(
            self._name, self._color, duration))

    def get_power(self):
        self._monitor.log_call(Action.GET_POWER)
        return self._power

    def set_power(self, power, duration):
        power = param_bool(power)
        duration = param_32(duration)
        self._monitor.log_call(Action.SET_POWER, power, duration)

    def quietly(self):
        self._monitor.quietly()
        return self

    def get_call_list(self):
        return self._monitor.get_call_list()

    def was_set(self, color) -> bool:
        return self._set_color == color


class MultizoneLight(Light, i_controller.MultizoneLight):
    def __init__(self, name, group, location, num_zones=16):
        super().__init__(name, group, location)
        self._zone_colors = [[0, 0, 0, 0] for _ in range(0, num_zones)]
        self._width = num_zones

    def get_zone_colors(self, start_index=0, end_index=16):
        start_index = param_16(start_index)
        end_index = param_16(end_index)
        self._monitor.log_call(Action.GET_ZONE_COLOR, start_index, end_index)
        return self._zone_colors[start_index: end_index]

    def set_zone_colors(self, start_index, end_index, color, duration):
        start_index = param_16(start_index)
        end_index = param_16(end_index)
        color = param_color(color)
        duration = param_32(duration)
        self._monitor.log_call(
            Action.SET_ZONE_COLOR, start_index, end_index, color, duration)
        logging.info(
            'Set colors for "{}" zones {} - {}: {}, {}'.format(
                self._name, start_index, end_index - 1, color, duration))
        for zone in range(start_index, end_index):
            self._zone_colors[zone] = color.copy()


class MatrixLight(Light, i_controller.MatrixLight):
    def __init__(self, name, group, location, height=6, width=5):
        super().__init__(name, group, location)
        self._height = height
        self._width = width
        def all_zero():
            while True:
                yield [0, 0, 0, 0]
        self._matrix = ColorMatrix.new_from_iterable(height, width, all_zero())

    def set_matrix(self, matrix, duration=0) -> None:
        logging.info(
            'Set matrix for "{}", duration {}'.format(self._name, duration))
        logging.info('\n' + str(matrix))
        self._matrix.set_from_matrix(matrix)
        self._monitor.log_call(Action.SET_MATRIX, matrix, duration)

    def get_matrix(self):
        self._monitor.log_call(Action.GET_MATRIX)
        return self._matrix
