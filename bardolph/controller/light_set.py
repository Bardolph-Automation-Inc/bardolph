#!/usr/bin/env python

import logging
import threading
import time

import lifxlan

from ..lib.color import average_color
from ..lib.injection import bind_instance, inject
from ..lib.i_lib import Settings

from . import i_controller 


class LightSet(i_controller.LightSet):
    the_instance = None

    def __init__(self):
        self.light_dict = {}
        self.groups = {}
        self.locations = {}
        self.num_successful_discovers = 0
        self.num_failed_discovers = 0
        self.last_discover = None
   
    def __len__(self):
        return self.get_count()

    @classmethod
    def configure(cls):
        if LightSet.the_instance == None:
            LightSet.the_instance = LightSet()

    @classmethod
    def get_instance(cls):
        return LightSet.the_instance
    
    @inject(Settings)
    def discover(self, settings):
        expected = settings.get_value('default_num_lights', 0)       
        new_dict = {}
        try:
            if expected == 0:
                light_list = self.broadcast_state_service()
            else:
                light_list = self.broadcast_state_service(expected)
            for light in light_list:
                new_dict[light.get_label()] = light  
            self.light_dict = new_dict
            self.last_discover = time.localtime()
            
            self.groups = self.build_set(
                light_list, lifxlan.device.Device.get_group)
            self.locations = self.build_set(
                light_list, lifxlan.device.Device.get_location)
        except lifxlan.errors.WorkflowException as ex:
            logging.error("Error during discovery {}".format(ex))
            return False
              
        actual = len(self.light_dict) 
        if actual < expected:
            logging.warning(
                "Expected {} devices, found {}".format(expected, actual))
            return False
        else:
            return True
        
    def broadcast_state_service(self, num_expected):
        lifx = lifxlan.LifxLAN(num_expected)
        responses = lifx.broadcast_with_resp(
            lifxlan.msgtypes.GetService, lifxlan.msgtypes.StateService,
            max_attempts = 5)

        light_list = list()
        for response in responses:
            new_light = lifxlan.light.Light(
                response.target_addr, response.ip_addr, response.service,
                response.port, lifx.source_id, lifx.verbose)
            light_list.append(new_light)
        
        return light_list
       
    def build_set(self, light_list, fn):
        # Produces a dictionary keyed on group or location name, pointing to
        # a list of (lifxlan) light objects.
        sets = {}
        for light in light_list:
            set_name = fn(light)
            if set_name in sets:
                sets[set_name].append(light)
            else:
                sets[set_name] = [light]
        return sets

    def get_light_names(self):
        """ list of strings """
        return self.light_dict.keys()
        
    def get_light(self, name):
        """ returns an instance of lifxlan.Light, or None if it's not there """ 
        return self.light_dict.get(name, None)
    
    def get_group_names(self):
        """ list of strings """
        return self.groups.keys()
        
    def get_group(self, name):
        """ list of Lights """ 
        return self.groups.get(name, [])
    
    def get_location_names(self):
        """ list of strings """
        return self.locations.keys()
        
    def get_location(self, name):
        """ list of Lights. """ 
        return self.locations.get(name, [])
    
    def get_all_lights(self):
        """ list of Lights. """
        return self.light_dict.values()
    
    def get_count(self):
        return len(self.light_dict)
    
    def get_last_discover(self):
        return self.last_discover
    
    def get_successful_discovers(self):
        return self.num_successful_discovers
    
    def get_failed_discovers(self):
        return self.num_failed_discovers
    
    @inject(Settings)
    def set_color(self, color, duration, settings):
        num_expected = settings.get_value('default_num_lights')
        lifx = lifxlan.LifxLAN(num_expected)
        lifx.set_color_all_lights(color, duration, True)
        return True
    
    def get_color(self):
        """ Returns arithmetic mean of each color setting. """
        return average_color(
            list(self.get_lifxlan().get_color_all_lights().values()))
    
    def set_power(self, power_level, duration):
        self.get_lifxlan().set_power_all_lights(power_level, duration, True)
        return True
    
    def get_power(self):
        """ Returns True if at least one bulb is on. """
        return self.any_power(
            self.get_lifxlan().get_power_all_lights())
            
    def any_power(self, state_dict):
        for state in state_dict.values():
            if state:
                return True
        return False
    
    @inject(Settings)
    def get_lifxlan(self, settings):
        num_expected = settings.get_value('default_num_lights')
        return lifxlan.LifxLAN(num_expected)

def start_light_refresh():
    logging.info("Starting refresh thread.")
    threading.Thread(
        target=light_refresh, name='rediscover', daemon=True).start()


@inject(Settings)
def light_refresh(settings):
    logging.debug("will start discover loop")
    
    success_sleep_time = settings.get_value('refresh_sleep_time')
    failure_sleep_time = settings.get_value('failure_sleep_time')
    complete_success = False
    
    while True:
        logging.info("Discovering light_set.")
        lights = LightSet.get_instance()
        try:
            complete_success = lights.discover()
            lights.num_successful_discovers += 1
        except lifxlan.errors.WorkflowException as ex:
            logging.warning("Error during discovery {}".format(ex))
            lights.num_failed_discovers += 1
        
        time.sleep(
            success_sleep_time if complete_success else failure_sleep_time)
        
    logging.info("Exiting light_refresh()")
    

@inject(Settings)
def configure(settings):
    LightSet.configure()
    lights = LightSet.get_instance()
    bind_instance(lights).to(i_controller.LightSet)
    lights.discover()
    
    single = settings.get_value('single_light_discover')
    logging.debug("single_light_discover: {}".format(single))
    if (not single):
        start_light_refresh()
