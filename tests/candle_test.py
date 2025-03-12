#!/usr/bin/env python

import unittest

from bardolph.lib import i_lib, injection
from tests import test_module
from tests.script_runner import ScriptRunner


class CandleTest(unittest.TestCase):
    def setUp(self):
        test_module.configure()
        current_settings = injection.provide(i_lib.Settings)
        if current_settings.get_value('use_fakes', True):
            self._time_code = 'time 0\n'
        else:
            self._time_code = 'time 2\n'
        self._default_code = (self._time_code +
            'units raw\n'
            'hue 1 saturation 2 brightness 3 kelvin 4 set default\n'
            'hue 0 saturation 0 brightness 0 kelvin 0\n')

    def _assert_all_colors(self, light, color):
        mat = light.get_matrix()
        for actual_color in mat.as_list():
            self.assertListEqual(color, actual_color)

    def test_minimal(self):
        script = self._default_code + """
            define test_name "test_minimal"

            hue 0 saturation 0 brightness 0 kelvin 0
            set default

            hue 120 saturation 50 brightness 25 kelvin 2500
            set "Candle" row 1 2 column 3 4
        """
        runner = ScriptRunner(self)
        runner.run_script(script)

        c = [120, 50, 25, 2500]
        d = [0, 0, 0, 0]
        expected = (
            d, d, d, d, d,
            d, d, d, c, c,
            d, d, d, c, c,
            d, d, d, d, d,
            d, d, d, d, d,
            d, d, d, d, d
        )
        runner.check_final_matrix('Candle', 6, 5, expected)

    def test_row_only(self):
        script = self._default_code + """
            define test_name "test_row_only"

            hue 0 saturation 0 brightness 0 kelvin 0
            set default

            hue 120 saturation 80 brightness 20 kelvin 2700
            set "Candle" row 4
        """
        runner = ScriptRunner(self)
        runner.run_script(script)

        c = [120, 80, 20, 2700]
        d = [0, 0, 0, 0]
        expected = (
            d, d, d, d, d,
            d, d, d, d, d,
            d, d, d, d, d,
            d, d, d, d, d,
            c, c, c, c, c,
            d, d, d, d, d
        )
        runner.check_final_matrix('Candle', 6, 5, expected)

    def test_all_rows(self):
        script = self._default_code + """
            define test_name "test_all_rows"
            hue 240 saturation 80 brightness 20 kelvin 2700
            set "Candle" row 0 5
        """
        runner = ScriptRunner(self)
        runner.run_script(script)

        c = [240, 80, 20, 2700]
        expected = (
            c, c, c, c, c,
            c, c, c, c, c,
            c, c, c, c, c,
            c, c, c, c, c,
            c, c, c, c, c,
            c, c, c, c, c
        )
        runner.check_final_matrix('Candle', 6, 5, expected)

    def test_column_only(self):
        script = self._default_code + """
            define test_name "test_column_only"

            hue 0 saturation 0 brightness 0 kelvin 0
            set default

            hue 120 saturation 80 brightness 30
            set "Candle" column 2
        """
        runner = ScriptRunner(self)
        runner.run_script(script)

        c = [120, 80, 30, 0]
        d = [0, 0, 0, 0]
        expected = (
            d, d, c, d, d,
            d, d, c, d, d,
            d, d, c, d, d,
            d, d, c, d, d,
            d, d, c, d, d,
            d, d, c, d, d
        )
        runner.check_final_matrix('Candle', 6, 5, expected)

    def test_row_column(self):
        script = self._default_code + """
            define test_name "test_row_column"

            hue 0 saturation 0 brightness 0 kelvin 0
            set default

            hue 0 saturation 80 brightness 30
            set "Candle" row 0 column 2 3

            # Resets row 0 column 2 3 default.
            set "Candle" column 3 4 row 2 3
        """
        c = [0, 80, 30, 0]
        d = [0, 0, 0, 0]
        expected = (
            d, d, d, d, d,
            d, d, d, d, d,
            d, d, d, c, c,
            d, d, d, c, c,
            d, d, d, d, d,
            d, d, d, d, d
        )
        runner = ScriptRunner(self)
        runner.run_script(script)
        runner.check_final_matrix('Candle', 6, 5, expected)

    def test_rgb(self):
        script = """
            define test_name "test_rgb"

            units raw
            hue 10 saturation 20 brightness 30 kelvin 40
            set default

            units rgb
            red 50 green 50 blue 50 kelvin 0

            set "Candle" row 2 3 column 2 3
        """
        d = [10, 20, 30, 40]
        r = [0, 0, 32768, 0]
        expected = (
            d, d, d, d, d,
            d, d, d, d, d,
            d, d, r, r, d,
            d, d, r, r, d,
            d, d, d, d, d,
            d, d, d, d, d
        )
        runner = ScriptRunner(self)
        runner.run_script(script)
        runner.check_final_matrix('Candle', 6, 5, expected)

if __name__ == '__main__':
    unittest.main()
