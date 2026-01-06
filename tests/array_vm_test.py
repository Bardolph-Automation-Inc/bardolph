#!/usr/bin/env python

import unittest

from bardolph.vm.array import Array


class ArrayVmTest(unittest.TestCase):
    def test_vector(self):
        array = Array()
        array.add_dimension(25)
        cursor = array.base()
        cursor.index(5)
        cursor.set_value(100)
        cursor = array.base()
        cursor.index(5)
        self.assertEqual(100, cursor.get_value())

    def test_matrix2(self):
        # 5 x 10
        array = Array()
        array.add_dimension(5)
        array.add_dimension(10)

        # assign 100 to the element at [1][2]
        cursor = array.base()
        cursor.index(1)
        cursor.index(2)
        cursor.set_value(100)

        # assign 200 to the element at [4][7]
        cursor = array.base()
        cursor.index(4)
        cursor.index(7)
        cursor.set_value(200)

        cursor = array.base()
        cursor.base()
        cursor.index(1)
        cursor.index(2)
        self.assertEqual(100, cursor.get_value())

        cursor = array.base()
        cursor.index(4)
        cursor.index(7)
        self.assertEqual(200, cursor.get_value())


if __name__ == '__main__':
    unittest.main()
