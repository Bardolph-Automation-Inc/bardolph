#!/usr/bin/env python3

import time
import unittest

from bardolph.controller import i_controller 
from bardolph.controller.script_job import ScriptJob
from bardolph.lib.injection import provide
from bardolph.lib.job_control import JobControl
from . import test_module

class EndToEndTest(unittest.TestCase):
    def setUp(self):
        test_module.configure()
        
    def _run_script(self, script):
        jobs = JobControl()
        jobs.add_job(ScriptJob.from_string(script))
        max_waits = 10
        while jobs.has_jobs():
            time.sleep(0.1)
            max_waits -= 1
            if max_waits < 0:
                self.fail("Jobs didn't finish.")

    def test_individual(self):
        script = 'units raw hue 11 saturation 22 brightness 33 kelvin 2500 '
        script += 'set "Top" hue 44 saturation 55 brightness 66 set "Bottom"'
        self._run_script(script)
        lifx = provide(i_controller.Lifx)
        for light in lifx.get_lights():
            if light.get_label() == 'Top':
                expected = [('set_color', ([11, 22, 33, 2500], 0))]
            elif light.get_label() == 'Bottom':
                expected = [('set_color', ([44, 55, 66, 2500], 0))]
            else:
                expected = []
            self.assertListEqual(light.call_list(), expected)
            
    def test_group(self):
        script = 'units raw hue 1 saturation 2 brightness 3 kelvin 4 '
        script += 'duration 5 set group "Pole"'
        self._run_script(script)

        expected = [('set_color', ([1, 2, 3, 4], 5))]
        lifx = provide(i_controller.Lifx)
        for light in lifx.get_lights():
            if light.get_label() in ('Top', 'Middle', 'Bottom'):
                self.assertListEqual(light.call_list(), expected)
            else:
                self.assertListEqual(light.call_list(), [])

    def test_location(self):
        script = 'units raw hue 6 saturation 7 brightness 8 kelvin 9 '
        script += 'duration 10 set location "Home"'
        self._run_script(script)

        expected = [('set_color', ([6, 7, 8, 9], 10))]
        lifx = provide(i_controller.Lifx)
        for light in lifx.get_lights():
            self.assertListEqual(light.call_list(), expected)

    def test_power(self):
        script = 'on "Top" off "Bottom"'
        self._run_script(script)
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
        script = 'units raw hue 1 saturation 2 brightness 3 kelvin 4 '
        script += 'duration 5 set "Bottom" and "Top" and "Middle"'
        self._run_script(script)
        lifx = provide(i_controller.Lifx)
        for light in lifx.get_lights():
            if light.get_label() in ('Bottom', 'Middle', 'Top'):
                expected = [('set_color', ([1, 2, 3, 4], 5))]
            else:
                expected = []
            self.assertListEqual(light.call_list(), expected)

    def test_mixed_and(self):
        script = 'units raw hue 10 saturation 20 brightness 30 kelvin 40 '
        script += 'duration 50 set "Table" and group "Pole"'
        self._run_script(script)
        lifx = provide(i_controller.Lifx)
        for light in lifx.get_lights():
            if light.get_label() in ('Top', 'Middle', 'Bottom', 'Table'):
                expected = [('set_color', ([10, 20, 30, 40], 50))]
            else:
                expected = []        
            self.assertListEqual(light.call_list(), expected)


if __name__ == '__main__':
    unittest.main()
