import time

from bardolph.controller import i_controller
from bardolph.controller.script_job import ScriptJob
from bardolph.lib.injection import provide
from bardolph.lib.job_control import JobControl

class ScriptRunner:
    def __init__(self, test):
        self._test = test

    def run_script(self, script, max_waits=None):
        jobs = JobControl()
        jobs.add_job(ScriptJob.from_string(script))
        while jobs.has_jobs():
            time.sleep(0.01)
            if max_waits is not None:
                max_waits -= 1
                if max_waits < 0:
                    self._test.fail("Jobs didn't finish.")

    def check_call_list(self, light_names, expected):
        lifx = provide(i_controller.Lifx)
        for light in lifx.get_lights():
            if light.get_label() in light_names:
                self._test.assertListEqual(light.get_call_list(), expected)

    def check_all_call_lists(self, expected):
        # Calls that were made to all lights, each one individually.
        lifx = provide(i_controller.Lifx)
        for light in lifx.get_lights():
            self._test.assertListEqual(light.get_call_list(), expected)

    @classmethod
    def print_all_call_lists(cls):
        lifx = provide(i_controller.Lifx)
        for light in lifx.get_lights():
            print(light.get_label(), light.get_call_list())

    def check_global_call_list(self, expected):
        # Calls made to LightSet as opposed to individual lights.
        lifx = provide(i_controller.Lifx)
        self._test.assertListEqual(lifx.get_call_list(), expected)

    def test_code(self, script, lights, expected):
        self.run_script(script)
        self.check_call_list(lights, expected)

    def test_code_all(self, script, expected):
        self.run_script(script)
        self.check_all_call_lists(expected)
