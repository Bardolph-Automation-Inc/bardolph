#!/usr/bin/env python

import unittest
from bardolph.lib.sorted_list import SortedList

class SortedListTest(unittest.TestCase):
    def setUp(self):
        self._list = SortedList()
        for value in ('b', 'c', 'a', 'c', 'd'):
            self._list.add(value)

    def test_forward(self):
        self.assertEqual(self._list.first(), 'a')
        self.assertEqual(self._list.next('b'), 'c')
        self.assertIsNone(self._list.next('d'))

        self._list.remove('d')
        self.assertIsNone(self._list.next('d'))
        self.assertIsNone(self._list.next('c'))

        self._list.remove('b')
        self.assertEqual(self._list.next('b'), 'c')

    def test_reverse(self):
        self.assertEqual(self._list.last(), 'd')
        self.assertEqual(self._list.prev('d'), 'c')
        self.assertIsNone(self._list.prev('a'))

        self._list.remove('a')
        self.assertIsNone(self._list.prev('a'))
        self.assertIsNone(self._list.prev('b'))

        self._list.remove('d')
        self.assertEqual(self._list.prev('d'), 'c')

    def test_empty(self):
        for value in ('c', 'b', 'a', 'd'):
            self._list.remove(value)
        self.assertIsNone(self._list.first())
        self.assertIsNone(self._list.last())
        self._list.add('e')
        self.assertEqual(self._list.first(), 'e')
        self.assertEqual(self._list.last(), 'e')


if __name__ == '__main__':
    unittest.main()
