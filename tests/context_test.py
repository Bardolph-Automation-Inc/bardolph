#!/usr/bin/env python

import unittest

from bardolph.controller.routine import Routine
from bardolph.lib.symbol import SymbolType
from bardolph.parser.context import Context


class ContextTest(unittest.TestCase):
    def assertUndefined(self, symbol):
        self.assertTrue(symbol.undefined)

    def test_add_variable(self):
        context = Context()
        context.add_variable('global')

        context.enter_routine(Routine('test', SymbolType.VAR))
        context.add_variable('a')
        context.add_variable('b')
        context.exit_routine()
        self.assertUndefined(context.get_data('a'))
        self.assertUndefined(context.get_data('b'))

        context.clear()
        self.assertUndefined(context.get_data('global'))

    def test_get_routine(self):
        context = Context()
        context.add_variable('a')
        context.add_routine(Routine('routine', SymbolType.VAR))
        self.assertTrue(context.get_routine('a').undefined)
        self.assertEqual(context.get_routine('routine').name, 'routine')


if __name__ == '__main__':
    unittest.main()
