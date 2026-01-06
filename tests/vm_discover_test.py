#!/usr/bin/env python

import unittest

from bardolph.vm.call_stack import CallStack
from bardolph.vm.eval_stack import EvalStack
from bardolph.vm.machine import Registers
from bardolph.vm.vm_codes import Operand
from bardolph.vm.vm_discover import VmDiscover
from tests import test_module


class VmDiscoverTest(unittest.TestCase):
    def setUp(self):
        test_module.using_small_set().configure()
        self._reg = Registers()
        self._call_stack = CallStack()
        self._eval_stack = EvalStack()
        self._discover = VmDiscover(
            self._call_stack, self._eval_stack, self._reg)

    def _assert_and_next(self, expected_name):
        actual_name = self._eval_stack.pop()
        self.assertEqual(actual_name, expected_name)
        self._discover.dnext(expected_name)

    def _assert_and_nextm(self, lights, expected_name):
        actual_name = self._eval_stack.pop()
        self.assertEqual(actual_name, expected_name)
        self._discover.dnextm(lights, expected_name)

    def _assert_at_end(self):
        self.assertEqual(self._eval_stack.pop(), Operand.NULL)

    def test_all_lights(self):
        self._reg.operand = Operand.LIGHT
        self._discover.disc()
        for name in ('light_2', 'light_1', 'light_0'):
            self._assert_and_next(name)
        self._assert_at_end()

    def test_all_lights_fwd(self):
        self._reg.operand = Operand.LIGHT
        self._reg.disc_forward = True
        self._discover.disc()
        for name in ('light_0', 'light_1', 'light_2'):
            self._assert_and_next(name)
        self._assert_at_end()

    def test_all_groups(self):
        self._reg.operand = Operand.GROUP
        self._discover.disc()
        self._assert_and_next('group')
        self._assert_and_next('a')
        self._assert_at_end()

    def test_all_groups_fwd(self):
        self._reg.operand = Operand.GROUP
        self._reg.disc_forward = True
        self._discover.disc()
        self._assert_and_next('a')
        self._assert_and_next('group')
        self._assert_at_end()

    def test_all_locations(self):
        self._reg.operand = Operand.LOCATION
        self._discover.disc()
        self._assert_and_next('loc')
        self._assert_and_next('b')
        self._assert_at_end()

    def test_all_locations_fwd(self):
        self._reg.operand = Operand.LOCATION
        self._reg.disc_forward = True
        self._discover.disc()
        self._assert_and_next('b')
        self._assert_and_next('loc')
        self._assert_at_end()

    def test_group_membership(self):
        self._reg.operand = Operand.GROUP
        self._discover.discm('group')
        self._assert_and_nextm('group', 'light_2')
        self._assert_and_nextm('group', 'light_0')
        self._assert_at_end()

    def test_group_membership_fwd(self):
        self._reg.operand = Operand.GROUP
        self._reg.disc_forward = True
        self._discover.discm('group')
        self._assert_and_nextm('group', 'light_0')
        self._assert_and_nextm('group', 'light_2')
        self._assert_at_end()

    def test_location_membership(self):
        self._reg.operand = Operand.LOCATION
        self._discover.discm('loc')
        self._assert_and_nextm('loc', 'light_2')
        self._assert_and_nextm('loc', 'light_0')
        self._assert_at_end()

    def test_location_membership_fwd(self):
        self._reg.operand = Operand.LOCATION
        self._reg.disc_forward = True
        self._discover.discm('loc')
        self._assert_and_nextm('loc', 'light_0')
        self._assert_and_nextm('loc', 'light_2')
        self._assert_at_end()


if __name__ == '__main__':
    unittest.main()
