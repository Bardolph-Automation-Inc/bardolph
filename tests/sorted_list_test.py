#!/usr/bin/env python

import unittest
from bardolph.lib.sorted_list import SortedDict, SortedList

class SortedListTest(unittest.TestCase):
    def setUp(self):
        self._list: SortedList[int] = SortedList()
        for value in (10, 30, 20, 50, 40):
            self._list.add(value)

    def test_forward(self):
        lst = self._list
        self.assertEqual(lst.first(), 10)
        self.assertEqual(lst.next(10), 20)
        self.assertEqual(lst.next(30), 40)
        self.assertEqual(lst.next(40), 50)
        self.assertEqual(lst.next(20), 30)
        self.assertIsNone(lst.next(1000))

    def test_reverse(self):
        lst = self._list
        self.assertEqual(lst.last(), 50)
        self.assertIsNone(lst.prev(10))
        self.assertEqual(lst.prev(40), 30)
        self.assertEqual(lst.prev(50), 40)
        self.assertEqual(lst.prev(30), 20)
        self.assertEqual(lst.prev(1000), 50)

    def test_remove(self):
        lst = self._list
        lst.remove(30)
        self.assertListEqual(lst, [10, 20, 40, 50])
        self.assertEqual(lst.next(30), 40)
        self.assertEqual(lst.next(20), 40)
        self.assertEqual(lst.prev(40), 20)
        self.assertEqual(lst.prev(30), 20)


class SortedDictTest(unittest.TestCase):
    def setUp(self):
        lst = self._list = SortedDict()

        lst.add(10, 11)
        lst.add(10, 13)
        lst.add(10, 12)
        lst.add(10, 14)
        lst.add(10, 15)

        lst.add(20, 21)
        lst.add(20, 23)
        lst.add(20, 22)
        lst.add(20, 24)
        lst.add(20, 25)

        lst.add(30, 31)
        lst.add(30, 33)
        lst.add(30, 32)
        lst.add(30, 34)
        lst.add(30, 35)

        lst.add(40, 41)
        lst.add(40, 43)
        lst.add(40, 42)
        lst.add(40, 44)
        lst.add(40, 45)

    def test_remove(self):
        lst = self._list
        lst.remove(30, 32)
        lst.remove(40, 1000)
        actual = lst.get(30)
        self.assertListEqual(actual, [31, 33, 34, 35])
        actual = lst.get(40)
        self.assertListEqual(actual, [41, 42, 43, 44, 45])

    def test_full_remove(self):
        lst = self._list
        lst.remove(40, 45)
        lst.remove(40, 42)
        lst.remove(40, 41)
        lst.remove(40, 43)
        lst.remove(40, 44)
        lst.remove(40, 1000)
        self.assertIsNone(lst.get(40))
        self.assertIsNone(lst.next(30))
        key, value = lst.last()
        self.assertEqual(key, 30)
        self.assertListEqual(value, [31, 32, 33, 34, 35])

        lst.add(40, 50)
        actual = lst.get(40)
        self.assertListEqual(actual, [50])

    def test_remove_all(self):
        self._list.remove_all(30)
        self.assertIsNone(self._list.get(30))

    def test_remove_from_all(self):
        lst = self._list
        lst.add(20, 100)
        lst.add(30, 100)
        lst.add(40, 100)
        lst.add(50, 100)

        self.assertListEqual(lst.get(20), [21, 22, 23, 24, 25, 100])
        self.assertListEqual(lst.get(30), [31, 32, 33, 34, 35, 100])
        self.assertListEqual(lst.get(40), [41, 42, 43, 44, 45, 100])
        self.assertListEqual(lst.get(50), [100])

        lst.remove_from_all(100)
        self.assertListEqual(lst.get(20), [21, 22, 23, 24, 25])
        self.assertListEqual(lst.get(30), [31, 32, 33, 34, 35])
        self.assertListEqual(lst.get(40), [41, 42, 43, 44, 45])
        self.assertIsNone(lst.get(50))

    def test_first(self):
        k, v = self._list.first()
        self.assertEqual(k, 10)
        self.assertListEqual(v, [11, 12, 13, 14, 15])

    def test_last(self):
        k, v = self._list.last()
        self.assertEqual(k, 40)
        self.assertListEqual(v, [41, 42, 43, 44, 45])

    def test_next(self):
        lst = self._list
        actual = lst.next(0)
        self.assertListEqual(actual, [11, 12, 13, 14, 15])
        actual = lst.next(10)
        self.assertListEqual(actual, [21, 22, 23, 24, 25])
        actual = lst.next(20)
        self.assertListEqual(actual, [31, 32, 33, 34, 35])
        actual = lst.next(25)
        self.assertListEqual(actual, [31, 32, 33, 34, 35])
        actual = lst.next(40)
        self.assertIsNone(actual)
        actual = lst.next(41)
        self.assertIsNone(actual)

    def test_prev(self):
        lst = self._list
        actual = lst.prev(0)
        self.assertIsNone(actual)
        actual = lst.prev(30)
        self.assertListEqual(actual, [21, 22, 23, 24, 25])
        actual = lst.prev(35)
        self.assertListEqual(actual, [31, 32, 33, 34, 35])
        actual = lst.prev(1000)
        self.assertListEqual(actual, [41, 42, 43, 44, 45])

    def test_get(self):
        actual = self._list.get(20)
        self.assertListEqual(actual, [21, 22, 23, 24, 25])
        actual = self._list.get(21)
        self.assertIsNone(actual)
        actual = self._list.get(1000)
        self.assertIsNone(actual)

    def test_has(self):
        lst = self._list
        self.assertTrue(lst.has(30, 31))
        self.assertFalse(lst.has(30, 1000))
        self.assertFalse(lst.has(50, 31))

    def test_keys(self):
        lst = self._list

        keys = lst.keys()
        self.assertListEqual(keys, [10, 20, 30, 40])

        lst.remove(40, 45)
        lst.remove(40, 42)
        lst.remove(40, 41)
        lst.remove(40, 43)
        lst.remove(40, 44)
        lst.remove(40, 1000)
        lst.remove_all(20)
        keys = lst.keys()
        self.assertListEqual(keys, [10, 30])

    def test_values(self):
        values = self._list.values()
        self.assertListEqual(values, [
            [11, 12, 13, 14, 15],
            [21, 22, 23, 24, 25],
            [31, 32, 33, 34, 35],
            [41, 42, 43, 44, 45],
        ])


if __name__ == '__main__':
    unittest.main()
