#!/usr/bin/env python

import unittest

from tests.script_runner import ScriptRunner
from tests import test_module


class RuntimeTest(unittest.TestCase):
    def setUp(self):
        test_module.configure()
        self._output = test_module.replace_print()
        self._runner = ScriptRunner(self)

    def test_round(self):
        script = """
            print [round 1]
            print [round 1.5]
            print [round 1.1]
            print [round -1.1]
            print [round -1.6]
        """
        self._runner.run_script(script)
        self.assertListEqual(self._output.get_objects(), [1, 2, 1, -1, -2])

    def test_trunc(self):
        script = """
            print [trunc 1]
            print [trunc 1.5]
            print [trunc 1.1]
            print [trunc -1.1]
            print [trunc -1.6]
        """
        self._runner.run_script(script)
        self.assertListEqual(self._output.get_objects(), [1, 1, 1, -1, -1])

    def test_floor(self):
        script = """
            print [floor 2]
            print [floor 2.5]
            print [floor -2.5]
        """
        self._runner.run_script(script)
        self.assertListEqual(self._output.get_objects(), [2, 2, -3])

    def test_ceil(self):
        script = """
            print [ceil 2]
            print [ceil 2.5]
            print [ceil -2.5]
        """
        self._runner.run_script(script)
        self.assertListEqual(self._output.get_objects(), [2, 3, -2])

    def test_sqrt(self):
        script = """
            print [sqrt -9]
            print [sqrt 16]
        """
        self._runner.run_script(script)
        self.assertListEqual(self._output.get_objects(), [-1, 4])

    def test_trig(self):
        script = """
            print [sin 270]
            print [cos 0]
            print [tan 45]
            print [asin -1]
            print [acos 1]
            print [atan 1]
        """
        self._runner.run_script(script)
        self._runner.assert_list_almost_equal(
            self._output.get_objects(), [-1, 1, 1, -90, 0, 45])

    def test_cycle(self):
        script = """
            print [cycle 350]
            print [cycle 365]
            print [cycle -10]
            print [cycle -370]
            print [cycle 3607]
        """
        self._runner.run_script(script)
        self.assertListEqual(
            self._output.get_objects(), [350, 5, 350, 350, 7])


if __name__ == '__main__':
    unittest.main()
