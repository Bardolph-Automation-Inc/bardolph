import time

from bardolph.controller import i_controller
from bardolph.controller.color_matrix import ColorMatrix
from bardolph.controller.script_job import ScriptJob
from bardolph.lib.injection import provide
from bardolph.lib.job_control import JobControl
from bardolph.parser.parse import Parser


class ScriptRunner:
    def __init__(self, test_case):
        self._test_case = test_case
        self._machine_state = None

    @staticmethod
    def as_list(maybe_list):
        return maybe_list if isinstance(maybe_list, list) else [maybe_list]

    def parse_script(self, script):
        parser = Parser()
        self._test_case.assertTrue(parser.parse(script), parser.get_errors())

    def run_script(self, script, max_waits=None):
        jobs = JobControl()
        script_job = ScriptJob.from_string(script)
        if script_job.program is None:
            self._test_case.fail(
                "Compile failed - {}".format(script_job.compile_errors))
        jobs.add_job(script_job)
        while jobs.has_jobs():
            time.sleep(0.01)
            if max_waits is not None:
                max_waits -= 1
                if max_waits < 0:
                    self._test_case.fail("Jobs didn't finish.")
            self._machine_state = script_job.get_machine_state()

    def check_call_list(self, to_check, expected):
        light_api = provide(i_controller.LightApi)
        expected = self.as_list(expected)
        for light in light_api.get_lights():
            light_name = light.get_name()
            if light_name in to_check:
                self._test_case.assertListEqual(
                    light.get_call_list(),
                    expected,
                    'Light: "{}"'.format(light_name))

    def check_all_call_lists(self, expected):
        # Calls that were made to all lights, each one individually.
        expected = self.as_list(expected)
        light_api = provide(i_controller.LightApi)
        for light in light_api.get_lights():
            self._test_case.assertListEqual(
                light.get_call_list(),
                expected,
                'Light: "{}"'.format(light.get_name()))

    def check_global_call_list(self, expected):
        # Calls made to LightSet as opposed to individual lights.
        expected = self.as_list(expected)
        light_api = provide(i_controller.LightApi)
        self._test_case.assertListEqual(light_api.get_call_list(), expected)

    def assert_reg_equal(self, reg, expected):
        self._test_case.assertEqual(
            self._machine_state.reg.get_by_enum(reg), expected)

    def assert_var_equal(self, name: str, expected):
        actual = self._machine_state.call_stack.get_variable(name)
        self._test_case.assertIsNotNone(actual)
        if issubclass(int, type(expected)):
            self._test_case.assertEqual(actual, expected)
        else:
            self._test_case.assertAlmostEqual(actual, expected, 5)

    def assert_vars_equal(self, *pairs):
        it = iter(pairs)
        for pair in it:
            self.assert_var_equal(pair, next(it))

    def assert_list_almost_equal(self, list0, list1, precision=1, message=''):
        self._test_case.assertEqual(len(list0), len(list1), message)
        iter0 = iter(list0)
        iter1 = iter(list1)
        go = True
        while go:
            try:
                obj0 = next(iter0)
                obj1 = next(iter1)
                self._test_case.assertAlmostEqual(obj0, obj1, precision, message)
            except StopIteration:
                go = False

    def test_code(self, script, lights, expected):
        self.run_script(script)
        self.check_call_list(lights, expected)

    def test_code_all(self, script, expected):
        self.run_script(script)
        self.check_all_call_lists(expected)

    def check_no_others(self, *allowed):
        """
        Assert that only the lights in the list got any calls.
        """
        lifx = provide(i_controller.LightApi)
        for light in lifx.get_lights():
            if light.get_name() not in allowed:
                self._test_case.assertEqual(len(light.get_call_list()), 0)

    def check_final_matrix(self, light_name, height, width, expected):
        light_set = provide(i_controller.LightSet)
        light = light_set.get_light(light_name)
        self._test_case.assertIsNotNone(light)
        self._test_case.assertIsInstance(light, i_controller.MatrixLight)

        actual_mat = light.get_matrix()
        expected_mat = ColorMatrix.new_from_iterable(height, width, expected)

        self._test_case.assertListEqual(
            expected_mat.get_colors(), actual_mat.get_colors(),
            '\nActual:\n{}\nExpected:\n{}'.format(
                str(actual_mat), str(expected_mat)))

    @staticmethod
    def print_all_call_lists():
        lifx = provide(i_controller.LightApi)
        for light in lifx.get_lights():
            print(light.get_name(), light.get_call_list())
