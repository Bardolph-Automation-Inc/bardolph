#!/usr/bin/env python

import unittest

from bardolph.controller import units
from bardolph.vm.vm_codes import Register

class UnitsTest(unittest.TestCase):
    def _assert_colors_equal(self, color0, color1):
        places = 2
        for i in range(0, 4):
            self.assertAlmostEqual(color0[i], color1[i], places)

    def _assert_raw_equal(self, color0, color1):
        for i in range(0, 4):
            self.assertEqual(round(color0[i]), round(color1[i]))

    def test_conversions(self):
        raw_color = units.logical_to_raw([120.0, 33.0, 67, 4000])
        self._assert_raw_equal(raw_color, [21845, 21627, 43908, 4000])

        logical_color = units.raw_to_logical([21845, 21627, 43908, 4000])
        self._assert_colors_equal(logical_color, [120.0, 33.0, 67.0, 4000])

        rgb_color = units.logical_to_rgb([120.0, 33.0, 67, 4000])
        self._assert_colors_equal(rgb_color, [44.889, 67.0, 44.889, 4000])

        logical_color = units.rgb_to_logical([0, 100, 0, 4000])
        self._assert_colors_equal(logical_color, [120.0, 100.0, 100.0, 4000])

        raw_color = units.rgb_to_raw([100.0, 50.0, 25.0, 4000])
        self._assert_colors_equal(raw_color, [3640.83, 49151.25, 65535.0, 4000])

        rgb_color = units.raw_to_rgb([21845, 21627, 43908, 4000])
        self._assert_colors_equal(rgb_color, [44.889, 67.0, 44.889, 4000])

if __name__ == '__main__':
    unittest.main()
