#!/usr/bin/env python

import threading
import time
import unittest


class ThreadedTest(unittest.TestCase):
    def tearDown(self) -> None:
        super().tearDown()
        if threading.active_count() > 1:
            time.sleep(0.1)
        self.assertLess(threading.active_count(), 2,
            'Active threads: {}'.format(
                [t.name for t in threading.enumerate()]))


if __name__ == "__main__":
    unittest.main()
