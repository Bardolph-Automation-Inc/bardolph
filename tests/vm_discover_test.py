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
        for name in ('light_02', 'light_01', 'light_00'):
            self._assert_and_next(name)
        self.assertEqual(self._reg.result, Operand.NULL)

    def test_all_lights_fwd(self):
        self._reg.operand = Operand.LIGHT
        self._reg.disc_forward = True
        self._discover.disc()
        for name in ('light_00', 'light_01', 'light_02'):
            self._assert_and_next(name)
        self.assertEqual(self._reg.result, Operand.NULL)

    def test_all_groups(self):
        self._reg.operand = Operand.GROUP
        self._discover.disc()
        self._assert_and_next('x')
        self._assert_and_next('group')
        self.assertEqual(self._reg.result, Operand.NULL)

    def test_all_groups_fwd(self):
        self._reg.operand = Operand.GROUP
        self._reg.disc_forward = True
        self._discover.disc()
        self._assert_and_next('group')
        self._assert_and_next('x')
        self.assertEqual(self._reg.result, Operand.NULL)

    def test_all_locations(self):
        self._reg.operand = Operand.LOCATION
        self._discover.disc()
        self._assert_and_next('y')
        self._assert_and_next('loc')
        self.assertEqual(self._reg.result, Operand.NULL)

    def test_all_locations_fwd(self):
        self._reg.operand = Operand.LOCATION
        self._reg.disc_forward = True
        self._discover.disc()
        self._assert_and_next('loc')
        self._assert_and_next('y')
        self.assertEqual(self._reg.result, Operand.NULL)

    def test_group_membership(self):
        self._reg.operand = Operand.GROUP
        self._discover.discm('group')
        self._assert_and_nextm('group', 'light_02')
        self._assert_and_nextm('group', 'light_00')
        self.assertEqual(self._reg.result, Operand.NULL)

    def test_group_membership_fwd(self):
        self._reg.operand = Operand.GROUP
        self._reg.disc_forward = True
        self._discover.discm('group')
        self._assert_and_nextm('group', 'light_00')
        self._assert_and_nextm('group', 'light_02')
        self.assertEqual(self._reg.result, Operand.NULL)

    def test_location_membership(self):
        self._reg.operand = Operand.LOCATION
        self._discover.discm('loc')
        self._assert_and_nextm('loc','light_02')
        self._assert_and_nextm('loc', 'light_00')
        self.assertEqual(self._reg.result, Operand.NULL)

    def test_location_membership_fwd(self):
        self._reg.operand = Operand.LOCATION
        self._reg.disc_forward = True
        self._discover.discm('loc')
        self._assert_and_nextm('loc', 'light_00')
        self._assert_and_nextm('loc', 'light_02')
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

    def _assert_and_next(self, name):
        self.assertEqual(self._reg.result, name)
        self._discover.dnext(name)

    def _assert_and_nextm(self, set, name):
        self.assertEqual(self._reg.result, name)
        self._discover.dnextm(set, name)

if __name__ == '__main__':
    unittest.main()
