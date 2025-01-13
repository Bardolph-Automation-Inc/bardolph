#!/usr/bin/env python

import unittest
from bardolph.vm.call_stack import CallStack

class CallStackTest(unittest.TestCase):
    def test_routine(self):
        stack = CallStack()
        stack.new_frame()

        stack.put_variable('x', 100)
        stack.put_variable('y', 200)

        stack.put_param('x', 500)
        stack.put_param('y', 700)

        # Upon entering the routine, variables go out of scope.
        stack.enter_routine()
        self.assertEqual(stack.get_variable('x'), 500)
        self.assertEqual(stack.get_variable('y'), 700)

        # Returned from the routine, so variables should still be there.
        stack.exit_routine()
        self.assertEqual(stack.get_variable('x'), 100)
        self.assertEqual(stack.get_variable('y'), 200)


if __name__ == '__main__':
    unittest.main()
