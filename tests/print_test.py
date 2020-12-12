#!/usr/bin/env python

import unittest
from unittest.mock import patch

from tests.script_runner import ScriptRunner
from tests import test_module

class PrintTest(unittest.TestCase):
    def setUp(self):
        test_module.configure()
        self._runner = ScriptRunner(self)

    @patch('builtins.print')
    def test_print(self, print_fn):
        script = 'print "hello"'
        self._runner.run_script(script)
        print_fn.assert_called_with('hello', end=' ')

    @patch('builtins.print')
    def test_println(self, print_fn):
        script = 'println "hello"'
        self._runner.run_script(script)
        print_fn.assert_called_with('hello', end='\n')

    @patch('builtins.print')
    def test_printf(self, print_fn):
        script = """
            hue 456
            printf "{} {hue}" 123
        """
        self._runner.run_script(script)
        print_fn.assert_called_with('123 456')


if __name__ == '__main__':
    unittest.main()
