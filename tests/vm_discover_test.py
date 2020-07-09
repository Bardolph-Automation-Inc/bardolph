#!/usr/bin/env python

import unittest

from bardolph.controller import i_controller, light_set
from bardolph.fakes import fake_lifx
from bardolph.lib import injection, settings
from bardolph.vm.call_stack import CallStack
from bardolph.vm.machine import Registers
from bardolph.vm.vm_codes import LoopVar, Operand, Operator, Register
from bardolph.vm.vm_discover import VmDiscover
from tests import test_module

class VmDiscoverTest(unittest.TestCase):
    def setUp(self):
        test_module.configure()
        self._make_light_set()
        self._reg = Registers()
        self._discover = VmDiscover(CallStack(), self._reg)

    def test_all_lights(self):
        self._reg.operand = Operand.LIGHT
        self._discover.disc()
        for name in ('light_00', 'light_01', 'light_02'):
            self._assert_and_discn(name)
        self.assertEqual(self._reg.result, Operand.NULL)

    def test_all_lights_rev(self):
        self._reg.operand = Operand.LIGHT
        self._discover.discl()
        for name in ('light_02', 'light_01', 'light_00'):
            self._assert_and_discp(name)
        self.assertEqual(self._reg.result, Operand.NULL)

    def test_all_groups(self):
        self._reg.operand = Operand.GROUP
        self._discover.disc(Operand.ALL)
        self._assert_and_discn('group', Operand.ALL)
        self._assert_and_discn('x', Operand.ALL)
        self.assertEqual(self._reg.result, Operand.NULL)

    def test_all_groups_rev(self):
        self._reg.operand = Operand.GROUP
        self._discover.discl(Operand.ALL)
        self._assert_and_discp('x', Operand.ALL)
        self._assert_and_discp('group', Operand.ALL)
        self.assertEqual(self._reg.result, Operand.NULL)

    def test_all_locations(self):
        self._reg.operand = Operand.LOCATION
        self._discover.disc(Operand.ALL)
        self._assert_and_discn('loc', Operand.ALL)
        self._assert_and_discn('y', Operand.ALL)
        self.assertEqual(self._reg.result, Operand.NULL)

    def test_all_locations_rev(self):
        self._reg.operand = Operand.LOCATION
        self._discover.discl(Operand.ALL)
        self._assert_and_discp('y', Operand.ALL)
        self._assert_and_discp('loc', Operand.ALL)
        self.assertEqual(self._reg.result, Operand.NULL)

    def test_group_membership(self):
        self._reg.operand = Operand.GROUP
        self._discover.disc('group')
        self._assert_and_discn('light_00', 'group')
        self._assert_and_discn('light_02', 'group')
        self.assertEqual(self._reg.result, Operand.NULL)

    def test_group_membership_rev(self):
        self._reg.operand = Operand.GROUP
        self._discover.discl('group')
        self._assert_and_discp('light_02', 'group')
        self._assert_and_discp('light_00', 'group')
        self.assertEqual(self._reg.result, Operand.NULL)

    def test_location_membership(self):
        self._reg.operand = Operand.LOCATION
        self._discover.disc('loc')
        self._assert_and_discn('light_00', 'loc')
        self._assert_and_discn('light_02', 'loc')
        self.assertEqual(self._reg.result, Operand.NULL)

    def test_location_membership_rev(self):
        self._reg.operand = Operand.LOCATION
        self._discover.discl('loc')
        self._assert_and_discp('light_02', 'loc')
        self._assert_and_discp('light_00', 'loc')
        self.assertEqual(self._reg.result, Operand.NULL)

    @classmethod
    def _make_light_set(cls):
        color = [1, 2, 3, 4]
        fake_lifx.using([
            ('light_01', 'x', 'y', color, False),
            ('light_02', 'group', 'loc', color, False),
            ('light_00', 'group', 'loc', color, False)
        ]).configure()
        light_set.configure()

    def _assert_and_discn(self, name0, name1=None):
        self.assertEqual(self._reg.result, name0)
        self._discover.discn(name0, name1)

    def _assert_and_discp(self, name0, name1=None):
        self.assertEqual(self._reg.result, name0)
        self._discover.discp(name0, name1)

if __name__ == '__main__':
    unittest.main()
