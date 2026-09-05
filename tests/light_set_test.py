#!/usr/bin/env python

import unittest

from bardolph.controller import light_set
from bardolph.controller.i_controller import LightApi, LightSet
from bardolph.fakes import fake_light_api
from bardolph.lib import injection
from bardolph.lib.injection import inject
from tests import test_module
from tests.threaded_test import ThreadedTest


class LightSetTest(ThreadedTest):
    def setUp(self):
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
        self._light4 = 'Light 4'

        self._color = [1, 2, 3, 4]
        test_module.using((
            (self._light0, self._group0, self._loc0),
            (self._light1, self._group0, self._loc1),
            (self._light2, self._group1, self._loc0),
            (self._light3, self._group1, self._loc1),
            (self._light4, self._group2, self._loc2)
        )).configure()

    def _assert_names_match(self, name_list, *names):
        self.assertEqual(len(name_list), len(names), "List lengths unequal.")
        for name in names:
            self.assertTrue(name in name_list,
                            '"{}" not found in group/location'.format(name))

    @inject(LightSet)
    def test_discover(self, tested_set: LightSet):
        tested_set.discover()

        self.assertEqual(len(tested_set.get_light_names()), 5)
        for light_name in (
                self._light0, self._light1, self._light2, self._light3):
            light = tested_set.get_light(light_name)
            self.assertIsNotNone(light)
            self.assertEqual(light.get_name(), light_name)

        lights = tested_set.get_group_lights(self._group0)
        self._assert_names_match(lights, self._light0, self._light1)
        lights = tested_set.get_group_lights(self._group1)
        self._assert_names_match(lights, self._light2, self._light3)
        lights = tested_set.get_group_lights(self._group2)
        self._assert_names_match(lights, self._light4)

        lights = tested_set.get_location_lights(self._loc0)
        self._assert_names_match(lights, self._light0, self._light2)
        lights = tested_set.get_location_lights(self._loc1)
        self._assert_names_match(lights, self._light1, self._light3)
        lights = tested_set.get_location_lights(self._loc2)
        self._assert_names_match(lights, self._light4)

    @inject(LightSet)
    def test_group_change(self, tested_set: LightSet):
        tested_set.discover()

        tested_set.get_light(self._light2).set_group(self._group0)
        tested_set.get_light(self._light4).set_group(self._group1)

        tested_set.refresh()

        lights = tested_set.get_group_lights(self._group0)
        self._assert_names_match(
            lights, self._light0, self._light1, self._light2)
        lights = tested_set.get_group_lights(self._group1)
        self._assert_names_match(lights, self._light3, self._light4)
        self.assertEqual(len(tested_set.get_group_lights(self._group2)), 0)
        self.assertNotIn(self._group2, tested_set.get_group_names())

    @inject(LightSet)
    def test_location_change(self, tested_set: light_set):
        tested_set.discover()

        tested_set.get_light(self._light2).set_location(self._loc1)
        tested_set.get_light(self._light4).set_location(self._loc0)
        tested_set.refresh()

        lights = tested_set.get_location_lights(self._loc0)
        self._assert_names_match(lights, self._light0, self._light4)
        lights = tested_set.get_location_lights(self._loc1)
        self._assert_names_match(
            lights, self._light1, self._light2, self._light3)
        self.assertEqual(len(tested_set.get_location_lights(self._loc2)), 0)
        self.assertNotIn(self._loc2, tested_set.get_location_names())

    @inject(LightSet)
    def test_garbage_collect(self, tested_set: LightSet):
        tested_set.discover()

        light = tested_set.get_light(self._light4)
        light._age = 1000 * 1000
        tested_set._garbage_collect()

        self.assertEqual(len(tested_set.get_light_names()), 4)
        self.assertEqual(len(tested_set.get_group_names()), 2)
        self.assertEqual(len(tested_set.get_location_names()), 2)

        names = tested_set.get_group_lights(self._group0)
        self._assert_names_match(names, self._light0, self._light1)
        names = tested_set.get_group_lights(self._group1)
        self._assert_names_match(names, self._light2, self._light3)

        names = tested_set.get_location_lights(self._loc0)
        self._assert_names_match(names, self._light0, self._light2)
        names = tested_set.get_location_lights(self._loc1)
        self._assert_names_match(names, self._light1, self._light3)

        self.assertNotIn(self._group2, tested_set.get_group_names())
        self.assertNotIn(self._loc2, tested_set.get_location_names())

    @inject(LightSet)
    def test_added_light(self, tested_set: LightSet):
        tested_set.discover()

        light_api = injection.provide(LightApi)
        builder = fake_light_api.LightBuilder()
        light_api.add_light(builder
            .set_name('new_light')
            .set_group(self._group2)
            .set_location(self._loc2)
            .build())
        tested_set.refresh()

        lights = tested_set.get_group_lights(self._group0)
        self._assert_names_match(lights, self._light0, self._light1)
        lights = tested_set.get_group_lights(self._group1)
        self._assert_names_match(lights, self._light2, self._light3)
        lights = tested_set.get_group_lights(self._group2)
        self._assert_names_match(lights, self._light4, 'new_light')

        lights = tested_set.get_location_lights(self._loc0)
        self._assert_names_match(lights, self._light0, self._light2)
        lights = tested_set.get_location_lights(self._loc1)
        self._assert_names_match(lights, self._light1, self._light3)
        lights = tested_set.get_location_lights(self._loc2)
        self._assert_names_match(lights, self._light4, 'new_light')


if __name__ == '__main__':
    unittest.main()
