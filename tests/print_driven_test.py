import unittest

from tests.script_runner import ScriptRunner
from tests import test_module


class PrintDrivenTest(unittest.TestCase):
    def post_setup(self):
        self._output = test_module.replace_print()
        self._runner = ScriptRunner(self)

    def assert_output(self, expected):
        try:
            self.assertEqual(self._output.get_object(), expected)
        except IndexError:
            self.fail("No output was generated.")

    def run_and_check(self, script, expected):
        self._runner.run_script(script)
        if isinstance(expected, list):
            self.assertListEqual(self._output.get_objects(), expected)
        else:
            self.assert_output(expected)

    def run_and_check_rounded(self, script, expected):
        self._runner.run_script(script)
        self.assertListEqual(self._output.get_rounded(), expected)
