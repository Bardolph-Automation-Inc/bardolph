#!/usr/bin/env python

import unittest

from bardolph.lib.noneable import noneable

class NoneableTest(unittest.TestCase):
    @noneable
    def fn(self, param):
        self.assertIsNotNone(param)
        return param * 2

    @noneable
    def fn_kw(self, param):
        self.assertIsNotNone(param)
        return param * 2

    def test_with_none(self):
        actual = self.fn(None)
        self.assertIsNone(actual)

    def test_without_none(self):
        actual = self.fn(5)
        self.assertEqual(actual, 10)

    def test_with_none_kw(self):
        actual = self.fn_kw(param=None)
        self.assertIsNone(actual)
        actual = self.fn(5, param=None)
        self.assertIsNone(actual)

    def test_without_none_kw(self):
        actual = self.fn_kw(param=15)
        self.assertEqual(actual, 30)


if __name__ == '__main__':
    unittest.main()
