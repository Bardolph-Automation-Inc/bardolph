#!/usr/bin/env python

import copy
import unittest

from bardolph.controller.color_matrix import ColorMatrix, Rect

# colors
a = [1, 2, 3, 4]
b = [10, 20, 30, 40]
c = [100, 200, 300, 400]
d = [1000, 2000, 3000, 4000]
e = [10000, 20000, 30000, 40000]
f = [51000, 52000, 53000, 54000]
x = [123, 456, 789, 1011]


def iterable_srce():
    return [
        a, b, c, d, e,
        b, c, d, e, f,
        c, d, e, f, a,
        d, e, f, a, b,
        e, f, a, b, c,
        f, a, b, c, d
    ]


class ColorMatrixTest(unittest.TestCase):
    def test_round_trip(self):
        srce = iterable_srce()
        mat = ColorMatrix.new_from_iterable(6, 5, srce)
        returned = mat.as_list()
        self.assertListEqual(srce, returned)

    def test_overlay(self):
        expected = [
            a, b, c, d, e,
            b, x, x, x, x,
            c, x, x, x, x,
            d, x, x, x, x,
            e, f, a, b, c,
            f, a, b, c, d
        ]
        mat = ColorMatrix.new_from_iterable(6, 5, iterable_srce())
        mat.overlay_color(Rect(1, 3, 1, 4), x)
        actual = mat.as_list()
        self.assertListEqual(expected, actual)

    def test_new_from_constant(self):
        expected = [
            a, a, a, a, a,
            a, a, a, a, a,
            a, a, a, a, a,
            a, a, a, a, a,
            a, a, a, a, a,
            a, a, a, a, a
        ]
        mat = ColorMatrix.new_from_constant(6, 5, a)
        actual = mat.as_list()
        self.assertListEqual(expected, actual)

    def test_str(self):
        test_data = [
            a, a, a, a, a,
            a, a, a, a, a,
            a, a, None, a, a,
            a, a, a, a, a,
            a, a, a, a, a,
            a, a, a, a, a
        ]
        mat = ColorMatrix.new_from_iterable(6, 5, test_data)
        self.assertIsNotNone(str(mat))

    def test_new_from_iterable(self):
        expected = iterable_srce()
        mat = ColorMatrix.new_from_iterable(6, 5, iterable_srce())
        actual = mat.as_list()
        self.assertListEqual(expected, actual)

    def test_set_from_constant(self):
        expected = [
            a, a, a, a, a,
            a, a, a, a, a,
            a, a, a, a, a,
            a, a, a, a, a,
            a, a, a, a, a,
            a, a, a, a, a
        ]
        mat = ColorMatrix(6, 5)
        mat.set_from_constant(a)
        actual = mat.as_list()
        self.assertListEqual(expected, actual)

    def test_normalize_rect(self):
        matrix = ColorMatrix(6, 5)

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
