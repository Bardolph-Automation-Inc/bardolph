import logging

from ..controller import i_controller
from ..lib.injection import bind_instance


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
        self._set_color = None

    def __repr__(self):
        rep = '_name: "{}", _group: "{}", _location: "{}", _power: {}, '.format(
            self._name, self._group, self._location, self._power)
        rep += '_color: {}'.format(self._color)
        return rep

    def get_color(self):
        logging.info('Get color from "{}": {}'.format(self._name, self._color))
        return self._color

    def set_color(self, color, duration=0, _=False):
        self._color = color
        self._set_color = color
        logging.info(
            'Set color for "{}": {}, {}'.format(self._name, color, duration))

    def set_zone_color(self, start_index, end_index, color, duration, _=False):
        logging.info('Multizone color "{}": {}, {}, {}, {}'.format(
            self._name, start_index, end_index, color, duration))

    def supports_multizone(self):
        return self._multizone
    
    def set_return_color(self, color):
        self._color = color

    def set_power(self, power, duration, _=False):
        self._power = power
        logging.info(
            'Set power for "{}": {}, {}'.format(self._name, power, duration))

    def get_power(self):
        return self._power

    def get_color_zones(self, start=0, end=7):
        if start is None:
            start = 0
        if end is None:
            end = 7
        return [self._color] * (end - start)

    def set_return_power(self, power):
        self._power = power

    def get_label(self):
        return self._name

    def get_location(self):
        return self._location

    def get_group(self):
        return self._group
    
    def was_set(self, color):
        return self._set_color == color


class Lifx(i_controller.Lifx):
    def __init__(self):
        self.init_from(Lifx._inits)
    
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
    Lifx._inits = [
        ('Table', 'Furniture', 'Home', [1, 2, 3, 4], False),
        ('Top', 'Pole', 'Home', [10, 20, 30, 40], False),
        ('Middle', 'Pole', 'Home', [100, 200, 300, 400], False),
        ('Bottom', 'Pole', 'Home', [1000, 2000, 3000, 4000], False),
        ('Chair', 'Furniture', 'Home',
            [10000, 20000, 30000, 4004], False),
        ('Strip', 'Furniture', 'Home', [4, 3, 2, 1], True)
    ]
    bind_instance(Lifx()).to(i_controller.Lifx)
