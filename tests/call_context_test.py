#!/usr/bin/env python

import unittest

from bardolph.controller.routine import Routine
from bardolph.lib.symbol_table import SymbolType
from bardolph.parser.call_context import CallContext


class CallContextTest(unittest.TestCase):
    def test_push_pop(self):
        context = CallContext()
        context.add_param('a', 1)
        context.add_param('b', 2)
        context.push()
        context.add_param('a', 3)

        self.assertEqual(context.resolve_variable('a').value, 3)
        self.assertIsNone(context.resolve_variable('b'))
        self.assertIsNone(context.resolve_variable('x'))

        context.pop()
        self.assertEqual(context.resolve_variable('a').value, 1)
        self.assertEqual(context.resolve_variable('b').value, 2)

        context.clear()
        self.assertIsNone(context.resolve_variable('a'))

    def test_get_routine(self):
        context = CallContext()
        context.add_param('a', 1)
        context.add_routine(Routine('2'))
        self.assertIsNone(context.get_routine('a'))
        self.assertEqual(context.get_routine('2').name, '2')


if __name__ == '__main__':
    unittest.main()
