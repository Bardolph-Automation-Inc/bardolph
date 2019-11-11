#!/usr/bin/env python

import unittest

from bardolph.controller.units import Units
from bardolph.controller.instruction import Register

class UnitsTest(unittest.TestCase):
    def setUp(self):
        self.units = Units()

    def test_as_raw(self):
        self.assertEqual(self.units.as_raw(Register.HUE, 360.0), 0)
        self.assertEqual(self.units.as_raw(Register.HUE, 120.0), 21845)
        self.assertEqual(self.units.as_raw(Register.SATURATION, 33), 21627)
        self.assertEqual(self.units.as_raw(Register.BRIGHTNESS, 67), 43908)
        self.assertEqual(self.units.as_raw(Register.TIME, 1000000), 1000000)
        self.assertEqual(
            self.units.as_raw(Register.DURATION, 200000), 200000)
        self.assertEqual(self.units.as_raw(Register.KELVIN, 4000), 4000)

    def test_as_logical(self):
        places = 2
        self.assertAlmostEqual(
            self.units.as_logical(Register.HUE, 65535), 360.0, places)
        self.assertAlmostEqual(
            self.units.as_logical(Register.HUE, 21845), 120.0, places)
        self.assertAlmostEqual(
            self.units.as_logical(Register.SATURATION, 21627), 33.0, places)
        self.assertAlmostEqual(
            self.units.as_logical(Register.BRIGHTNESS, 43908), 67.0, places)
        self.assertAlmostEqual(
            self.units.as_logical(Register.KELVIN, 4000), 4000.0, places)

        # These values should be untouched, hence assertEqual.
        self.assertEqual(
            self.units.as_logical(Register.TIME, 1000000.0), 1000000.0)
        self.assertEqual(
            self.units.as_logical(Register.DURATION, 200000.0), 200000.0)

    def test_with_strings(self):
        places = 2
        self.assertEqual(self.units.as_raw("HUE", 360.0), 0)
        self.assertAlmostEqual(
            self.units.as_logical("SATURATION", 21627), 33.0, places)
        
if __name__ == '__main__':
    unittest.main()
