#!/usr/bin/env python

import unittest

from bardolph.controller import light_set
from bardolph.fakes import fake_light_api
from bardolph.lib import injection, settings


class LightSetTest(unittest.TestCase):
    def setUp(self):
        injection.configure()
        settings.using({
            'log_to_console': True,
            'single_light_discover': True,
            'use_fakes': True
        }).configure()

        self._group0 = 'Group 0'
        self._group1 = 'Group 1'
        self._group2 = 'Group 2'

        self._loc0 = 'Location 0'
        self._loc1 = 'Location 1'
        self._loc2 = 'Location 2'

        self._light0 = 'Light 0'
        self._light1 = 'Light 1'
        self._light2 = 'Light 2'
        self._light3 = 'Light 3'

        self._color = [1, 2, 3, 4]
        fake_light_api.using([
            (self._light0, self._group0, self._loc0, self._color),
            (self._light1, self._group0, self._loc1, self._color),
            (self._light2, self._group1, self._loc0, self._color),
            (self._light3, self._group1, self._loc1, self._color)
        ]).configure()
        light_set.configure()

    def _assert_names_match(self, name_list, *names):
        self.assertEqual(len(name_list), len(names), "List lengths unequal.")
        for name in names:
            self.assertTrue(name in name_list,
                            '"{}" not found in group/location'.format(name))

    def test_discover(self):
        tested_set = light_set.LightSet()
        tested_set.discover()

        self.assertEqual(len(tested_set.get_light_names()), 4)
        self.assertEqual(len(tested_set.get_group_names()), 2)
        self.assertEqual(len(tested_set.get_location_names()), 2)
        for light_name in (
                self._light0, self._light1, self._light2, self._light3):
            light = tested_set.get_light(light_name)
            self.assertIsNotNone(light)
            self.assertEqual(light.get_name(), light_name)

        lights = tested_set.get_group_lights(self._group0)
        self._assert_names_match(lights, self._light0, self._light1)
        lights = tested_set.get_group_lights(self._group1)
        self._assert_names_match(lights, self._light2, self._light3)

        lights = tested_set.get_location_lights(self._loc0)
        self._assert_names_match(lights, self._light0, self._light2)
        lights = tested_set.get_location_lights(self._loc1)
        self._assert_names_match(lights, self._light1, self._light3)

    def test_refresh(self):
        tested_set = light_set.LightSet()
        tested_set.discover()

        fake_light_api.using([
            (self._light0, self._group0, self._loc0, self._color),
            (self._light1, self._group0, self._loc1, self._color),
            (self._light2, self._group0, self._loc1, self._color),
            (self._light3, self._group2, self._loc0, self._color)
        ]).configure()
        tested_set.refresh()

        self.assertEqual(len(tested_set.get_light_names()), 4)
        self.assertEqual(len(tested_set.get_group_names()), 2)
        self.assertEqual(len(tested_set.get_location_names()), 2)

        names = tested_set.get_group_lights(self._group0)
        self._assert_names_match(
            names, self._light0, self._light1, self._light2)
        self.assertIsNone(tested_set.get_group_lights(self._group1))
        names = tested_set.get_group_lights(self._group2)
        self._assert_names_match(names, self._light3)

        names = tested_set.get_location_lights(self._loc0)
        self._assert_names_match(names, self._light0, self._light3)
        names = tested_set.get_location_lights(self._loc1)
        self._assert_names_match(names, self._light1, self._light2)

    def test_garbage_collect(self):
        tested_set = light_set.LightSet()
        tested_set.discover()
        light = tested_set.get_light(self._light0)
        light._age = 1000 * 1000
        tested_set._garbage_collect()

        self.assertEqual(len(tested_set.get_light_names()), 3)
        self.assertEqual(len(tested_set.get_group_names()), 2)
        self.assertEqual(len(tested_set.get_location_names()), 2)

        names = tested_set.get_group_lights(self._group0)
        self._assert_names_match(names, self._light1)
        names = tested_set.get_group_lights(self._group1)
        self._assert_names_match(names, self._light2, self._light3)

        names = tested_set.get_location_lights(self._loc0)
        self._assert_names_match(names, self._light2)
        names = tested_set.get_location_lights(self._loc1)
        self._assert_names_match(names, self._light1, self._light3)


if __name__ == '__main__':
    unittest.main()
