#!/usr/bin/env python

import unittest

from bardolph.controller.candle_color_matrix import CandleColorMatrix
from bardolph.controller.color_matrix import Rect
from tests.color_matrix_test import a, b, c, create_test_mat, d, e, f


class CandleColorMatrixTest(unittest.TestCase):
    def test_new_from_iterable(self):
        expected = [
            a, b, c, d, e,
            b, c, d, e, f,
            c, d, e, f, a,
            d, e, f, a, b,
            e, f, a, b, c,
            f, a, b, c, d
        ]
        mat = CandleColorMatrix.new_from_iterable(create_test_mat())
        actual = mat.as_list()
        self.assertListEqual(expected, actual, "CandleColorMatrix overlay")

    def test_set_from_constant(self):
        expected = [
            a, a, a, a, a,
            a, a, a, a, a,
            a, a, a, a, a,
            a, a, a, a, a,
            a, a, a, a, a,
            a, a, a, a, a
        ]
        mat = CandleColorMatrix.new_from_constant(a)
        actual = mat.as_list()
        self.assertListEqual(expected, actual, "CandleColorMatrix set all")

    def test_normalize_rect(self):
        matrix = CandleColorMatrix()

        rect = Rect(None, None, 1, 2)
        self.assertEqual(matrix._normalize_rect(rect), Rect(0, 5, 1, 2))
        rect = Rect(None, 1, 3, 4)
        self.assertEqual(matrix._normalize_rect(rect), Rect(1, 1, 3, 4))
        rect = Rect(2, None, 5, 6)
        self.assertEqual(matrix._normalize_rect(rect), Rect(2, 2, 5, 6))

        rect = Rect(1, 2, None, None)
        self.assertEqual(matrix._normalize_rect(rect), Rect(1, 2, 0, 4))
        rect = Rect(1, 3, None, 4)
        self.assertEqual(matrix._normalize_rect(rect), Rect(1, 3, 4, 4))
        rect = Rect(2, 5, 6, None)
        self.assertEqual(matrix._normalize_rect(rect), Rect(2, 5, 6, 6))


if __name__ == '__main__':
    unittest.main()
