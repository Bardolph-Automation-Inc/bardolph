#!/usr/bin/env python3

import unittest

from bardolph.fakes.fake_lifx import Action
from tests.script_runner import ScriptRunner
from tests import test_module


class DefineTest(unittest.TestCase):
    def setUp(self):
        test_module.configure()
        self._runner = ScriptRunner(self)

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

    def test_assign_registers(self):
        script = """
            assign y 0
            hue 10
            assign y hue
            hue y set "Top"
            brightness 20
            assign z {brightness * 5}
            hue z set "Top"
        """
        self._runner.test_code(
            script, 'Top', [
                (Action.SET_COLOR, ([1820, 0, 0, 0], 0)),
                (Action.SET_COLOR, ([18204, 0, 13107, 0], 0))
            ])

    def test_nested_define(self):
        script = """
            units raw define x 500 define y x
            hue 1 saturation 2 brightness 3 kelvin 4 duration y
            set "Top"
        """
        self._runner.test_code(
            script, 'Top', (Action.SET_COLOR, ([1, 2, 3, 4], 500)))

    def test_routine_get_zone(self):
        script = """
            units raw define get_z with x z get x zone z
            get_z "Strip" 5
        """
        self._runner.test_code(
            script, 'Strip', (Action.GET_ZONE_COLOR, (5, 6)))

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

    def test_simple_routine(self):
        script = """
            units raw
            hue 100 saturation 10 brightness 1 kelvin 1000
            define do_set with light_name set light_name
            do_set "Table"
        """
        self._runner.test_code(
            script, 'Table', (Action.SET_COLOR, ([100, 10, 1, 1000], 0)))

    def test_compound_routine(self):
        script = """
            units raw
            hue 500 saturation 50 brightness 5 kelvin 5000
            define do_set with light1 light2 the_hue
            begin
                hue the_hue set light1 and light2
            end
            do_set "Table" "Bottom" 600
            units logical
        """
        self._runner.test_code(script, ('Table', 'Bottom'),
                               (Action.SET_COLOR, ([600, 50, 5, 5000], 0)))

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
            'Table', (Action.SET_COLOR, ([5, 1, 2, 3], 0)))
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
        self._runner.check_call_list(
            'Chair', (Action.SET_COLOR, ([1, 7500, 3, 50], 0)))

    def test_nested_assignment(self):
        script = """
            # Assign to global variable inside routine

            units raw
            assign y 100

            define set_global begin
                assign y 50
            end

            hue y set "Top"
            set_global
            hue y set "Top"
        """
        self._runner.run_script(script)
        self._runner.check_call_list('Top', [
            (Action.SET_COLOR, ([100, 0, 0, 0], 0)),
            (Action.SET_COLOR, ([50, 0, 0, 0], 0))
        ])

    def test_simple_routines(self):
        script = """
            hue 180 saturation 50 brightness 50 duration 100 time 0 kelvin 0

            define simple_no_params kelvin 50
            simple_no_params
            set all

            define simple_one_param with x kelvin x
            simple_one_param 1000
            set all

            hue 0 saturation 25 brightness 75 kelvin 100
            define simple_three_params with x y z set x and y and z
            simple_three_params "Top" "Middle" "Bottom"
        """
        self._runner.run_script(script)
        self._runner.check_global_call_list([
            (Action.SET_COLOR, ([32768, 32768, 32768, 50], 100000)),
            (Action.SET_COLOR, ([32768, 32768, 32768, 1000], 100000))
        ])
        self._runner.check_call_list(('Top', 'Middle', 'Bottom'),
            (Action.SET_COLOR, ([0, 16384, 49151, 100], 100000)))

    def test_complex_routines(self):
        script = """
            hue 180 saturation 50 brightness 50 duration 100 time 0 kelvin 0

            define complex_no_params begin
                kelvin 75
                brightness 100
            end
            complex_no_params
            set all

            define complex_one_param with x begin
                kelvin x
            end
            complex_one_param 85
            set all

            hue 90 saturation 75 brightness 33.33
            define complex_three_params with x y z begin
                set x
                set y
                set z
            end
            complex_three_params "Bottom" "Middle" "Top"
        """
        self._runner.run_script(script)
        self._runner.check_global_call_list([
            (Action.SET_COLOR, ([32768, 32768, 65535, 75], 100000)),
            (Action.SET_COLOR, ([32768, 32768, 65535, 85], 100000))
        ])
        self._runner.check_call_list(('Top', 'Middle', 'Bottom'),
            (Action.SET_COLOR, ([16384, 49151, 21843, 85], 100000)))

    def test_routine_namespace(self):
        script = """
            hue 180 saturation 50 brightness 75 duration 100 time 0 kelvin 0

            define simple_no_params kelvin 75
            define simple_1_param with x kelvin x
            define use_1_param with x simple_1_param x
            use_1_param 90
            set all

            define set_2 with x y set x and y
            hue 90 saturation 75 brightness 33.33 kelvin 85
            define simple_2_params with x y set_2 x y
            define use_2_params simple_2_params "Top" "Middle"
            use_2_params
        """
        self._runner.run_script(script)
        self._runner.check_global_call_list(
            (Action.SET_COLOR, ([32768, 32768, 49151, 90], 100000)))
        self._runner.check_call_list(('Top', 'Middle'),
            (Action.SET_COLOR, ([16384, 49151, 21843, 85], 100000)))


if __name__ == '__main__':
    unittest.main()
