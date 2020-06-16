#!/usr/bin/env python3

import unittest

from bardolph.controller import i_controller
from bardolph.fakes.fake_lifx import Action
from bardolph.lib.injection import provide
from tests.script_runner import ScriptRunner
from tests import test_module

class EndToEndTest(unittest.TestCase):
    _ALL_LIGHTS = ('Top', 'Middle', 'Bottom', 'Table', 'Chair', 'Strip')

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

    def test_define_operand(self):
        script = """
            units raw define light_name "Top"
            hue 1 saturation 2 brightness 3 kelvin 4 duration 5
            set light_name
            on light_name
        """
        self._runner.test_code(script, 'Top', [
            (Action.SET_COLOR, ([1, 2, 3, 4], 5)),
            (Action.SET_POWER, (65535, 5.0))])

    def test_define_value(self):
        script = """
            units raw define x 500
            hue 1 saturation 2 brightness 3 kelvin 4 duration x time x
            set "Top"
        """
        self._runner.test_code(
            script, 'Top', [(Action.SET_COLOR, ([1, 2, 3, 4], 500))])

    def test_nested_define(self):
        script = """
            units raw define x 500 define y x
            hue 1 saturation 2 brightness 3 kelvin 4 duration y
            set "Top"
        """
        self._runner.test_code(
            script, 'Top', [(Action.SET_COLOR, ([1, 2, 3, 4], 500))])

    def test_zones(self):
        script = """
            units raw
            hue 5 saturation 10 brightness 15 kelvin 20 duration 25
            set "Strip" zone 0 5
            set "Strip" zone 1
        """
        self._runner.test_code(script, 'Strip', [
            (Action.SET_ZONE_COLOR, (0, 6, [5, 10, 15, 20], 25.0)),
            (Action.SET_ZONE_COLOR, (1, 2, [5, 10, 15, 20], 25.0))
        ])

    def test_set_zone(self):
        script = """
            units raw hue 10 saturation 20 brightness 30 kelvin 40 duration 50
            set "Strip" zone 5 7
        """
        self._runner.test_code(script, 'Strip',
            [(Action.SET_ZONE_COLOR, (5, 8, [10, 20, 30, 40], 50))])

    def test_get_zone(self):
        # LIFXLan treats range as non-inclusive.
        script = """
            define nine 9
            get "Strip" zone nine get "Strip" zone 9
        """
        self._runner.test_code(script, 'Strip', [
            (Action.GET_ZONE_COLOR, (9, 10)),
            (Action.GET_ZONE_COLOR, (9, 10))])

    def test_routine_get_zone(self):
        script = """
            units raw define get_z with x and z get x zone z
            get_z "Strip" 5
        """
        self._runner.test_code(script, 'Strip',
            [(Action.GET_ZONE_COLOR, (5, 6))])

    def test_define_zones(self):
        script = """
            units raw
            hue 50 saturation 100 brightness 150 kelvin 200 duration 789
            define z1 0 define z2 5 define light "Strip"
            set light zone z1 z2
            set light zone z2
        """
        self._runner.test_code(script, 'Strip', [
            (Action.SET_ZONE_COLOR, (0, 6, [50, 100, 150, 200], 789)),
            (Action.SET_ZONE_COLOR, (5, 6, [50, 100, 150, 200], 789))])

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

    def test_simple_routine(self):
        script = """
            units raw
            hue 100 saturation 10 brightness 1 kelvin 1000
            define do_set with light_name set light_name
            do_set "Table"
        """
        self._runner.test_code(script, 'Table',
                        [(Action.SET_COLOR, ([100, 10, 1, 1000], 0))])

    def test_compound_routine(self):
        script = """
            units raw
            hue 500 saturation 50 brightness 5 kelvin 5000
            define do_set with light1 and light2 and the_hue
            begin
                hue the_hue set light1 and light2
            end
            do_set "Table" "Bottom" 600
            units logical
        """
        self._runner.test_code(script, ('Table', 'Bottom'),
                        [(Action.SET_COLOR, ([600, 50, 5, 5000], 0))])

    def test_nested_param(self):
        script = """
            units raw
            define inner with inner_hue hue inner_hue
            define outer with outer_hue inner outer_hue
            define outer_outer with outer_hue outer outer_hue
            hue 600 saturation 60 brightness 6 kelvin 6000
            set "Table"
            outer_outer 700
            set "Table"
        """
        self._runner.test_code(script, 'Table', [
                        (Action.SET_COLOR, ([600, 60, 6, 6000], 0)),
                        (Action.SET_COLOR, ([700, 60, 6, 6000], 0))])

    def test_variables(self):
        script = """
            units raw saturation 1 brightness 2 kelvin 3
            assign x 5 hue x set "Table"

            assign name "Chair" set name
            assign name2 name set name2

            define use_var with x
            begin assign y x hue y set name end
            use_var 10

            assign z 100
            use_var z

            brightness z set "Chair"
        """
        self._runner.run_script(script)
        self._runner.check_call_list(
            'Table', [(Action.SET_COLOR, ([5, 1, 2, 3], 0))])
        self._runner.check_call_list('Chair', [
            (Action.SET_COLOR, ([5, 1, 2, 3], 0)),
            (Action.SET_COLOR, ([5, 1, 2, 3], 0)),
            (Action.SET_COLOR, ([10, 1, 2, 3], 0)),
            (Action.SET_COLOR, ([100, 1, 2, 3], 0)),
            (Action.SET_COLOR, ([100, 1, 100, 3], 0))])

    def test_nested_variables(self):
        script = """
            units raw hue 1 saturation 2 brightness 3 kelvin 4
            assign n 50

            define inner1 with x begin kelvin x set "Chair" end
            define inner2 with y begin saturation y inner1 n end
            define outer1 with z inner2 z

            outer1 7500
        """
        self._runner.run_script(script)
        self._runner.check_call_list('Chair', [
            (Action.SET_COLOR, ([1, 7500, 3, 50], 0))])

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
            (Action.SET_COLOR_ALL, ([10922, 49151, 65535, 0], 1000)),
            (Action.SET_COLOR_ALL, ([5461, 49151, 65535, 0], 1000)),
            (Action.SET_COLOR_ALL, ([10922, 49151, 65535, 0], 1000)),
            (Action.SET_COLOR_ALL, ([5461, 49151, 65535, 0], 1000)),
            (Action.SET_COLOR_ALL, ([5461, 32768, 10000, 0], 1000))
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
            (Action.SET_COLOR_ALL, ([3000, 2000, 5000, 0], 1)),
            (Action.SET_COLOR_ALL, ([4000, 2000, 5000, 0], 1)),
            (Action.SET_COLOR_ALL, ([3000, 2000, 5000, 0], 1)),
            (Action.SET_COLOR_ALL, ([4000, 2000, 5000, 0], 1)),
            (Action.SET_COLOR_ALL, ([6000, 2000, 32768, 0], 1))
        ])

if __name__ == '__main__':
    unittest.main()
