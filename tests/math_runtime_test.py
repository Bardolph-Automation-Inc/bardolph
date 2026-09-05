#!/usr/bin/env python

import unittest

from bardolph.lib.i_lib import Output
from bardolph.lib.injection import inject
from tests.script_runner import ScriptRunner
from tests import test_module


class MathRuntimeTest(unittest.TestCase):
    def setUp(self):
        test_module.configure()
        test_module.replace_print()
        self._runner = ScriptRunner(self)

    @inject(Output)
    def test_round(self, output):
        script = """
            print [round 1]
            print [round 1.5]
            print [round 1.1]
            print [round -1.1]
            print [round -1.6]
        """
        self._runner.run_script(script)
        self.assertListEqual(output.get_objects(), [1, 2, 1, -1, -2])

    @inject(Output)
    def test_trunc(self, output):
        script = """
            print [trunc 1]
            print [trunc 1.5]
            print [trunc 1.1]
            print [trunc -1.1]
            print [trunc -1.6]
        """
        self._runner.run_script(script)
        self.assertListEqual(output.get_objects(), [1, 1, 1, -1, -1])

    @inject(Output)
    def test_floor(self, output):
        script = """
            print [floor 2]
            print [floor 2.5]
            print [floor -2.5]
        """
        self._runner.run_script(script)
        self.assertListEqual(output.get_objects(), [2, 2, -3])

    @inject(Output)
    def test_ceil(self, output):
        script = """
            print [ceil 2]
            print [ceil 2.5]
            print [ceil -2.5]
        """
        self._runner.run_script(script)
        self.assertListEqual(output.get_objects(), [2, 3, -2])

    @inject(Output)
    def test_random(self, output):
        self._runner.run_script('print [random 0 100]')
        self.assertTrue(0 <= output.get_object() <= 100)

    @inject(Output)
    def test_sqrt(self, output):
        script = """
            print [sqrt -9]
            print [sqrt 16]
        """
        self._runner.run_script(script)
        self.assertListEqual(output.get_objects(), [-1, 4])

    @inject(Output)
    def test_trig(self, output):
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
            output.get_objects(), [-1, 1, 1, -90, 0, 45])

    @inject(Output)
    def test_cycle(self, output):
        script = """
            print [cycle 350]
            print [cycle 365]
            print [cycle -10]
            print [cycle -370]
            print [cycle 3607]
        """
        self._runner.run_script(script)
        self.assertListEqual(
            output.get_objects(), [350, 5, 350, 350, 7])

    @inject(Output)
    def test_abs(self, output):
        script = """
            print [abs 1]
            print [abs (1 - 2)]
            print [abs 0]
            print [abs 2 - 1]
        """
        self._runner.run_script(script)
        self.assertListEqual(
            output.get_objects(), [1, 1, 0, 1])


if __name__ == '__main__':
    unittest.main()
