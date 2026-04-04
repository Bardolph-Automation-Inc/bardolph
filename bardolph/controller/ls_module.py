from collections.abc import Iterator

from bardolph.lib import injection, settings
from bardolph.controller import config_values, light_module
from bardolph.lib import job_control
from bardolph.controller.script_job import ScriptJob
from bardolph.runtime import runtime_module

class LsModule:
    _jobs = job_control.JobControl()

    @staticmethod
    def queue_script(script: str):
        return LsModule._jobs.add_job(ScriptJob.from_string(script))

    @staticmethod
    def run_script(script: str):
        return LsModule._jobs.run_job(ScriptJob.from_string(script))


def configure():
    injection.configure()
    settings.using(config_values.functional).apply_env().configure()
    light_module.configure()
    runtime_module.configure()


def queue_script(script) -> job_control.Agent:
    return LsModule.queue_script(script) or job_control.failed_job()


def run_script(script) -> job_control.Agent:
    return LsModule.run_script(script) or job_control.failed_job()


def consume_scripts(producer: Iterator[str]):
    LsModule._jobs.stop_current()
    LsModule._jobs.clear_queue()
    for script in producer:
        LsModule._jobs.run_single_job(ScriptJob.from_string(script))
