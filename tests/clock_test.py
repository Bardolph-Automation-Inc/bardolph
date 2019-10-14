#!/usr/bin/env python3

import unittest

from bardolph.lib import clock, injection, settings

class ClockTest(unittest.TestCase):
    def setUp(self):
        injection.configure()
        self._precision = 0.1
        settings.using_base({'sleep_time': self._precision}).configure()

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

if __name__ == '__main__':
    unittest.main()
