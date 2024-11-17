#!/usr/bin/env python

import time
import unittest

from bardolph.controller import i_controller, ls_module
from bardolph.fakes.activity_monitor import Action
from bardolph.lib.injection import provide

from . import test_module


class LsModuleTest(unittest.TestCase):
    def setUp(self):
        test_module.configure()

    def test_script(self):
        agent = ls_module.queue_script("on all time 2 off all")
        tries_left = 500
        while agent.is_running():
            time.sleep(0.1)
            tries_left -= 1
            self.assertGreater(tries_left, 0)
        lifx = provide(i_controller.LightApi)
        self.assertListEqual(lifx.get_call_list(),
            [(Action.SET_POWER, 1, 0), (Action.SET_POWER, 0, 0)])

    def test_stop(self):
        agent = ls_module.queue_script("time 5 repeat on all")
        tries_left = 500
        while agent.is_running():
            time.sleep(0.1)
            tries_left -= 1
            self.assertGreater(tries_left, 0)
            if tries_left == 490:
                agent.request_stop()


if __name__ == '__main__':
    unittest.main()
