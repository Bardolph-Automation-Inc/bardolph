#!/usr/bin/env python

import unittest

from bardolph.controller import i_controller
from bardolph.controller import light_set
from bardolph.fakes import fake_lifx
from bardolph.lib import injection, settings

class LightSetTest(unittest.TestCase):      
    def setUp(self):
        injection.configure()
        settings.use_base({
            'failure_sleep_time': 300,
            'log_to_console': True,
            'refresh_sleep_time': 300,
            'single_light_discover': True,
            'use_fakes': True
        }).configure()        
        fake_lifx.configure()
        light_set.configure()
        
        self._group0 = 'Group 0'
        self._group1 = 'Group 1'
        self._group2 = 'Group 2'
        
        self._location0 = 'Location 0'
        self._location1 = 'Location 1'
        self._location2 = 'Location 2'
        
        self._light0 = 'Light 0'
        self._light1 = 'Light 1'
        self._light2 = 'Light 2'
        self._light3 = 'Light 3'
        
        self._color = [1, 2, 3, 4]
        lifx = injection.provide(i_controller.Lifx)
        lifx.init_from([
            (self._light0, self._group0, self._location0, self._color, False),
            (self._light1, self._group0, self._location1, self._color, False),
            (self._light2, self._group1, self._location0, self._color, False),
            (self._light3, self._group1, self._location1, self._color, False)
        ])
        
    def _assert_names_equal(self, light_set, *names):
        self.assertEqual(len(light_set), len(names))
        for name in names:
            found = False
            for light in light_set:
                if name == light.name:
                    found = True
                    break
            self.assertTrue(
                found, '"{}" not found in group/location'.format(name))

    def test_discover(self):
        tested_set = light_set.LightSet()
        tested_set.discover()
        
        self.assertEqual(len(tested_set.light_names), 4)
        self.assertEqual(len(tested_set.group_names), 2)
        self.assertEqual(len(tested_set.location_names), 2)
        for light_name in (
                self._light0, self._light1, self._light2, self._light3):
            light = tested_set.get_light(light_name)
            self.assertIsNotNone(light)
            self.assertEqual(light.name, light_name)

        group = tested_set.get_group(self._group0)
        self._assert_names_equal(group, self._light0, self._light1)
        group = tested_set.get_group(self._group1)
        self._assert_names_equal(group, self._light2, self._light3)

        location = tested_set.get_location(self._location0)
        self._assert_names_equal(location, self._light0, self._light2)        
        location = tested_set.get_location(self._location1)
        self._assert_names_equal(location, self._light1, self._light3)        

    def test_refresh(self):
        tested_set = light_set.LightSet()
        tested_set.discover()
        
        lifx = injection.provide(i_controller.Lifx)
        lifx.init_from([
            (self._light0, self._group0, self._location0, self._color, False),
            (self._light1, self._group0, self._location1, self._color, False),
            (self._light2, self._group0, self._location1, self._color, False),
            (self._light3, self._group2, self._location0, self._color, False)
        ])
        
        tested_set.refresh()
        self.assertEqual(len(tested_set.light_names), 4)
        self.assertEqual(len(tested_set.group_names), 2)
        self.assertEqual(len(tested_set.location_names), 2)
                        
        group = tested_set.get_group(self._group0)
        self._assert_names_equal(
            group, self._light0, self._light1, self._light2)      
        self.assertIsNone(tested_set.get_group(self._group1))
        group = tested_set.get_group(self._group2)
        self._assert_names_equal(group, self._light3)

        location = tested_set.get_location(self._location0)
        self._assert_names_equal(location, self._light0, self._light3)        
        location = tested_set.get_location(self._location1)
        self._assert_names_equal(location, self._light1, self._light2)        

    def test_garbage_collect(self):
        tested_set = light_set.LightSet()
        tested_set.discover()
        light = tested_set.get_light(self._light0)
        light._birth = 0
        tested_set._garbage_collect()
        
        self.assertEqual(len(tested_set.light_names), 3)
        self.assertEqual(len(tested_set.group_names), 2)
        self.assertEqual(len(tested_set.location_names), 2)
                
        group = tested_set.get_group(self._group0)
        self._assert_names_equal(group, self._light1)
        group = tested_set.get_group(self._group1)
        self._assert_names_equal(group, self._light2, self._light3)
        
        location = tested_set.get_location(self._location0)
        self._assert_names_equal(location, self._light2)
        location = tested_set.get_location(self._location1)
        self._assert_names_equal(location, self._light1, self._light3)

if __name__ == '__main__':
    unittest.main()
