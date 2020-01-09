#!/usr/bin/env python3

import unittest

from bardolph.fakes.fake_lifx import ActivityLog

class ActivityLogTest(unittest.TestCase):
    def setUp(self): pass
        
    def test_calls(self):
        activities = ActivityLog()
        activities.call("a", (1, 2))
        activities.call("b", (3, 4))
        activities.call("a", (5, 6))
        activities.call("b", (7, 8))
        
        expected = [(1, 2), (5, 6)]
        self.assertListEqual(activities.calls_to("a"), expected)
        expected = [(3, 4), (7, 8)]
        self.assertListEqual(activities.calls_to("b"), expected)

if __name__ == '__main__':
    unittest.main()
