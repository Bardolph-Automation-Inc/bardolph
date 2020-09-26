import logging
from enum import Enum, auto

from bardolph.controller import i_controller
from bardolph.lib.injection import bind_instance


class Action(Enum):
    GET_COLOR = auto()
    GET_ZONE_COLOR = auto()
    GET_POWER = auto()
    SET_COLOR = auto()
    SET_POWER = auto()
    SET_ZONE_COLOR = auto()


class ActivityMonitor:
    def __init__(self):
        self._actions = []
        self._quiet = False

    def log_call(self, name, params=None):
        # params is a tuple or None.
        if not self._quiet:
            self._actions.append((name, params))
        else:
            self._quiet = False

    def log_output(self, msg):
        logging.info(msg)

    def calls_to(self, name):
        # list of tuples and/or None's.
        return [action[1] for action in self._actions if action[0] == name]

    def get_call_list(self):
        return self._actions

    def clear(self):
        self._actions.clear()

    def quietly(self):
        self._quiet = True
        return self


class Light(ActivityMonitor):
    """
    Fake lifxlan.light.Light which implements the methods that are actually
    called by the tests.
    """
    def __init__(self, name, group, location, color=None, multizone=False):
        super().__init__()
        self._name = name
        self._group = group
        self._location = location
        self._multizone = multizone
        self._power = 12345
        self._color = color or [-1] * 4
        self._color_zones = [self._color] * 16
        self._set_color = None
        self._quiet = False

    def __repr__(self):
        fmt = 'fake_lifx.Light(_name: "{}", _group: "{}", _location: "{}", '
        fmt += '_power: {}, _color: {})'
        return fmt.format(
            self._name, self._group, self._location, self._power, self._color)

    def get_color(self):
        self.log_call(Action.GET_COLOR, self._color)
        logging.info(
            'Get color from "{}": {}'.format(self._name, self._color))
        return self._color

    def set_color(self, color, duration=0, _=False):
        self._color = color.copy()
        self._set_color = self._color
        self.log_call(Action.SET_COLOR, (color, duration))
        logging.info(
            'Set color for "{}": {}, {}'.format(
                self._name, color, duration))

    def set_zone_color(self, start_index, end_index, color, duration, _=False):
        for zone in range(start_index, end_index):
            self._color_zones[zone] = color.copy()
        self.log_call(
            Action.SET_ZONE_COLOR, (start_index, end_index, color, duration))
        logging.info('Set color for "{}" zones {} - {}: {}, {}'.format(
            self._name, start_index, end_index, color, duration))

    def supports_multizone(self):
        return self._multizone

    def set_power(self, power, duration, _=False):
        self._power = power
        self.log_call(Action.SET_POWER, (power, duration))
        logging.info(
            'Set power for "{}": {}, {}'.format(self._name, power, duration))

    def get_power(self):
        self.log_call(Action.GET_POWER)
        return self._power

    def get_color_zones(self, start_index=0, end_index=16):
        self.log_call(Action.GET_ZONE_COLOR, (start_index, end_index))
        logging.info('Get color from "{}" zones {} - {}'.format(
                        self._name, start_index, end_index))
        return self._color_zones[start_index : end_index]

    def get_label(self):
        return self._name

    def get_location(self):
        return self._location

    def get_group(self):
        return self._group

    def was_set(self, color):
        return self._set_color == color


class Lifx(i_controller.Lifx, ActivityMonitor):
    _inits = []

    def __init__(self):
        ActivityMonitor.__init__(self)
        self._lights = []
        for init in self._inits:
            self._lights.append(Light(*init))

    def get_lights(self):
        return self._lights

    def set_color_all_lights(self, color, duration):
        self.log_call(Action.SET_COLOR, (color, duration))
        logging.info("Color (all) {}, {}".format(color, duration))
        for light in self.get_lights():
            light.quietly().set_color(color, duration)

    def set_power_all_lights(self, power_level, duration):
        self.log_call(Action.SET_POWER, (power_level, duration))
        logging.info("Power (all) {} {}".format(power_level, duration))
        for light in self.get_lights():
            light.quietly().set_power(power_level, duration)


class _Reinit:
    def configure(self):
        bind_instance(Lifx()).to(i_controller.Lifx)


def configure():
    using_large_set().configure()


def using(inits):
    Lifx._inits = inits.copy()
    return _Reinit()


def using_large_set():
    # light name, group, location
    Lifx._inits = [
        ('Table', 'Furniture', 'Home', [1, 2, 3, 4], False),
        ('Top', 'Pole', 'Home', [10, 20, 30, 40], False),
        ('Middle', 'Pole', 'Home', [100, 200, 300, 400], False),
        ('Bottom', 'Pole', 'Home', [1000, 2000, 3000, 4000], False),
        ('Chair', 'Furniture', 'Home',
            [10000, 20000, 30000, 4004], False),
        ('Strip', 'Furniture', 'Home', [4, 3, 2, 1], True)
    ].copy()
    return _Reinit()


def using_small_set():
    color = [1, 2, 3, 4]
    Lifx._inits = [
        ('light_1', 'x', 'y', color, False),
        ('light_2', 'group', 'loc', color, False),
        ('light_0', 'group', 'loc', color, False)
    ].copy()
    return _Reinit()
