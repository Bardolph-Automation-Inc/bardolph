#!/usr/bin/env python

import unittest

from bardolph.lib.i_lib import Output
from bardolph.lib.injection import inject
from tests.script_runner import ScriptRunner
from tests import test_module


class StrRuntimeTest(unittest.TestCase):
    def setUp(self):
        test_module.configure()
        test_module.replace_print()
        self._runner = ScriptRunner(self)

    @inject(Output)
    def test_concat(self, output):
        script = """
            print [concat "abc" "def"]
            print [concat "abc" 1.5]
            print [concat 2.6 "jkl"]
            print [concat 2 3]
        """
        self._runner.run_script(script)
        self.assertListEqual(
            output.get_objects(), ['abcdef', 'abc1.5', '2.6jkl', '23'])

    @inject(Output)
    def test_left(self, output):
        script = """
            print [left "abcdef" 1]
            print [left "abcdef" 2]
            print [left "abcdef" 6]
            print [left "abcdef" 100]
        """
        self._runner.run_script(script)
        self.assertListEqual(
            output.get_objects(), ['a', 'ab', 'abcdef', 'abcdef'])

    @inject(Output)
    def test_right(self, output):
        script = """
            print [right "abcdef" 1]
            print [right "abcdef" 2]
            print [right "abcdef" 6]
        """
        self._runner.run_script(script)
        self.assertListEqual(
            output.get_objects(), ['f', 'ef', 'abcdef'])

    @inject(Output)
    def test_substr(self, output):
        script = """
            print [substr "abcdef" 0 1]
            print [substr "abcdef" 5 1]
            print [substr "abcdef" 1 3]
            print [substr "abcdef" 1 100]
        """
        self._runner.run_script(script)
        self.assertListEqual(
            output.get_objects(), ['a', 'f', 'bcd', 'bcdef'])

    @inject(Output)
    def test_contains(self, output):
        script = """
            print [contains "abcdef" "ab"]
            print [contains "abcdef" "x"]
            print [contains "abcdef" "abcdef"]
            print [contains "abcdef" ""]
            print [contains "" "a"]
        """
        self._runner.run_script(script)
        self.assertListEqual(
            output.get_objects(), [1, 0, 1, 1, 0])

    @inject(Output)
    def test_length(self, output):
        script = """
            print [length "abcdef"]
            print [length ""]
        """
        self._runner.run_script(script)
        self.assertListEqual(output.get_objects(), [6, 0])

if __name__ == '__main__':
    unittest.main()
