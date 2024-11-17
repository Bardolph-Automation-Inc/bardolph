#!/usr/bin/env python

import unittest

from bardolph.lib import param_helper


class ParamHelperTest(unittest.TestCase):
    def test_8(self):
        self.assertEqual(param_helper.param_8(-1), 0)
        self.assertEqual(param_helper.param_8(255), 255)
        self.assertEqual(param_helper.param_8(256), 255)
        self.assertEqual(param_helper.param_8(65536), 255)

    def test_16(self):
        self.assertEqual(param_helper.param_16(-1), 0)
        self.assertEqual(param_helper.param_16(65535), 65535)
        self.assertEqual(param_helper.param_16(65536), 65535)
        self.assertEqual(param_helper.param_16(65536), 65535)

    def test_32(self):
        self.assertEqual(param_helper.param_32(-1), 0)
        self.assertEqual(param_helper.param_32(4294967295), 4294967295)
        self.assertEqual(param_helper.param_32(4294967296), 4294967295)

    def test_bool(self):
        self.assertEqual(param_helper.param_bool(-1), 1)
        self.assertEqual(param_helper.param_bool(0), 0)
        self.assertEqual(param_helper.param_bool(1), 1)

    def test_color(self):
        big_color = [128000, 256000, 384000, 512000]
        self.assertListEqual(param_helper.param_color(big_color), [65535] * 4)


if __name__ == '__main__':
    unittest.main()
