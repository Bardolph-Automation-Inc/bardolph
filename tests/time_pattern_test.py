#!/usr/bin/env python

import unittest

from bardolph.lib.time_pattern import TimePattern


class TimePatternTest(unittest.TestCase):
    def test_regex(self):
        matches = {
            '1:23': ('1', '23'),
            '1:*3': ('1', '*3'),
            '1:2*': ('1', '2*'),
            '1:*': ('1', '*'),

            '11:23': ('11', '23'),
            '11:*3': ('11', '*3'),
            '11:2*': ('11', '2*'),
            '11:*': ('11', '*'),

            '1*:23': ('1*', '23'),
            '1*:*3': ('1*', '*3'),
            '1*:2*': ('1*', '2*'),
            '1*:*': ('1*', '*'),

            '*1:23': ('*1', '23'),
            '*1:*3': ('*1', '*3'),
            '*1:2*': ('*1', '2*'),
            '*1:*': ('*1', '*'),

            '*:23': ('*', '23'),
            '*:*3': ('*', '*3'),
            '*:2*': ('*', '2*'),
            '*:*': ('*', '*'),
        }
        for key in matches.keys():
            actual_groups = TimePattern.REGEX.match(key).groups()
            expected = (*matches[key], '')
            self.assertTupleEqual(expected, actual_groups)

        non_matches = (
            '111:23', '11*:23', '**:23', '1:23*', '1:23*m', '1:**', '11:2')
        for non_match in non_matches:
            self.assertIsNone(TimePattern.REGEX.match(non_match))

    def test_hours_valid(self):
        good_hours = [
            '*1', '*2', '1*', '2*', '10', '1', '2', '4', '19', '9', '*'
        ]
        for hour in good_hours:
            self.assertTrue(TimePattern.hours_valid(hour))

        bad_hours = ['3*', '25', '123', '**', '*a', '1a']
        for hour in bad_hours:
            self.assertFalse(TimePattern.hours_valid(hour), hour)

    def test_minutes_valid(self):
        good_minutes = [
            '*1', '*2', '1*', '2*', '10', '01', '02', '04', '19', '59', '*'
        ]
        for minute in good_minutes:
            self.assertTrue(TimePattern.minutes_valid(minute), minute)

        bad_minutes = ['6*', '60', '123', '**', '*a', '1a']
        for minute in bad_minutes:
            self.assertFalse(TimePattern.minutes_valid(minute), minute)

    def test_patterns(self):
        pattern = TimePattern('*3', '0*')
        self.assertTrue(pattern.match(3, 0))
        self.assertTrue(pattern.match(13, 1))
        self.assertTrue(pattern.match(23, 2))
        self.assertFalse(pattern.match(23, 10))

        pattern = TimePattern('1*', '*5')
        self.assertTrue(pattern.match(10, 5))
        self.assertTrue(pattern.match(11, 15))
        self.assertTrue(pattern.match(12, 45))
        self.assertFalse(pattern.match(1, 5))
        self.assertFalse(pattern.match(10, 50))

        pattern = TimePattern('11', '*')
        self.assertTrue(pattern.match(11, 5))
        self.assertTrue(pattern.match(11, 15))
        self.assertTrue(pattern.match(11, 45))
        self.assertFalse(pattern.match(1, 5))

        pattern = TimePattern('*', '05')
        self.assertTrue(pattern.match(11, 5))
        self.assertTrue(pattern.match(12, 5))
        self.assertTrue(pattern.match(23, 5))
        self.assertFalse(pattern.match(1, 50))

        pattern = TimePattern('*', '00')
        self.assertTrue(pattern.match(1, 0))
        self.assertTrue(pattern.match(12, 0))
        self.assertTrue(pattern.match(23, 0))
        self.assertFalse(pattern.match(23, 1))
        self.assertFalse(pattern.match(24, 0))

        pattern = TimePattern('12', '*')
        self.assertTrue(pattern.match(12, 0))

    def test_union(self):
        merged = TimePattern('*3', '0*')
        pattern = TimePattern('1*', '*5')
        pattern.union(merged)

        self.assertTrue(pattern.match(3, 0))
        self.assertTrue(pattern.match(13, 1))
        self.assertTrue(pattern.match(23, 2))
        self.assertFalse(pattern.match(23, 10))

        self.assertTrue(pattern.match(10, 5))
        self.assertTrue(pattern.match(11, 15))
        self.assertTrue(pattern.match(12, 45))
        self.assertFalse(pattern.match(1, 5))
        self.assertFalse(pattern.match(10, 50))


if __name__ == '__main__':
    unittest.main()
