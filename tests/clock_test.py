#!/usr/bin/env python3

import unittest

from bardolph.lib import clock, injection, settings

class ClockTest(unittest.TestCase):
    def setUp(self):
        injection.configure()
        precision = 0.1
        tolerance = 0.0075
        self.min = precision - tolerance
        self.max = precision + tolerance

        settings.using_base({'sleep_time': precision}).configure()
        
    def test_clock(self):
        c = clock.Clock()
        c.start()
        t0 = c.et()
        for _ in range(1, 10):
            c.wait()
            t1 = c.et()
            delta = t1 - t0
            self.assertTrue(delta > self.min and delta < self.max)
            t0 = t1
        c.stop()

if __name__ == '__main__':
    unittest.main()
