#!/usr/bin/env python

import unittest
from unittest.mock import patch

from bardolph.controller.light_set import LightSet
from bardolph.lib import injection, settings

class LightSetTest(unittest.TestCase):
    def get_color_all_lights(self):
        return {
            "test1": [1, 2, 3, 4],
            "test2": [3, 6, 9, 12]
        }
        
    def get_power_all_lights(self):
        return self.power
        
    def setUp(self):
        injection.configure()
        settings.using_base({'default_num_lights': 5}).configure()
        self.power1 = {
            "test1": 0,
            "test2": 65535
        }
        self.power2 = {
            "test1": 0,
            "test2": 0
        }    
    
    @patch('lifxlan.LifxLAN') 
    def test_get(self, lifxlan):
        lifxlan.return_value = self
        light_set = LightSet()
        
        expected_color = [2, 4, 6, 8]
        self.assertListEqual(light_set.get_color(), expected_color)
        
        self.power = self.power1
        self.assertTrue(light_set.get_power())
        self.power = self.power2
        self.assertFalse(light_set.get_power())


if __name__ == '__main__':
    unittest.main()
