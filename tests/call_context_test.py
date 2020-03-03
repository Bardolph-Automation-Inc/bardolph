#!/usr/bin/env python

import unittest

from bardolph.controller.routine import Routine
from bardolph.lib.symbol_table import SymbolType
from bardolph.parser.call_context import CallContext


class CallContextTest(unittest.TestCase):
    def test_push_pop(self):
        context = CallContext()
        context.add_variable('global', 100)

        context.push()
        context.add_variable('a', 1)
        context.add_variable('b', 2)
        context.push()
        context.add_variable('a', 3)

        self.assertEqual(context.get_data('a').value, 3)
        self.assertEqual(context.get_data('global').value, 100)
        self.assertIsNone(context.get_symbol('b'))
        self.assertIsNone(context.get_symbol('x'))

        context.pop()
        self.assertEqual(context.get_data('a').value, 1)
        self.assertEqual(context.get_data('b').value, 2)
        self.assertEqual(context.get_data('global').value, 100)

        context.clear()
        self.assertIsNone(context.get_data('global'))
        self.assertIsNone(context.get_data('a'))

    def test_get_routine(self):
        context = CallContext()
        context.add_variable('a', 1)
        context.add_routine(Routine('2'))
        self.assertIsNone(context.get_routine('a'))
        self.assertEqual(context.get_routine('2').name, '2')


if __name__ == '__main__':
    unittest.main()
