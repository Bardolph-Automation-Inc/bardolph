#!/usr/bin/env python

from datetime import datetime
import logging

from bardolph.lib import injection
from bardolph.controller import i_controller


class Light:
    def __init__(self, name, group, location, color, multizone):
        self._name = name
        self._group = group
        self._location = location
        self._multizone = multizone
        self._power = 12345
        self._color = color if color is not None else [0, 0, 0, 0]

    def __repr__(self):
        rep = '_name: "{}", _group: "{}", _location: "{}", _power: {}, '.format(
            self._name, self._group, self._location, self._power)
        rep += '_color: {}'.format(self._color)
        return rep

    def get_color(self):
        logging.info('Get _color "{}" {}'.format(self._name, self._color))
        return self._color

    def set_color(self, color, duration=0, _=False):
        self._color = color
        logging.info('Color "{}" {}, {}'.format(self._name, color, duration))

    def set_zone_color(self, start_index, end_index, color, duration, _=False):
        logging.info('Multizone color "{}" {}, {}, {}, {}'.format(
            self._name, start_index, end_index, color, duration))

    def supports_multizone(self):
        return self._multizone
    
    def set_return_color(self, color):
        self._color = color

    def set_power(self, power, duration):
        self._power = power
        logging.info('Power "{}", {}, {}'.format(self._name, power, duration))

    def get_power(self):
        return self._power

    def get_color_zones(self, start=0, end=7):
        return [[self._color]] * (end - start)

    def set_return_power(self, power):
        self._power = power

    def get_label(self):
        return self._name

    def get_location(self):
        return self._location

    def get_group(self):
        return self._group


class LightSet:
    def __init__(self):
        self.clear_lights()
        self.discover()

    def clear_lights(self):
        self._lights = {}
        self._groups = {}
        self._locations = {}

    def discover(self):
        if len(self._lights) == 0:
            self.add_light('Table', 'Furniture', 'Home', [1, 2, 3, 4])
            self.add_light('Top', 'Pole', 'Home', [10, 20, 30, 40])
            self.add_light('Middle', 'Pole', 'Home', [100, 200, 300, 400])
            self.add_light(
                'Bottom', 'Pole', 'Home', [1000, 2000, 3000, 4000])
            self.add_light(
                'Chair', 'Furniture', 'Home', [10000, 20000, 30000, 40000])
            self.add_light('Strip', 'Furniture', 'Home', [4, 3, 2, 1], True)

    def add_light(self, name, group, location, color=None, multizone=False):
        new_light = Light(name, group, location, color, multizone)
        self._lights[name] = new_light
        if group is not None:
            if group in self._groups:
                self._groups[group].append(new_light)
            else:
                self._groups[group] = [new_light]
        if location is not None:
            if location in self._locations:
                self._locations[location].append(new_light)
            else:
                self._locations[location] = [new_light]

    @property
    def light_names(self):
        return self._lights.keys()

    @property
    def lights(self):
        return list(self._lights.values())

    @property
    def group_names(self):
        return self._groups.keys()

    @property
    def location_names(self):
        return self._locations.keys()
    
    @property
    def count(self):
        return len(self._lights)

    @property
    def last_discover(self):
        return datetime.now()

    @property
    def successful_discovers(self):
        return 100

    @property
    def failed_discovers(self):
        return 10

    def get_light(self, name):
        if not name in self._lights:
            logging.error("Light >\"{}\"< not in fake _lights".format(name))
            return None
        return self._lights[name]

    def get_group(self, name):
        return self._groups.get(name, {})

    def get_location(self, name):
        return self._locations.get(name, {})

    def set_color(self, color, duration):
        logging.info("Color (all) {}, {}".format(color, duration))
        
    def get_color(self):
        return [1, 2, 3, 4]

    def set_power(self, power_level, duration):
        logging.info("Power (all) {} {}".format(power_level, duration))

    def get_power(self):
        return True

def configure():
    injection.bind_instance(LightSet()).to(i_controller.LightSet)
