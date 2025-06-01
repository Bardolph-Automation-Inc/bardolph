#!/usr/bin/env python

import unittest

from bardolph.controller import i_controller
from bardolph.fakes.activity_monitor import Action
from bardolph.lib.injection import provide
from tests import test_module
from tests.script_runner import ScriptRunner


class EndToEndTest(unittest.TestCase):
    def setUp(self):
        test_module.configure()
        self._runner = ScriptRunner(self)

    def test_individual(self):
        script = """
            units raw
            hue 11 saturation 22 brightness 33 kelvin 2500 set "Top"
            hue 44 saturation 55 brightness 66 set "Bottom"
        """
        self._runner.run_script(script)
        lifx = provide(i_controller.LightApi)
        self._runner.check_call_list(
            'Top', (Action.SET_COLOR, [11, 22, 33, 2500], 0))
        self._runner.check_call_list(
            'Bottom', (Action.SET_COLOR, [44, 55, 66, 2500], 0))

    def test_power(self):
        script = 'on "Top" off "Bottom"'
        self._runner.run_script(script)
        self._runner.check_call_list("Top", (Action.SET_POWER, 1, 0))
        self._runner.check_call_list("Bottom", (Action.SET_POWER, 0, 0))

    def test_and(self):
        script = """
            units raw hue 1 saturation 2 brightness 3 kelvin 4 duration 5
            set "Bottom" and "Top" and "Middle"
        """
        self._runner.run_script(script)
        lifx = provide(i_controller.LightApi)
        self._runner.check_call_list(
            ('Bottom', 'Top', 'Middle'), (Action.SET_COLOR, [1, 2, 3, 4], 5))

    def test_mixed_and(self):
        script = """
            units raw hue 10 saturation 20 brightness 30 kelvin 40
            duration 50 set "Table" and group "Pole"
        """
        self._runner.test_code(script, ('Top', 'Middle', 'Bottom', 'Table'),
                               (Action.SET_COLOR, [10, 20, 30, 40], 50))

    def test_group(self):
        script = """
            units raw
            hue 100 saturation 10 brightness 1 kelvin 1000
            set group "Pole"
            on group "Furniture"
        """
        self._runner.run_script(script)
        self._runner.check_call_list(('Top', 'Middle', 'Bottom'),
                                     (Action.SET_COLOR, [100, 10, 1, 1000], 0))
        self._runner.check_call_list(('Table', 'Chair', 'Strip'),
                                     (Action.SET_POWER, 1, 0))

    def test_location(self):
        script = """
            units raw
            hue 100 saturation 10 brightness 1 kelvin 1000
            set location "Home"
            on location "Home"
        """
        self._runner.test_code(
            script,
            ('Top', 'Middle', 'Bottom', 'Strip', 'Candle'),
            [(Action.SET_COLOR, [100, 10, 1, 1000], 0),
             (Action.SET_POWER, 1, 0)])

    def test_multiple_get_logical(self):
        script = """
            duration 1 hue 30 saturation 75 brightness 100 set "Top"
            time 1
            hue 60 set all
            get "Top" hue 30 set all
            get "Top" hue 60 set all
            get "Top" hue 30 set all
            units raw brightness 10000 units logical saturation 50 set all
        """
        self._runner.run_script(script)
        self._runner.check_call_list('Top', [
            (Action.SET_COLOR, [5461, 49151, 65535, 0], 1000.0),
            (Action.GET_COLOR, [10922, 49151, 65535, 0]),
            (Action.GET_COLOR, [5461, 49151, 65535, 0]),
            (Action.GET_COLOR, [10922, 49151, 65535, 0])
        ])
        self._runner.check_global_call_list([
            (Action.SET_COLOR, [10922, 49151, 65535, 0], 1000),
            (Action.SET_COLOR, [5461, 49151, 65535, 0], 1000),
            (Action.SET_COLOR, [10922, 49151, 65535, 0], 1000),
            (Action.SET_COLOR, [5461, 49151, 65535, 0], 1000),
            (Action.SET_COLOR, [5461, 32768, 10000, 0], 1000)
        ])

    def test_multiple_get_raw(self):
        script = """
            units raw
            duration 1 hue 1000 saturation 2000 brightness 5000 set "Top"
            time 1
            hue 3000 set all
            get "Top" hue 4000 set all
            get "Top" hue 3000 set all
            get "Top" hue 4000 set all
            units logical brightness 50 units raw hue 6000 set all
        """
        self._runner.run_script(script)
        self._runner.check_call_list('Top', [
            (Action.SET_COLOR, [1000, 2000, 5000, 0], 1),
            (Action.GET_COLOR, [3000, 2000, 5000, 0]),
            (Action.GET_COLOR, [4000, 2000, 5000, 0]),
            (Action.GET_COLOR, [3000, 2000, 5000, 0])
        ])
        self._runner.check_global_call_list([
            (Action.SET_COLOR, [3000, 2000, 5000, 0], 1),
            (Action.SET_COLOR, [4000, 2000, 5000, 0], 1),
            (Action.SET_COLOR, [3000, 2000, 5000, 0], 1),
            (Action.SET_COLOR, [4000, 2000, 5000, 0], 1),
            (Action.SET_COLOR, [6000, 2000, 32768, 0], 1)
        ])


if __name__ == '__main__':
    unittest.main()
