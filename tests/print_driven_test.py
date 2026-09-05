import unittest

from bardolph.lib.i_lib import Output
from bardolph.lib.injection import inject
from tests import test_module
from tests.script_runner import ScriptRunner


class PrintDrivenTest(unittest.TestCase):
    def post_setup(self):
        test_module.replace_print()
        self._runner = ScriptRunner(self)

    @inject(Output)
    def assert_output(self, expected, output):
        try:
            self.assertEqual(output.get_object(), expected)
        except IndexError:
            self.fail("No output was generated.")

    @inject(Output)
    def run_and_check(self, script, expected, output):
        self._runner.run_script(script)
        if isinstance(expected, list):
            self.assertListEqual(output.get_objects(), expected)
        else:
            self.assert_output(expected)

    @inject(Output)
    def run_and_check_rounded(self, script, expected, output):
        self._runner.run_script(script)
        self.assertListEqual(output.get_rounded(), expected)
