#!/usr/bin/env python

from datetime import datetime
import logging

from bardolph.lib import injection
from bardolph.controller import i_controller


class Light:
    def __init__(self, name, group, location, color):
        self.name = name
        self.group = group
        self.location = location
        self.power = 12345
        self.color = color if color is not None else [0, 0, 0, 0]
        
    def __repr__(self):
        s = 'name: "{}", group: "{}", location: "{}", power: {}, '.format(
            self.name, self.group, self.location, self.power)
        s += 'color: {}'.format(self.color)
        return s
        
    def get_color(self):
        logging.info('Get color "{}" {}'.format(self.name, self.color))
        return self.color

    def set_color(self, color, duration = 0, _ = False):
        self.color = color
        logging.info('Color "{}" {}, {}'.format(self.name, color, duration))
        
    def set_return_color(self, color):
        self.color = color
        
    def set_power(self, power, duration):
        self.power = power
        logging.info('Power "{}", {}, {}'.format(self.name, power, duration))
        
    def get_power(self):
        return self.power
    
    def set_return_power(self, power):
        self.power = power
        
    def get_label(self):
        return self.name
    
    def get_location(self):
        return self.location
    
    def get_group(self):
        return self.group
  

class LightSet:
    def __init__(self):
        self.clear_lights()
        self.discover()
    
    def clear_lights(self):
        self.lights = {}
        self.groups = {}
        self.locations = {} 
        
    def discover(self):
        if len(self.lights) == 0:
            self.add_light('Table', 'Furniture', 'Home', [1, 2, 3, 4])
            self.add_light('Top',  'Pole', 'Home', [10, 20, 30, 40])
            self.add_light('Middle', 'Pole', 'Home', [100, 200, 300, 400])
            self.add_light(
                'Bottom', 'Pole', 'Home', [1000, 2000, 3000, 4000])
            self.add_light(
                'Chair', 'Furniture', 'Home', [10000, 20000, 30000, 40000])
     
    def add_light(self, name, group, location, color=None):
        new_light = Light(name, group, location, color)
        self.lights[name] = new_light
        if group is not None:
            if group in self.groups:
                self.groups[group].append(new_light)
            else:
                self.groups[group] = [new_light] 
        if location is not None:
            if location in self.locations:
                self.locations[location].append(new_light)
            else:
                self.locations[location] = [new_light]
    
    def get_light_names(self): 
        return self.lights.keys()
    
    def get_light(self, name):
        if not name in self.lights:
            logging.error("Light >\"{}\"< not in fake lights".format(name))
            return None
        return self.lights[name]
    
    def get_all_lights(self):
        return list(self.lights.values());

    def get_group_names(self):
        return self.groups.keys()
    
    def get_group(self, name):
        return self.groups.get(name, {})
    
    def get_location_names(self):
        return self.locations.keys()
    
    def get_location(self, name):
        return self.locations.get(name, {})

    def get_last_discover(self):
        return datetime.now()
    
    def get_successful_discovers(self):
        return 100
    
    def get_failed_discovers(self):
        return 10
    
    def set_color(self, color, duration):
        logging.info("Color (all) {}, {}".format(color, duration))

    def set_power(self, power_level, duration):
        logging.info("Power (all) {} {}".format(power_level, duration))


def configure():
    injection.bind_instance(LightSet()).to(i_controller.LightSet)
