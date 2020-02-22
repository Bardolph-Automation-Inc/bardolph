#!/usr/bin/env python

import unittest

from bardolph.controller.call_stack import CallStack
from bardolph.controller.routine import Routine
from bardolph.lib.symbol_table import SymbolType


class CallStackTest(unittest.TestCase):
    def test_push_pop(self):
        stack = CallStack()
        stack.add_param('a', 1)
        stack.add_param('b', 2)
        stack.set_return(5)
        stack.push_current()
        self.assertEqual(stack.get_variable('a'), 1)
        self.assertEqual(stack.get_variable('b'), 2)
        self.assertEqual(stack.get_return(), 5)

        stack.add_param('a', 3)
        stack.add_param('c', 4)
        self.assertIsNone(stack.get_variable('c'))
        stack.push_current()
        self.assertEqual(stack.get_variable('a'), 3)
        self.assertEqual(stack.get_variable('c'), 4)

        stack.pop_current()
        self.assertEqual(stack.get_variable('a'), 1)
        self.assertEqual(stack.get_variable('b'), 2)

        stack.clear()
        self.assertIsNone(stack.get_variable('a'))


if __name__ == '__main__':
    unittest.main()
