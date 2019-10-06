#!/usr/bin/env python

import unittest

from bardolph.controller.units import Units
from bardolph.parser.token_types import TokenTypes

class UnitsTest(unittest.TestCase):
    def setUp(self):
        self.units = Units()
        
    def test_as_raw(self):
        self.assertEqual(self.units.as_raw(TokenTypes.HUE, 360.0), 0)
        self.assertEqual(self.units.as_raw(TokenTypes.HUE, 120.0), 21845)
        self.assertEqual(self.units.as_raw(TokenTypes.SATURATION, 33), 21627)
        self.assertEqual(self.units.as_raw(TokenTypes.BRIGHTNESS, 67), 43908)
        self.assertEqual(self.units.as_raw(TokenTypes.TIME, 1000000), 1000000)
        self.assertEqual(self.units.as_raw(TokenTypes.DURATION, 200000), 200000)
        self.assertEqual(self.units.as_raw(TokenTypes.KELVIN, 4000), 4000)
        
    def test_as_logical(self):
        places = 2
        self.assertAlmostEqual(
            self.units.as_logical(TokenTypes.HUE, 65535), 360.0, places)
        self.assertAlmostEqual(
            self.units.as_logical(TokenTypes.HUE, 21845), 120.0, places)
        self.assertAlmostEqual(
            self.units.as_logical(TokenTypes.SATURATION, 21627), 33.0, places)
        self.assertAlmostEqual(
            self.units.as_logical(TokenTypes.BRIGHTNESS, 43908), 67.0, places)
        self.assertAlmostEqual(
            self.units.as_logical(TokenTypes.KELVIN, 4000), 4000.0, places)
        
        # These values should be untouched, hence assertEqual.
        self.assertEqual(
            self.units.as_logical(TokenTypes.TIME, 1000000.0), 1000000.0)
        self.assertEqual(
            self.units.as_logical(TokenTypes.DURATION, 200000.0), 200000.0)
        
     
if __name__ == '__main__':
    unittest.main()
