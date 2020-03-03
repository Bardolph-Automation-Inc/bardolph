#!/usr/bin/env python3

import unittest

from bardolph.controller import i_controller
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
                expected = [('set_color', ([11, 22, 33, 2500], 0))]
            elif light.get_label() == 'Bottom':
                expected = [('set_color', ([44, 55, 66, 2500], 0))]
            else:
                expected = []
            self.assertListEqual(light.call_list(), expected)

    def test_power(self):
        script = 'on "Top" off "Bottom"'
        self._runner.run_script(script)
        lifx = provide(i_controller.Lifx)
        for light in lifx.get_lights():
            if light.get_label() == "Top":
                expected = [('set_power', (65535, 0))]
            elif light.get_label() == "Bottom":
                expected = [('set_power', (0, 0))]
            else:
                expected = []
            self.assertListEqual(light.call_list(), expected)

    def test_and(self):
        script = """
            units raw hue 1 saturation 2 brightness 3 kelvin 4
            duration 5 set "Bottom" and "Top" and "Middle"
        """
        self._runner.run_script(script)
        lifx = provide(i_controller.Lifx)
        for light in lifx.get_lights():
            if light.get_label() in ('Bottom', 'Middle', 'Top'):
                expected = [('set_color', ([1, 2, 3, 4], 5))]
            else:
                expected = []
            self.assertListEqual(light.call_list(), expected)

    def test_mixed_and(self):
        script = """
            units raw hue 10 saturation 20 brightness 30 kelvin 40
            duration 50 set "Table" and group "Pole"
        """
        self._runner.test_code(script, ('Top', 'Middle', 'Bottom', 'Table'),
                        [('set_color', ([10, 20, 30, 40], 50))])

    def test_define_operand(self):
        script = """
            units raw define light_name "Top"
            hue 1 saturation 2 brightness 3 kelvin 4 duration 5
            set light_name
            on light_name
        """
        self._runner.test_code(script, 'Top', [
            ('set_color', ([1, 2, 3, 4], 5)),
            ('set_power', (65535, 5.0))])

    def test_define_value(self):
        script = """
            units raw define x 500
            hue 1 saturation 2 brightness 3 kelvin 4 duration x time x
            set "Top"
        """
        self._runner.test_code(
            script, 'Top', [('set_color', ([1, 2, 3, 4], 500))])

    def test_nested_define(self):
        script = """
            units raw define x 500 define y x
            hue 1 saturation 2 brightness 3 kelvin 4 duration y
            set "Top"
        """
        self._runner.test_code(
            script, 'Top', [('set_color', ([1, 2, 3, 4], 500))])

    def test_zones(self):
        script = """
            units raw
            hue 5 saturation 10 brightness 15 kelvin 20 duration 25
            set "Strip" zone 0 5
            set "Strip" zone 1
        """
        self._runner.test_code(script, 'Strip', [
            ('set_zone_color', (0, 6, [5, 10, 15, 20], 25.0)),
            ('set_zone_color', (1, 2, [5, 10, 15, 20], 25.0))])

    def test_set_zone(self):
        script = """
            units raw hue 10 saturation 20 brightness 30 kelvin 40 duration 50
            set "Strip" zone 5 7
        """
        self._runner.test_code(script, 'Strip',
                        [('set_zone_color', (5, 8, [10, 20, 30, 40], 50))])

    def test_get_zone(self):
        # LIFXLan treats range as non-inclusive.
        script = """
            define nine 9
            get "Strip" zone nine get "Strip" zone 9
        """
        self._runner.test_code(script, 'Strip', [
            ('get_color_zones', (9, 10)),
            ('get_color_zones', (9, 10))])

    def test_routine_get_zone(self):
        script = """
            units raw define get_z with x and z get x zone z
            get_z "Strip" 5
        """
        self._runner.test_code(script, 'Strip', [('get_color_zones', (5, 6))])

    def test_define_zones(self):
        script = """
            units raw
            hue 50 saturation 100 brightness 150 kelvin 200 duration 789
            define z1 0 define z2 5 define light "Strip"
            set light zone z1 z2
            set light zone z2
        """
        self._runner.test_code(script, 'Strip', [
            ('set_zone_color', (0, 6, [50, 100, 150, 200], 789)),
            ('set_zone_color', (5, 6, [50, 100, 150, 200], 789))])

    def test_group(self):
        script = """
            units raw
            hue 100 saturation 10 brightness 1 kelvin 1000
            set group "Pole"
            on group "Furniture"
        """
        self._runner.run_script(script)
        self._runner.check_call_list(('Top', 'Middle', 'Bottom'), [
            ('set_color', ([100, 10, 1, 1000], 0))])
        self._runner.check_call_list(('Table', 'Chair', 'Strip'), [
            ('set_power', (65535, 0))])

    def test_location(self):
        script = """
            units raw
            hue 100 saturation 10 brightness 1 kelvin 1000
            set location "Home"
            on location "Home"
        """
        self._runner.test_code_all(script, [
            ('set_color', ([100, 10, 1, 1000], 0)),
            ('set_power', (65535, 0))])

    def test_simple_routine(self):
        script = """
            units raw
            hue 100 saturation 10 brightness 1 kelvin 1000
            define do_set with light_name set light_name
            do_set "Table"
        """
        self._runner.test_code(script, 'Table',
                        [('set_color', ([100, 10, 1, 1000], 0))])

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
                        [('set_color', ([600, 50, 5, 5000], 0))])

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
                        ('set_color', ([600, 60, 6, 6000], 0)),
                        ('set_color', ([700, 60, 6, 6000], 0))])

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
            'Table', [('set_color', ([5, 1, 2, 3], 0))])
        self._runner.check_call_list('Chair', [
            ('set_color', ([5, 1, 2, 3], 0)),
            ('set_color', ([5, 1, 2, 3], 0)),
            ('set_color', ([10, 1, 2, 3], 0)),
            ('set_color', ([100, 1, 2, 3], 0)),
            ('set_color', ([100, 1, 100, 3], 0))])

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
            ('set_color', ([1, 7500, 3, 50], 0))])

if __name__ == '__main__':
    unittest.main()
