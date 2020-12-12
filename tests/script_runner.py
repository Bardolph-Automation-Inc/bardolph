import time

from bardolph.controller import i_controller
from bardolph.controller.script_job import ScriptJob
from bardolph.lib.injection import provide
from bardolph.lib.job_control import JobControl

class ScriptRunner:
    def __init__(self, test_case):
        self._test_case = test_case

    @staticmethod
    def assure_list(maybe_list):
        return maybe_list if isinstance(maybe_list, list) else [maybe_list]

    def run_script(self, script, max_waits=None):
        jobs = JobControl()
        jobs.add_job(ScriptJob.from_string(script))
        while jobs.has_jobs():
            time.sleep(0.01)
            if max_waits is not None:
                max_waits -= 1
                if max_waits < 0:
                    self._test_case.fail("Jobs didn't finish.")

    def check_call_list(self, light_names, expected):
        lifx = provide(i_controller.Lifx)
        for light in lifx.get_lights():
            if light.get_label() in light_names:
                self._test_case.assertListEqual(
                    light.get_call_list(), self.assure_list(expected))

    def check_all_call_lists(self, expected):
        # Calls that were made to all lights, each one individually.
        expected = self.assure_list(expected)
        lifx = provide(i_controller.Lifx)
        for light in lifx.get_lights():
            self._test_case.assertListEqual(light.get_call_list(), expected)

    def check_global_call_list(self, expected):
        # Calls made to LightSet as opposed to individual lights.
        expected = self.assure_list(expected)
        lifx = provide(i_controller.Lifx)
        self._test_case.assertListEqual(lifx.get_call_list(), expected)

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
        lifx = provide(i_controller.Lifx)
        for light in lifx.get_lights():
            if light.get_label() not in allowed:
                self._test_case.assertEqual(len(light.get_call_list()), 0)

    @staticmethod
    def print_all_call_lists():
        lifx = provide(i_controller.Lifx)
        for light in lifx.get_lights():
            print(light.get_label(), light.get_call_list())
