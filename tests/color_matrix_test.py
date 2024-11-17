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


def test_mat():
    return copy.deepcopy([
        a, b, c, d, e,
        b, c, d, e, f,
        c, d, e, f, a,
        d, e, f, a, b,
        e, f, a, b, c,
        f, a, b, c, d
    ])


class ColorMatrixTest(unittest.TestCase):
    def test_round_trip(self):
        srce = test_mat()
        mat = ColorMatrix.new_from_iterable(srce, 6, 5)
        returned = mat.as_list()
        self.assertListEqual(srce, returned, "ColorMatrix round trip")

    def test_overlay(self):
        expected = [
            a, b, c, d, e,
            b, x, x, x, x,
            c, x, x, x, x,
            d, x, x, x, x,
            e, f, a, b, c,
            f, a, b, c, d
        ]

        mat = ColorMatrix.new_from_iterable(test_mat(), 6, 5)
        mat.overlay_color(Rect(1, 3, 1, 4), x)
        actual = mat.as_list()
        self.assertListEqual(expected, actual, "ColorMatrix overlay")


if __name__ == '__main__':
    unittest.main()
