#!/usr/bin/env python

import unittest

from bardolph.lib import settings

base = {
    'one': 1,
    'two': 2
}

override = {
    'two': 22,
    'four': 4
}

class SettingsTest(unittest.TestCase):
    def test_base(self):
        settings.using(base).configure()
        s = settings.Settings()
        self.assertEqual(1, s.get_value('one'))
        self.assertEqual(2, s.get_value('two'))

    def test_override(self):
        settings.using(base).add_overrides(override).configure()
        s = settings.Settings()
        self.assertEqual(1, s.get_value('one'))
        self.assertEqual(22, s.get_value('two'))
        self.assertEqual(4, s.get_value('four'))

    def test_apply_file(self):
        settings.using(base).apply_file('tests/test_apply_file.ini').configure()
        s = settings.Settings()
        self.assertEqual('11', s.get_value('one'))
        self.assertEqual('22', s.get_value('two'))


if __name__ == '__main__':
    unittest.main()
