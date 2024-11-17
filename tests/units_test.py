#!/usr/bin/env python

import unittest

from bardolph.controller import units
from bardolph.fakes.activity_monitor import Action
from tests import test_module
from tests.script_runner import ScriptRunner


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
        self._assert_colors_equal(raw_color, [3641, 49151, 65535, 4000])

        rgb_color = units.raw_to_rgb([21845, 21627, 43908, 4000])
        self._assert_colors_equal(rgb_color, [44.889, 67.0, 44.889, 4000])

    def test_mode_switch(self):
        script = """
            units raw saturation 2000 kelvin 4000
            units logical hue 120 brightness 50
            units raw
            hue {hue + 10}
            brightness {brightness + 20}
            set "Top"
            units rgb
            red 100 green 0 blue 0 kelvin 0
            set "Middle"
            red 100 green 100 blue 0 kelvin 0
            set "Middle"
            red 50 green 50 blue 50 kelvin 1000
            set "Middle"
            red 25 green 50 blue 75 kelvin 2000
            units raw
            hue {hue + 100}
            saturation {saturation + 200}
            brightness {brightness + 300}
            kelvin {kelvin + 400}
            set "Bottom"
        """
        test_module.configure()
        runner = ScriptRunner(self)
        runner.run_script(script)
        runner.check_call_list(
            'Top', (Action.SET_COLOR, [21855, 2000, 32788, 4000], 0))
        runner.check_call_list(
            'Middle', [
                (Action.SET_COLOR, [0, 65535, 65535, 0], 0),
                (Action.SET_COLOR, [10922, 65535, 65535, 0], 0),
                (Action.SET_COLOR, [0, 0, 32768, 1000], 0)
            ])
        runner.check_call_list(
            'Bottom', (Action.SET_COLOR, [38329, 43890, 49451, 2400], 0))

    def test_flip(self):
        script = """
            hue 120 saturation 100 brightness 100 kelvin 2000
            set "Top"

            units rgb
            green {green / 2.0}
            set "Top"
        """
        test_module.configure()
        runner = ScriptRunner(self)
        runner.run_script(script)
        runner.check_call_list(
            'Top', [
                (Action.SET_COLOR, [21845, 65535, 65535, 2000], 0),
                (Action.SET_COLOR, [21845, 65535, 32768, 2000], 0)
            ])


if __name__ == '__main__':
    unittest.main()
