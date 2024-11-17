#!/usr/bin/env python

import unittest

from bardolph.fakes.activity_monitor import Action
from tests.script_runner import ScriptRunner
from tests import test_module


class ExampleTest(unittest.TestCase):
    def setUp(self):
        test_module.configure()
        self._runner = ScriptRunner(self)

    def test_individual(self):
        script = """
            units raw
            hue 120 saturation 100 brightness 75 kelvin 2700
            set "Table"
        """
        self._runner.test_code(
            script, 'Table', (Action.SET_COLOR, [120, 100, 75, 2700], 0))

    def test_multizone(self):
        script = """
            units raw
            hue 150 saturation 100 brightness 50 kelvin 2700 duration 2
            set "Strip"
            set "Strip" zone 5
            set "Strip" zone 0 8
        """
        self._runner.test_code(script, 'Strip', [
            (Action.SET_COLOR, [150, 100, 50, 2700], 2),
            (Action.SET_ZONE_COLOR, 5, 6, [150, 100, 50, 2700], 2),
            (Action.SET_ZONE_COLOR, 0, 9, [150, 100, 50, 2700], 2)
        ])

    def test_and(self):
        script = """
            units raw
            hue 120 saturation 75 brightness 75 kelvin 2700 duration 2
            set "Strip" zone 0 5 and "Table"
        """
        self._runner.run_script(script)
        self._runner.check_call_list(
            'Strip', (Action.SET_ZONE_COLOR, 0, 6, [120, 75, 75, 2700], 2))
        self._runner.check_call_list(
            'Table', (Action.SET_COLOR, [120, 75, 75, 2700], 2))

    def test_group(self):
        script = """
            units raw
            on location "Home"
            hue 120 saturation 80 brightness 75 kelvin 2700
            set location "Home"
        """
        self._runner.test_code(
            script,
            ('Top', 'Middle', 'Bottom', 'Strip', 'Candle'),
            [(Action.SET_POWER, 1, 0),
             (Action.SET_COLOR, [120, 80, 75, 2700], 0)])

    def test_macro_definition(self):
        script = """
            units raw
            define my_light "Chair"
            hue 120 saturation 80 brightness 50 kelvin 2700
            set my_light

            define zone_1 5 define zone_2 10
            set "Strip" zone zone_1 zone_2
        """
        self._runner.run_script(script)
        self._runner.check_call_list(
            'Chair', (Action.SET_COLOR, [120, 80, 50, 2700], 0))
        self._runner.check_call_list(
            'Strip', (Action.SET_ZONE_COLOR, 5, 11, [120, 80, 50, 2700], 0))


if __name__ == '__main__':
    unittest.main()
