#!/usr/bin/env python

import unittest
from bardolph.vm.call_stack import CallStack

class CallStackTest(unittest.TestCase):
    def test_push_pop(self):
        stack = CallStack()
        stack.put_variable('a', 1)
        stack.put_variable('b', 2)
        stack.set_return(5)
        stack.push_current()
        self.assertEqual(stack.get_variable('a'), 1)
        self.assertEqual(stack.get_variable('b'), 2)
        self.assertEqual(stack.get_return(), 5)

        stack.put_variable('a', 3)
        stack.put_param('c', 4)
        self.assertIsNone(stack.get_variable('c'))
        stack.push_current()
        self.assertEqual(stack.get_variable('a'), 1)
        self.assertEqual(stack.get_variable('c'), 4)

        stack.pop_current()
        self.assertEqual(stack.get_variable('a'), 3)
        self.assertEqual(stack.get_variable('b'), 2)

        stack.reset()
        self.assertIsNone(stack.get_variable('a'))


if __name__ == '__main__':
    unittest.main()
