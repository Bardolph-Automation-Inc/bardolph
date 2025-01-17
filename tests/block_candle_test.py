#!/usr/bin/env python

import unittest

from bardolph.lib import i_lib, injection
from tests import test_module
from tests.script_runner import ScriptRunner


class BlockCandleTest(unittest.TestCase):
    def setUp(self):
        test_module.configure()
        current_settings = injection.provide(i_lib.Settings)
        if current_settings.get_value('use_fakes', True):
            self._time_code = 'time 0\n'
        else:
            self._time_code = 'time 2\n'
        self._default_color = [1, 2, 3, 4]
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
            set "Candle" begin
                hue 120 saturation 50 brightness 25 kelvin 2500
                stage row 1 2 column 3 4
                stage row 0 1 column 0 1
            end
        """
        runner = ScriptRunner(self)
        runner.run_script(script)

        c = [120, 50, 25, 2500]
        d = self._default_color
        expected = (
            c, c, d, d, d,
            c, c, d, c, c,
            d, d, d, c, c,
            d, d, d, d, d,
            d, d, d, d, d,
            d, d, d, d, d
        )
        runner.check_final_matrix('Candle', expected)

    def test_row_only(self):
        script = self._default_code + """
            define test_name "test_row_only"
            hue 120 saturation 80 brightness 20 kelvin 2700
            set "Candle" begin
                stage row 1
                stage row 4
            end
        """
        runner = ScriptRunner(self)
        runner.run_script(script)

        c = [120, 80, 20, 2700]
        d = self._default_color
        expected = (
            d, d, d, d, d,
            c, c, c, c, c,
            d, d, d, d, d,
            d, d, d, d, d,
            c, c, c, c, c,
            d, d, d, d, d
        )
        runner.check_final_matrix('Candle', expected)

    def test_all_rows(self):
        script = self._default_code + """
            define test_name "test_all_rows"
            hue 240 saturation 80 brightness 20 kelvin 2700
            set "Candle" begin
                stage row 0 1
                stage row 2
                stage row 3 4
                stage row 5
            end
        """
        runner = ScriptRunner(self)
        runner.run_script(script)

        c = [240, 80, 20, 2700]
        i = self._default_color
        expected = (
            c, c, c, c, c,
            c, c, c, c, c,
            c, c, c, c, c,
            c, c, c, c, c,
            c, c, c, c, c,
            c, c, c, c, c
        )
        runner.check_final_matrix('Candle', expected)

    def test_column_only(self):
        script = self._default_code + """
            define test_name "test_column_only"
            hue 120 saturation 80 brightness 30
            set "Candle" begin
                stage column 2
            end
        """
        runner = ScriptRunner(self)
        runner.run_script(script)

        c = [120, 80, 30, 0]
        i = self._default_color
        expected = (
            i, i, c, i, i,
            i, i, c, i, i,
            i, i, c, i, i,
            i, i, c, i, i,
            i, i, c, i, i,
            i, i, c, i, i
        )
        runner.check_final_matrix('Candle', expected)

    def test_row_column(self):
        script = self._default_code + """
            define test_name "test_row_column"
            hue 0 saturation 80 brightness 30
            set "Candle" begin
                stage row 0
                stage column 2 3
            end

            # Resets to default.
            set "Candle" begin
                stage column 3 4 row 2 3
            end
        """
        c = [0, 80, 30, 0]
        d = self._default_color
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
        runner.check_final_matrix('Candle', expected)

    def test_top_down(self):
        script = self._default_code + """
            define test_name "test_top_down"
            hue 200 saturation 50 brightness 20 kelvin 2700 duration 2 time 2
            define top_down	begin
                set "Candle" begin
                    repeat with row_num from 0 to 5
                        stage row row_num
                end
            end
            top_down
        """
        c = [200, 50, 20, 2700]
        z = [0] * 4
        expected = (
            c, c, c, c, c,
            c, c, c, c, c,
            c, c, c, c, c,
            c, c, c, c, c,
            c, c, c, c, c,
            c, c, c, c, c
        )
        runner = ScriptRunner(self)
        runner.run_script(script)
        runner.check_final_matrix('Candle', expected)

    def test_simple_loop(self):
        script = self._default_code + """
            define test_name "test_simple_loop"
            saturation 100 brightness 25 kelvin 35

            set "Candle" begin
                hue 0
                repeat with row_num from 1 to 3 begin
                    stage row row_num column 1
                    hue {hue + 60}
                end
            end
        """
        d = self._default_color
        expected = (
            d, d, d, d, d,
            d, [0, 100, 25, 35], d, d, d,
            d, [60, 100, 25, 35], d, d, d,
            d, [120, 100, 25, 35], d, d, d,
            d, d, d, d, d,
            d, d, d, d, d
        )
        runner = ScriptRunner(self)
        runner.run_script(script)
        runner.check_final_matrix('Candle', expected)

    def test_loop_break(self):
        script = self._default_code + """
            define test_name "test_simple_loop"
            saturation 100 brightness 25 kelvin 35

            set "Candle" begin
                hue 0
                repeat with row_num from 1 to 3 begin
                    if {row_num == 3}
                        break
                    stage row row_num column 1
                    hue {hue + 60}
                end
            end
        """
        d = self._default_color
        expected = (
            d, d, d, d, d,
            d, [0, 100, 25, 35], d, d, d,
            d, [60, 100, 25, 35], d, d, d,
            d, d, d, d, d,
            d, d, d, d, d,
            d, d, d, d, d
        )
        runner = ScriptRunner(self)
        runner.run_script(script)
        runner.check_final_matrix('Candle', expected)

    def test_routine_call(self):
        script = self._default_code + """
            define test_name "test_routine_call"
            hue 0 saturation 80 brightness 30

            define do_stage with start_row end_row start_col end_col begin
                stage row start_row end_row column start_col end_col
            end

            set "Candle" begin
                do_stage 0 1 3 4
            end
        """
        c = [0, 80, 30, 0]
        d = self._default_color
        expected = (
            d, d, d, c, c,
            d, d, d, c, c,
            d, d, d, d, d,
            d, d, d, d, d,
            d, d, d, d, d,
            d, d, d, d, d
        )
        runner = ScriptRunner(self)
        runner.run_script(script)
        runner.check_final_matrix('Candle', expected)


if __name__ == '__main__':
    unittest.main()
