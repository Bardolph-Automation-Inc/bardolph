#!/usr/bin/env python

import unittest

from tests import print_driven_test, test_module
from tests.script_runner import ScriptRunner


class GetTest(print_driven_test.PrintDrivenTest):
    def setUp(self):
        test_module.configure()
        self._runner = ScriptRunner(self)
        self.post_setup()

    def test_bulb(self):
        script = """
            hue 11 saturation 22 brightness 33 kelvin 2500 set "Top"
            hue 0 saturation 0 brightness 0 kelvin 0
            get "Top"
            printf "{hue:.0f} {saturation:.0f} {brightness:.0f} {kelvin:.0f}"
        """
        self.run_and_check(script, "11 22 33 2500")

    def test_multizone(self):
        script = """
            hue 10 saturation 20 brightness 30 kelvin 40
            set "Strip" zone 5
            hue 0 saturation 0 brightness 0 kelvin 0
            get "Strip" zone 5
            printf "{hue:.0f} {saturation:.0f} {brightness:.0f} {kelvin:.0f}"
        """
        self.run_and_check(script, "10 20 30 40")

    def test_multizone_unaffected(self):
        script = """
            hue 0 saturation 0 brightness 0 kelvin 0
            set "Strip"

            hue 10 saturation 20 brightness 30 kelvin 40
            set "Strip" zone 5

            hue 0 saturation 0 brightness 0 kelvin 0
            get "Strip" zone 7

            printf "{hue:.0f} {saturation:.0f} {brightness:.0f} {kelvin:.0f}"
        """
        self.run_and_check(script, "0 0 0 0")

    def test_multizone_as_bulb(self):
        script = """
            hue 15 saturation 25 brightness 35 kelvin 45
            set "Strip" zone 5
            hue 0 saturation 0 brightness 0 kelvin 0
            get "Strip"
            printf "{hue:.0f} {saturation:.0f} {brightness:.0f} {kelvin:.0f}"

            hue 25 saturation 35 brightness 45 kelvin 55
            set "Strip"
            hue 0 saturation 0 brightness 0 kelvin 0
            get "Strip"
            printf "{hue:.0f} {saturation:.0f} {brightness:.0f} {kelvin:.0f}"

            hue 26 saturation 36 brightness 46 kelvin 56
            set "Strip" zone 0
            hue 0 saturation 0 brightness 0 kelvin 0
            get "Strip"
            printf "{hue:.0f} {saturation:.0f} {brightness:.0f} {kelvin:.0f}"
        """
        self.run_and_check(script, ['0 0 0 0', '25 35 45 55', '26 36 46 56'])


if __name__ == '__main__':
    unittest.main()
