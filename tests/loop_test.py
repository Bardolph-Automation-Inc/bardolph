#!/usr/bin/env python3

import unittest

from bardolph.controller import light_set
from bardolph.fakes import fake_lifx
from bardolph.fakes.fake_lifx import Action
from bardolph.lib.injection import provide
from tests.script_runner import ScriptRunner
from tests import test_module

class LoopTest(unittest.TestCase):
    def setUp(self):
        test_module.configure()
        fake_lifx.using_small_set().configure()
        light_set.configure()
        self._runner = ScriptRunner(self)

    def test_all(self):
        script = """
            hue 180 saturation 50 brightness 50 kelvin 1000
            repeat all as the_light with brt from 0 to 100
            begin
                brightness brt
                set the_light
            end
        """
        self._runner.run_script(script)
        self._runner.check_call_list('light_0', [
            (Action.SET_COLOR, ([32768, 32768, 0, 1000], 0))
        ])
        self._runner.check_call_list('light_1', [
            (Action.SET_COLOR, ([32768, 32768, 32768, 1000], 0))
        ])
        self._runner.check_call_list('light_2', [
            (Action.SET_COLOR, ([32768, 32768, 65535, 1000], 0))
        ])

    def test_const_count(self):
        script = """
            hue 180 saturation 50 brightness 50 kelvin 1000

            repeat 4 with brt from 0 to 100 begin
                brightness brt
                set all
            end
        """
        self._runner.run_script(script)
        self._runner.check_global_call_list([
            (Action.SET_COLOR, ([32768, 32768, 0, 1000], 0)),
            (Action.SET_COLOR, ([32768, 32768, 21845, 1000], 0)),
            (Action.SET_COLOR, ([32768, 32768, 43690, 1000], 0)),
            (Action.SET_COLOR, ([32768, 32768, 65535, 1000], 0))
        ])

    def test_expr_count(self):
        script = """
            assign x 16
            define y 5
            assign z 10
            assign thou 1000

            hue {36 * y} saturation {y * z} brightness {50 * 1} kelvin thou

            repeat {16 / (y - 1)} with brt from {-z+z} to {thou / 10} begin
                brightness brt
                set all
            end
        """
        self._runner.run_script(script)
        self._runner.check_global_call_list([
            (Action.SET_COLOR, ([32768, 32768, 0, 1000], 0)),
            (Action.SET_COLOR, ([32768, 32768, 21845, 1000], 0)),
            (Action.SET_COLOR, ([32768, 32768, 43690, 1000], 0)),
            (Action.SET_COLOR, ([32768, 32768, 65535, 1000], 0))
        ])

    def test_cycle_count(self):
        script = """
            repeat 5 with the_hue cycle 180 begin
                hue the_hue
                set all
            end
        """
        self._runner.run_script(script)
        self._runner.check_global_call_list([
            (Action.SET_COLOR, ([32768, 0, 0, 0], 0)),
            (Action.SET_COLOR, ([45874, 0, 0, 0], 0)),
            (Action.SET_COLOR, ([58982, 0, 0, 0], 0)),
            (Action.SET_COLOR, ([6554, 0, 0, 0], 0)),
            (Action.SET_COLOR, ([19660, 0, 0, 0], 0))
        ])

    def test_nested_cycle(self):
        script = """
            saturation 90 brightness 75 kelvin 2700

            repeat 5 with base_hue cycle begin
                time 0
                repeat all as the_light with the_hue cycle base_hue begin
                    hue the_hue
                    set the_light
                end
                time 3
                wait
            end
        """
        self._runner.run_script(script)

    def test_while(self):
        script = """
            hue 180 saturation 10 brightness 10 kelvin 500

            assign y 0
            define x 100
            repeat while {y < 4 and x == 100} begin
                set all
                assign y {y + 1}
            end
        """
        self._runner.run_script(script)
        self._runner.check_global_call_list(
            [(Action.SET_COLOR, ([32768, 6554, 6554, 500], 0))] * 4)

    def test_bare_with(self):
        script = """
            units raw
            repeat with i from 3 to 1 begin
                hue i set all
            end
            repeat with i from 1 to 3 begin
                hue i set all
            end
        """
        self._runner.run_script(script)
        self._runner.check_global_call_list([
            (Action.SET_COLOR, ([3, 0, 0, 0], 0)),
            (Action.SET_COLOR, ([2, 0, 0, 0], 0)),
            (Action.SET_COLOR, ([1, 0, 0, 0], 0)),
            (Action.SET_COLOR, ([1, 0, 0, 0], 0)),
            (Action.SET_COLOR, ([2, 0, 0, 0], 0)),
            (Action.SET_COLOR, ([3, 0, 0, 0], 0))
        ])

    def test_basic_list(self):
        script = """
            hue 180 saturation 50 brightness 50 kelvin 1000

            define l0 "light_0" assign l1 "light_1"
            repeat
                in l0 and l1 and "light_2"
                as the_light
                with brt from {saturation - brightness}
                to {hue - brightness - 30}
            begin
                brightness brt
                set the_light
            end
        """
        self._runner.run_script(script)
        self._runner.check_call_list('light_0', [
            (Action.SET_COLOR, ([32768, 32768, 0, 1000], 0))
        ])
        self._runner.check_call_list('light_1', [
            (Action.SET_COLOR, ([32768, 32768, 32768, 1000], 0))
        ])
        self._runner.check_call_list('light_2', [
            (Action.SET_COLOR, ([32768, 32768, 65535, 1000], 0))
        ])

    def test_list_cycle(self):
        script = """
            hue 180 saturation 50 brightness 50 kelvin 1000

            repeat
                in "light_0" and "light_1" and "light_2" as the_light
                with the_hue cycle
            begin
                hue the_hue
                set the_light
            end
        """
        self._runner.run_script(script)
        self._runner.check_call_list('light_0', [
            (Action.SET_COLOR, ([0, 32768, 32768, 1000], 0))
        ])
        self._runner.check_call_list('light_1', [
            (Action.SET_COLOR, ([21845, 32768, 32768, 1000], 0))
        ])
        self._runner.check_call_list('light_2', [
            (Action.SET_COLOR, ([43690, 32768, 32768, 1000], 0))
        ])

    def test_group(self):
        script = """
            hue 180 saturation 50 brightness 50 kelvin 1000

            repeat in group "group" as the_light with brt from 100 to 0
            begin
                brightness brt
                set the_light
            end
        """
        self._runner.run_script(script)
        self._runner.check_call_list('light_0', [
            (Action.SET_COLOR, ([32768, 32768, 65535, 1000], 0))
        ])
        self._runner.check_call_list('light_2', [
            (Action.SET_COLOR, ([32768, 32768, 0, 1000], 0))
        ])

    def test_group_cycle(self):
        script = """
            saturation 75 brightness 25 kelvin 1234

            repeat in group "group" as the_light with the_hue cycle
            begin
                hue the_hue
                set the_light
            end
        """
        self._runner.run_script(script)
        self._runner.check_call_list('light_0', [
            (Action.SET_COLOR, ([0, 49151, 16384, 1234], 0))
        ])
        self._runner.check_call_list('light_2', [
            (Action.SET_COLOR, ([32768, 49151, 16384, 1234], 0))
        ])

    def test_group_no_with(self):
        script = """
            hue 90 saturation 50 brightness 75 kelvin 2000
            repeat in group "group" as the_light set the_light
        """
        self._runner.run_script(script)
        self._runner.check_call_list('light_0', [
            (Action.SET_COLOR, ([16384, 32768, 49151, 2000], 0))
        ])
        self._runner.check_call_list('light_2', [
            (Action.SET_COLOR, ([16384, 32768, 49151, 2000], 0))
        ])

    def test_all_groups(self):
        script = """
            hue 180 saturation 50 brightness 50 kelvin 1000

            repeat group as grp with brt from 0 to 100
            begin
                brightness brt
                set group grp
            end
        """
        fake_lifx.using_large_set().configure()
        light_set.configure()
        self._runner.run_script(script)
        self._runner.check_call_list(('Chair', 'Strip', 'Table'), [
            (Action.SET_COLOR, ([32768, 32768, 0, 1000], 0))
        ])
        self._runner.check_call_list(('Bottom', 'Middle', 'Top'), [
            (Action.SET_COLOR, ([32768, 32768, 65535, 1000], 0))
        ])

    def test_all_locations(self):
        script = """
            hue 180 saturation 50 brightness 50 kelvin 1000

            repeat location as loc with brt from 0 to 100
            begin
                brightness brt
                set location loc
            end
        """
        self._runner.run_script(script)
        self._runner.check_call_list(('light_0', 'light_2'), [
            (Action.SET_COLOR, ([32768, 32768, 0, 1000], 0))
        ])
        self._runner.check_call_list('light_1', [
            (Action.SET_COLOR, ([32768, 32768, 65535, 1000], 0))
        ])

    def test_mixture(self):
        fake_lifx.using_large_set().configure()
        light_set.configure()

        script = """
            hue 180 saturation 50 brightness 50 kelvin 1000

            repeat in "Table" and group "Pole" and "Chair"
            and location "Home" as the_light
            begin
                set the_light
            end
        """
        self._runner.run_script(script)
        self._runner.check_call_list(
            ('Top', 'Middle', 'Bottom', 'Table', 'Chair'),
            [(Action.SET_COLOR, ([32768, 32768, 32768, 1000], 0))] * 2)


if __name__ == '__main__':
    unittest.main()
