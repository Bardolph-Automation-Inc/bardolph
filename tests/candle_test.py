#!/usr/bin/env python

import copy
import unittest

from bardolph.controller import i_controller
from bardolph.controller.candle_color_matrix import CandleColorMatrix
from bardolph.lib import i_lib, injection
from tests import test_module
from tests.script_runner import ScriptRunner


class CandleTest(unittest.TestCase):
    def setUp(self):
        test_module.configure()
        current_settings = injection.provide(i_lib.Settings)
        if current_settings.get_value('use_fakes', True):
            self._time_code = 'time 0 '
        else:
            self._time_code = 'time 2 '
        self._matrix_init_color = current_settings.get_value(
            'matrix_init_color', [-1] * 4)

    def _assert_all_colors(self, light, color):
        mat = light.get_matrix()
        for actual_color in mat.as_list():
            self.assertListEqual(color, actual_color)

    def test_set_as_generic(self):
        color = [0, 20000, 8192, 2700]
        light_set = injection.provide(i_controller.LightSet)
        light = light_set.get_light("Candle")
        light.set_color(color, 0)

    def test_set_all(self):
        light_set = injection.provide(i_controller.LightSet)
        light = light_set.get_light("Candle")
        mat = CandleColorMatrix()
        color = [16000, 50000, 8192, 2700]
        mat.set_body(color)
        mat.set_top(color)
        light.set_matrix(mat, 0)

    def test_minimal(self):
        script = self._time_code + """
            define test_name "test_minimal"
            units raw
            hue 120 saturation 50 brightness 25 kelvin 2500
            set "Candle" row 1 2 column 3 4 top
        """
        runner = ScriptRunner(self)
        runner.run_script(script)

        color = [120, 50, 25, 2500]
        i = self._matrix_init_color
        z = [0] * 4
        expected = (
            color, z, z, z, z,
            i, i, i, i, i,
            i, i, i, color, color,
            i, i, i, color, color,
            i, i, i, i, i,
            i, i, i, i, i
        )
        runner.check_final_matrix('Candle', expected)

    def test_row_only(self):
        script = self._time_code + """
            define test_name "test_row_only"
            units raw
            hue 120 saturation 80 brightness 20 kelvin 2700
            set "Candle" row 4
        """
        runner = ScriptRunner(self)
        runner.run_script(script)

        c = [120, 80, 20, 2700]
        i = self._matrix_init_color
        expected = (
            i, i, i, i, i,
            i, i, i, i, i,
            i, i, i, i, i,
            i, i, i, i, i,
            i, i, i, i, i,
            c, c, c, c, c
        )
        runner.check_final_matrix('Candle', expected)

    def test_all_rows(self):
        script = self._time_code + """
            define test_name "test_all_rows"
            units raw
            hue 240 saturation 80 brightness 20 kelvin 2700
            set "Candle" row 0 4
        """
        runner = ScriptRunner(self)
        runner.run_script(script)

        c = [240, 80, 20, 2700]
        i = self._matrix_init_color
        expected = (
            i, i, i, i, i,
            c, c, c, c, c,
            c, c, c, c, c,
            c, c, c, c, c,
            c, c, c, c, c,
            c, c, c, c, c
        )
        runner.check_final_matrix('Candle', expected)

    def test_column_only(self):
        script = self._time_code + """
            define test_name "test_column_only"
            units raw
            hue 120 saturation 80 brightness 30
            set "Candle" column 2
        """
        runner = ScriptRunner(self)
        runner.run_script(script)

        c = [120, 80, 30, 0]
        i = self._matrix_init_color
        expected = (
            i, i, i, i, i,
            i, i, c, i, i,
            i, i, c, i, i,
            i, i, c, i, i,
            i, i, c, i, i,
            i, i, c, i, i
        )
        runner.check_final_matrix('Candle', expected)

    def test_top_only(self):
        script = self._time_code + """
            define test_name "test_top_only"
            units raw
            hue 180 saturation 80 brightness 30
            set "Candle" top
        """
        runner = ScriptRunner(self)
        runner.run_script(script)

        c = [180, 80, 30, 0]
        i = self._matrix_init_color
        z = [0] * 4
        expected = (
            c, z, z, z, z,
            i, i, i, i, i,
            i, i, i, i, i,
            i, i, i, i, i,
            i, i, i, i, i,
            i, i, i, i, i
        )
        runner.check_final_matrix('Candle', expected)

    def test_row_with_top(self):
        script = self._time_code + """
            define test_name "test_row_with_top"
            units raw
            hue 240 saturation 80 brightness 30
            set "Candle" row 0 1 top
        """
        runner = ScriptRunner(self)
        runner.run_script(script)

        c = [240, 80, 30, 0]
        i = self._matrix_init_color
        z = [0] * 4
        expected = (
            c, z, z, z, z,
            c, c, c, c, c,
            c, c, c, c, c,
            i, i, i, i, i,
            i, i, i, i, i,
            i, i, i, i, i
        )
        runner.check_final_matrix('Candle', expected)

    def test_column_with_top(self):
        script = self._time_code + """
            define test_name "test_column_with_top"
            units raw
            hue 300 saturation 80 brightness 30
            set "Candle" top column 0 1
        """
        runner = ScriptRunner(self)
        runner.run_script(script)

        c = [300, 80, 30, 0]
        i = self._matrix_init_color
        z = [0] * 4
        expected = (
            c, z, z, z, z,
            c, c, i, i, i,
            c, c, i, i, i,
            c, c, i, i, i,
            c, c, i, i, i,
            c, c, i, i, i
        )
        runner.check_final_matrix('Candle', expected)

    def test_row_column(self):
        script = self._time_code + """
            define test_name "test_row_column"
            units raw
            hue 0 saturation 80 brightness 30
            set "Candle" row 0 column 2 3
            set "Candle" column 3 4 row 2 3
        """
        runner = ScriptRunner(self)
        runner.run_script(script)

        c = [0, 80, 30, 0]
        i = self._matrix_init_color
        expected = (
            i, i, i, i, i,
            i, i, c, c, i,
            i, i, i, i, i,
            i, i, i, c, c,
            i, i, i, c, c,
            i, i, i, i, i
        )
        runner.check_final_matrix('Candle', expected)

    def test_top_down(self):
        script = self._time_code + """
            define test_name "test_top_down"
            units raw
            hue 200 saturation 50 brightness 20 kelvin 2700 duration 2 time 2
            define top_down	begin
                set "Candle" top
                set "Candle" top row 0
                set "Candle" top row 0 1
                set "Candle" top row 0 2
                set "Candle" top row 0 3
                set "Candle" top row 0 4
            end
            top_down
        """
        runner = ScriptRunner(self)
        runner.run_script(script)

        c = [200, 50, 20, 2700]
        z = [0] * 4
        expected = (
            c, z, z, z, z,
            c, c, c, c, c,
            c, c, c, c, c,
            c, c, c, c, c,
            c, c, c, c, c,
            c, c, c, c, c
        )
        runner.check_final_matrix('Candle', expected)

    def test_row_column_top(self):
        script = self._time_code + """
            define test_name "test_row_column_top"
            units raw
            hue 220 saturation 60 brightness 70 kelvin 2900
            set "Candle" row 0 top column 1 2

            # Equivalent to:
            set "Candle" row 0
            set "Candle" top
            set "Candle" column 1 2

        """
        runner = ScriptRunner(self)
        runner.run_script(script)

        c = [220, 60, 70, 2900]
        i = self._matrix_init_color
        z = [0] * 4
        expected = (
            c, z, z, z, z,
            c, c, c, c, c,
            i, c, c, i, i,
            i, c, c, i, i,
            i, c, c, i, i,
            i, c, c, i, i
        )
        runner.check_final_matrix('Candle', expected)

    def test_simple_loop(self):
        script = """
            define test_name "test_simple_loop"
            units raw
            saturation 100 brightness 25
            duration 2

            hue 0
            repeat with _row from 0 to 4 begin
                set "Candle" row _row
                hue {hue + 60}
            end
        """
        runner = ScriptRunner(self)
        runner.run_script(script)

    def test_begin_end(self):
        script = """
            define test_name "test_begin_end"
            units raw
            set "Candle" begin
                assign x 34
                hue 120 saturation 50
                set row 1 2 column 3 4 top
                brightness {1 + 5}
                kelvin {32 * x}
                set row 1
            end
        """
        runner = ScriptRunner(self)
        runner.run_script(script)

    def test_begin_end_break(self):
        script = """
            define test_name "test_begin_end_break"
            units raw
            hue 120 saturation 50
            set "Candle" begin
                # bug get all
                assign i 0
                repeat begin
                    if {i > 3}
                        break
                    assign i {i + 1}
                end
                set row i
            end
        """
        runner = ScriptRunner(self)
        runner.run_script(script)


if __name__ == '__main__':
    unittest.main()
