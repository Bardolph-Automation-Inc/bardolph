#!/usr/bin/env python

import unittest
from unittest.mock import patch, call

from tests import test_module
from tests.script_runner import ScriptRunner


class PrintTest(unittest.TestCase):
    def setUp(self):
        test_module.configure()
        self._runner = ScriptRunner(self)

    @patch('builtins.print')
    def test_print(self, print_fn):
        script = 'print "hello"'
        self._runner.run_script(script)
        self.assertListEqual(print_fn.mock_calls,[call('hello', end='')])

    @patch('builtins.print')
    def test_empty_print(self, print_fn):
        script = 'print'
        self._runner.run_script(script)
        self.assertEqual(print_fn.mock_calls, [])

    @patch('builtins.print')
    def test_empty_println(self, print_fn):
        script = 'println'
        self._runner.run_script(script)
        self.assertListEqual(
            print_fn.mock_calls, [call()])

    @patch('builtins.print')
    def test_println(self, print_fn):
        script = 'println "hello"'
        self._runner.run_script(script)
        self.assertListEqual(
            print_fn.mock_calls, [call('hello', end=''), call()])

    @patch('builtins.print')
    def test_printf(self, print_fn):
        script = """
            hue 456
            printf "{} {hue}" 123
        """
        self._runner.run_script(script)
        self.assertListEqual(print_fn.mock_calls, [call('123 456', end='')])


if __name__ == '__main__':
    unittest.main()
