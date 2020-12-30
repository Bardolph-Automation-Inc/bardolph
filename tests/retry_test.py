#!/usr/bin/env python

import unittest
from unittest.mock import Mock, call, patch

from bardolph.lib.retry import tries

class TestException(Exception):
    def __init__(self):
        super().__init__('expected')


class RetryTest(unittest.TestCase):
    def test_no_fail(self):
        fn = Mock()
        fn.side_effect = [123]

        @tries(1, TestException, False)
        def no_fail():
            return fn(1, 2, x=3)

        result = no_fail()
        fn.assert_called_with(1, 2, x=3)
        self.assertEqual(result, 123)

    def test_single_arg(self):
        fn = Mock()
        fn.side_effect = [456]

        @tries(1, TestException, False)
        def single_arg():
            return fn(1)

        result = single_arg()
        self.assertEqual(result, 456)

    @patch('logging.warning')
    def test_success_on_retry(self, warning):
        fn = Mock()
        ex = TestException()
        fn.side_effect = [ex, 789]

        @tries(2, TestException, False)
        def success_on_retry():
            return fn()

        result = success_on_retry()
        self.assertEqual(result, 789)
        warning.assert_called_with(ex)

    @patch('logging.warning')
    def test_fail(self, warning):
        fn = Mock()
        ex_list = [TestException()] * 3
        fn.side_effect = ex_list

        @tries(3, TestException, 'failed')
        def fail():
            return fn()

        result = fail()
        warning.assert_has_calls((call(ex) for ex in ex_list))
        warning.assert_called_with('Giving up after 3 tries.')
        self.assertEqual(result, 'failed')

    def test_percolates(self):
        @tries(1, TestException, False)
        def fail():
            raise Exception()
        self.assertRaises(Exception, fail)

if __name__ == '__main__':
    unittest.main()
