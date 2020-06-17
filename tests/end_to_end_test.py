#!/usr/bin/env python3

import unittest

from bardolph.controller import i_controller
from bardolph.fakes.fake_lifx import Action
from bardolph.lib.injection import provide
from tests.script_runner import ScriptRunner
from tests import test_module

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
        lifx = provide(i_controller.Lifx)
        for light in lifx.get_lights():
            if light.get_label() == 'Top':
                expected = [(Action.SET_COLOR, ([11, 22, 33, 2500], 0))]
            elif light.get_label() == 'Bottom':
                expected = [(Action.SET_COLOR, ([44, 55, 66, 2500], 0))]
            else:
                expected = []
            self.assertListEqual(light.get_call_list(), expected)

    def test_power(self):
        script = 'on "Top" off "Bottom"'
        self._runner.run_script(script)
        lifx = provide(i_controller.Lifx)
        for light in lifx.get_lights():
            if light.get_label() == "Top":
                expected = [(Action.SET_POWER, (65535, 0))]
            elif light.get_label() == "Bottom":
                expected = [(Action.SET_POWER, (0, 0))]
            else:
                expected = []
            self.assertListEqual(light.get_call_list(), expected)

    def test_and(self):
        script = """
            units raw hue 1 saturation 2 brightness 3 kelvin 4
            duration 5 set "Bottom" and "Top" and "Middle"
        """
        self._runner.run_script(script)
        lifx = provide(i_controller.Lifx)
        for light in lifx.get_lights():
            if light.get_label() in ('Bottom', 'Middle', 'Top'):
                expected = [(Action.SET_COLOR, ([1, 2, 3, 4], 5))]
            else:
                expected = []
            self.assertListEqual(light.get_call_list(), expected)

    def test_mixed_and(self):
        script = """
            units raw hue 10 saturation 20 brightness 30 kelvin 40
            duration 50 set "Table" and group "Pole"
        """
        self._runner.test_code(script, ('Top', 'Middle', 'Bottom', 'Table'),
                            [(Action.SET_COLOR, ([10, 20, 30, 40], 50))])

    def test_routine_get_zone(self):
        script = """
            units raw define get_z with x z get x zone z
            get_z "Strip" 5
        """
        self._runner.test_code(script, 'Strip',
            [(Action.GET_ZONE_COLOR, (5, 6))])

    def test_group(self):
        script = """
            units raw
            hue 100 saturation 10 brightness 1 kelvin 1000
            set group "Pole"
            on group "Furniture"
        """
        self._runner.run_script(script)
        self._runner.check_call_list(('Top', 'Middle', 'Bottom'), [
            (Action.SET_COLOR, ([100, 10, 1, 1000], 0))])
        self._runner.check_call_list(('Table', 'Chair', 'Strip'), [
            (Action.SET_POWER, (65535, 0))])

    def test_location(self):
        script = """
            units raw
            hue 100 saturation 10 brightness 1 kelvin 1000
            set location "Home"
            on location "Home"
        """
        self._runner.test_code_all(script, [
            (Action.SET_COLOR, ([100, 10, 1, 1000], 0)),
            (Action.SET_POWER, (65535, 0))])


    def test_expression(self):
        script = """
            assign x {5 + 6}
        """
        self._runner.run_script(script)

    def test_if_expr(self):
        script = """
            units raw
            hue 1 saturation 2 brightness 3 kelvin 4 duration 5

            assign x 10
            assign y 20

            if {8 >= 7} hue 5
            if {9 <= 10} begin saturation 55 end
            if {8 > 7} brightness 555
            if {not x > y} kelvin 5555

            if {8 != 9} duration {50 / 5}
            if {100 == 10 * 10} set "Top"
        """
        self._runner.test_code(
            script, 'Top', [(Action.SET_COLOR, ([5, 55, 555, 5555], 10.0))])

    def test_if_else(self):
        script = """
            units raw hue 1 saturation 2 brightness 3 kelvin 4
            assign five 5 assign two 2
            if {five < two} hue 0 else hue 1000 set "Top"
            if {five < two} begin hue 0 end else begin hue 2000 end set "Top"
            if {five < two} hue 0 else begin hue 3000 end set "Top"
            if {five > two} begin hue 4000 end else hue 0 set "Top"
            if {five > two} begin hue 5000 end else hue 0 set "Top"
        """
        self._runner.test_code(script, 'Top', [
                (Action.SET_COLOR, ([1000, 2, 3, 4], 0.0)),
                (Action.SET_COLOR, ([2000, 2, 3, 4], 0.0)),
                (Action.SET_COLOR, ([3000, 2, 3, 4], 0.0)),
                (Action.SET_COLOR, ([4000, 2, 3, 4], 0.0)),
                (Action.SET_COLOR, ([5000, 2, 3, 4], 0.0))])

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
            (Action.SET_COLOR, ([5461, 49151, 65535, 0], 1000)),
            (Action.GET_COLOR, ([10922, 49151, 65535, 0])),
            (Action.GET_COLOR, ([5461, 49151, 65535, 0])),
            (Action.GET_COLOR, ([10922, 49151, 65535, 0]))
        ])
        self._runner.check_global_call_list([
            (Action.SET_COLOR, ([10922, 49151, 65535, 0], 1000)),
            (Action.SET_COLOR, ([5461, 49151, 65535, 0], 1000)),
            (Action.SET_COLOR, ([10922, 49151, 65535, 0], 1000)),
            (Action.SET_COLOR, ([5461, 49151, 65535, 0], 1000)),
            (Action.SET_COLOR, ([5461, 32768, 10000, 0], 1000))
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
            (Action.SET_COLOR, ([1000, 2000, 5000, 0], 1)),
            (Action.GET_COLOR, ([3000, 2000, 5000, 0])),
            (Action.GET_COLOR, ([4000, 2000, 5000, 0])),
            (Action.GET_COLOR, ([3000, 2000, 5000, 0]))
        ])
        self._runner.check_global_call_list([
            (Action.SET_COLOR, ([3000, 2000, 5000, 0], 1)),
            (Action.SET_COLOR, ([4000, 2000, 5000, 0], 1)),
            (Action.SET_COLOR, ([3000, 2000, 5000, 0], 1)),
            (Action.SET_COLOR, ([4000, 2000, 5000, 0], 1)),
            (Action.SET_COLOR, ([6000, 2000, 32768, 0], 1))
        ])

if __name__ == '__main__':
    unittest.main()
