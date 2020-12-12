#!/usr/bin/env python

import unittest

from bardolph.controller.routine import Routine
from bardolph.parser.context import Context


class ContextTest(unittest.TestCase):
    def assertUndefined(self, symbol):
        self.assertTrue(symbol.undefined)

    def test_push_pop(self):
        context = Context()
        context.add_variable('global', 100)

        context.enter_routine()
        context.add_variable('a', 1)
        context.add_variable('b', 2)

        self.assertEqual(context.get_data('a').value, 1)
        self.assertEqual(context.get_data('b').value, 2)
        self.assertEqual(context.get_data('global').value, 100)

        context.exit_routine()
        self.assertUndefined(context.get_data('a'))
        self.assertUndefined(context.get_data('b'))
        self.assertEqual(context.get_data('global').value, 100)

        context.clear()
        self.assertUndefined(context.get_data('global'))

    def test_get_routine(self):
        context = Context()
        context.add_variable('a', 1)
        context.add_routine(Routine('routine'))
        self.assertTrue(context.get_routine('a').undefined)
        self.assertEqual(context.get_routine('routine').name, 'routine')


if __name__ == '__main__':
    unittest.main()
