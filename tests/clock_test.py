#!/usr/bin/env python

import unittest
from unittest.mock import patch

from bardolph.lib import clock, injection, settings, time_pattern

class MockNow:
    def __init__(self, hour, minute):
        self._hour = hour
        self._minute = minute

    @property
    def hour(self):
        self._minute += 1
        if self._minute == 60:
            self._minute = 0
            self._hour += 1
            if self._hour == 24:
                self._hour = 0
        return self._hour

    @property
    def minute(self):
        return self._minute

    def time_equals(self, hour, minute):
        return hour == self._hour and minute == self._minute


class ClockTest(unittest.TestCase):
    def setUp(self):
        injection.configure()
        self._precision = 0.1
        settings.using({'sleep_time': self._precision}).configure()

    def test_clock(self):
        clk = clock.Clock()
        clk.start()
        time_0 = clk.et()
        for _ in range(1, 10):
            clk.wait()
            time_1 = clk.et()
            delta = time_1 - time_0
            self.assertAlmostEqual(delta, self._precision, 1)
            time_0 = time_1
        clk.stop()

    @patch('bardolph.lib.clock.datetime')
    def test_time_pattern(self, patch_datetime):
        mock_now = MockNow(9, 55)
        patch_datetime.now = lambda: mock_now

        clk = clock.Clock()
        clk.start()

        clk.wait_until(time_pattern.TimePattern.from_string('10:*'))
        self.assertTrue(mock_now.time_equals(10, 0))

        clk.wait_until(time_pattern.TimePattern.from_string('10:1*'))
        self.assertTrue(mock_now.time_equals(10, 10))

        clk.wait_until(time_pattern.TimePattern.from_string('10:*5'))
        self.assertTrue(mock_now.time_equals(10, 15))

        clk.stop()


if __name__ == '__main__':
    unittest.main()
