#!/usr/bin/env python

import unittest

from bardolph.fakes.activity_monitor import ActivityMonitor

class ActivityLogTest(unittest.TestCase):
    def setUp(self): pass

    def test_calls(self):
        activities = ActivityMonitor()
        activities.log_call("a", (1, 2))
        activities.log_call("b", (3, 4))
        activities.log_call("a", (5, 6))
        activities.log_call("b", (7, 8))

        expected = [(1, 2), (5, 6)]
        self.assertListEqual(activities.calls_to("a"), expected)
        expected = [(3, 4), (7, 8)]
        self.assertListEqual(activities.calls_to("b"), expected)

if __name__ == '__main__':
    unittest.main()
