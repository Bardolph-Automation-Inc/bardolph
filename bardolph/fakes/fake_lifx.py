import logging

from ..controller import i_controller
from ..lib.injection import bind_instance


class ActivityLog:
    def __init__(self):
        self._actions = []

    def log_call(self, name, params=None):
        # params is a tuple or None.
        self._actions.append((name, params))

    def calls_to(self, name):
        # list of tuples and/or None's.
        return [action[1] for action in self._actions if action[0] == name]

    def get_call_list(self):
        return self._actions

    def clear(self):
        self._actions.clear()


class Light:
    """
    Fake lifxlan.light.Light which implements the methods that are actually
    called by the tests.
    """
    def __init__(self, name, group, location, color=None, multizone=False):
        self._name = name
        self._group = group
        self._location = location
        self._multizone = multizone
        self._power = 12345
        self._color = color if color is not None else [-1] * 4
        self._color_zones = [self._color] * 16
        self._set_color = None
        self._activity = ActivityLog()
        self._quiet = False

    def __repr__(self):
        fmt = 'fake_lifx.Light(_name: "{}", _group: "{}", _location: "{}", '
        fmt += '_power: {}, _color: {})'
        return fmt.format(
            self._name, self._group, self._location, self._power, self._color)

    def get_color(self):
        self._activity.log_call('get_color')
        if not self._quiet:
            logging.info(
                'Get color from "{}": {}'.format(self._name, self._color))
        return self._color

    def set_color(self, color, duration=0, _=False):
        self._color = color
        self._set_color = color
        self._activity.log_call('set_color', (color, duration))
        if not self._quiet:
            logging.info(
                'Set color for "{}": {}, {}'.format(
                    self._name, color, duration))

    def set_zone_color(self, start_index, end_index, color, duration, _=False):
        for zone in range(start_index, end_index):
            self._color_zones[zone] = color
        self._activity.log_call(
            'set_zone_color', (start_index, end_index, color, duration))
        logging.info('Set color for "{}" zones {} - {}: {}, {}'.format(
            self._name, start_index, end_index, color, duration))

    def supports_multizone(self):
        return self._multizone

    def set_return_color(self, color):
        self._color = color

    def set_power(self, power, duration, _=False):
        self._power = power
        self._activity.log_call('set_power', (power, duration))
        logging.info(
            'Set power for "{}": {}, {}'.format(self._name, power, duration))

    def get_power(self):
        self._activity.log_call('get_power')
        return self._power

    def get_color_zones(self, start_index=0, end_index=16):
        self._activity.log_call('get_color_zones', (start_index, end_index))
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

    def call_list(self):
        return self._activity.get_call_list()


class Lifx(i_controller.Lifx):
    inits = []

    def __init__(self):
        self.init_from(Lifx.inits)

    def init_from(self, inits):
        self._lights = [
            Light(init[0], init[1], init[2], init[3],
                  None if len(init) < 5 else init[4])
            for init in inits
        ]

    def get_lights(self):
        return self._lights

    def set_color_all_lights(self, color, duration):
        logging.info("Color (all) {}, {}".format(color, duration))

    def set_power_all_lights(self, power_level, duration):
        logging.info("Power (all) {} {}".format(power_level, duration))


def configure():
    # light name, group, location
    Lifx.inits = [
        ('Table', 'Furniture', 'Home', [1, 2, 3, 4], False),
        ('Top', 'Pole', 'Home', [10, 20, 30, 40], False),
        ('Middle', 'Pole', 'Home', [100, 200, 300, 400], False),
        ('Bottom', 'Pole', 'Home', [1000, 2000, 3000, 4000], False),
        ('Chair', 'Furniture', 'Home',
            [10000, 20000, 30000, 4004], False),
        ('Strip', 'Furniture', 'Home', [4, 3, 2, 1], True)
    ]
    bind_instance(Lifx()).to(i_controller.Lifx)
