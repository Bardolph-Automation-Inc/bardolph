#!/usr/bin/env python

import unittest

from tests.script_runner import ScriptRunner
from tests import test_module


class QueryTest(unittest.TestCase):
    def setUp(self):
        test_module.configure()
        self._output = test_module.replace_print()
        self._runner = ScriptRunner(self)

    def test_is_color(self):
        script = """
            print [query "is-color" "Top"]
            print [query "is-color" "Strip"]
            print [query "is-color" "Candle"]
            print [query "is-color" "Living Room"]
        """
        self._runner.run_script(script)
        self.assertListEqual(self._output.get_objects(), [1, 1, 1, 0])

    def test_is_matrix(self):
        script = """
            print [query "is-matrix" "Top"]
            print [query "is-matrix" "Tube"]
        """
        self._runner.run_script(script)
        self.assertListEqual(self._output.get_objects(), [0, 1])

    def test_is_multizone(self):
        script = """
            print [query "is-multizone" "Top"]
            print [query "is-multizone" "Strip"]
        """
        self._runner.run_script(script)
        self.assertListEqual(self._output.get_objects(), [0, 1])

    def test_height(self):
        script = """
            print [query "height" "Top"]
            print [query "height" "Strip"]
            print [query "height" "Candle"]
        """
        self._runner.run_script(script)
        self.assertListEqual(self._output.get_objects(), [1, 1, 6])

    def test_width(self):
        script = """
            print [query "width" "Top"]
            print [query "width" "Strip"]
            print [query "width" "Tube"]
        """
        self._runner.run_script(script)
        self.assertListEqual(self._output.get_objects(), [1, 16, 5])


if __name__ == '__main__':
    unittest.main()
