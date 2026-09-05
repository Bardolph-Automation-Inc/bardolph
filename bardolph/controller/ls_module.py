from collections.abc import Iterator

from bardolph.lib import injection, settings
from bardolph.controller import config_values, light_module
from bardolph.lib import job_control
from bardolph.controller.script_job import ScriptJob
from bardolph.runtime import runtime_module

_job_control = job_control.JobControl()


def configure():
    injection.configure()
    settings.using(config_values.functional).apply_env().configure()
    light_module.configure()
    runtime_module.configure()


def queue_script(script: str) -> job_control.Agent:
    return _job_control.append_job(ScriptJob.from_string(script))


def run_script(script: str) -> job_control.Agent:
    return _job_control.run_job(ScriptJob.from_string(script))


def spawn_script(script: str) -> job_control.Agent:
    return _job_control.spawn(ScriptJob.from_string(script))


def consume_scripts(script_producer: Iterator[str]) -> bool:
    def produce_jobs(script_producer: Iterator[str]) -> Iterator[ScriptJob]:
        for script in script_producer:
            yield ScriptJob.from_string(script)

    return _job_control.run_iterated(produce_jobs(script_producer))
