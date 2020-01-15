#!/usr/bin/env python

import unittest

from bardolph.controller import units
from bardolph.controller.instruction import Register

class UnitsTest(unittest.TestCase):

    def test_as_raw(self):
        self.assertEqual(units.as_raw(Register.HUE, 360.0), 0)
        self.assertEqual(units.as_raw(Register.HUE, 120.0), 21845)
        self.assertEqual(units.as_raw(Register.SATURATION, 33), 21627)
        self.assertEqual(units.as_raw(Register.BRIGHTNESS, 67), 43908)
        self.assertEqual(units.as_raw(Register.TIME, 1.0), 1000)
        self.assertEqual(
            units.as_raw(Register.DURATION, 2.0), 2000)
        self.assertEqual(units.as_raw(Register.KELVIN, 4000), 4000)

    def test_as_logical(self):
        places = 2
        self.assertAlmostEqual(
            units.as_logical(Register.HUE, 65535), 360.0, places)
        self.assertAlmostEqual(
            units.as_logical(Register.HUE, 21845), 120.0, places)
        self.assertAlmostEqual(
            units.as_logical(Register.SATURATION, 21627), 33.0, places)
        self.assertAlmostEqual(
            units.as_logical(Register.BRIGHTNESS, 43908), 67.0, places)
        self.assertAlmostEqual(
            units.as_logical(Register.KELVIN, 4000), 4000.0, places)

        self.assertAlmostEqual(
            units.as_logical(Register.TIME, 1000.0), 1.0, places)
        self.assertAlmostEqual(
            units.as_logical(Register.DURATION, 2000.0), 2.0, places)

    def test_with_strings(self):
        places = 2
        self.assertEqual(units.as_raw("HUE", 360.0), 0)
        self.assertAlmostEqual(
            units.as_logical("SATURATION", 21627), 33.0, places)
        
if __name__ == '__main__':
    unittest.main()
