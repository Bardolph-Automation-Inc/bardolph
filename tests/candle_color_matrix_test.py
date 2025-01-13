#!/usr/bin/env python

import unittest

from bardolph.controller.candle_color_matrix import CandleColorMatrix
from bardolph.controller.color_matrix import Rect
from tests.color_matrix_test import a, b, c, d, e, f, x, create_test_mat


_zeroes = [0] * 4


class CandleColorMatrixTest(unittest.TestCase):
    def test_set_tip(self):
        expected = [
            x, _zeroes, _zeroes, _zeroes, _zeroes,
            b, c, d, e, f,
            c, d, e, f, a,
            d, x, x, a, b,
            e, x, x, b, c,
            f, x, x, c, d
        ]
        mat = CandleColorMatrix.new_from_iterable(create_test_mat())
        mat.overlay_color(Rect(2, 4, 1, 2), x)
        mat.set_tip(x)
        actual = mat.as_list()
        self.assertListEqual(expected, actual, "CandleColorMatrix overlay")

    def test_set_body(self):
        expected = [
            a, b, c, d, e,
            x, x, x, x, x,
            x, x, x, x, x,
            x, x, x, x, x,
            x, x, x, x, x,
            x, x, x, x, x
        ]
        mat = CandleColorMatrix.new_from_iterable(create_test_mat())
        mat.set_body(x)
        actual = mat.as_list()
        self.assertListEqual(expected, actual, "CandleColorMatrix set all")


if __name__ == '__main__':
    unittest.main()
