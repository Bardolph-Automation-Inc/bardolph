from bardolph.lib import injection, settings
from bardolph.controller import config_values, light_module
from bardolph.lib import job_control
from bardolph.controller.script_job import ScriptJob

class LsModule:
    _jobs = job_control.JobControl()

    @staticmethod
    def queue_script(script):
        return LsModule._jobs.add_job(ScriptJob.from_string(script))


def configure():
    injection.configure()
    settings.using(config_values.functional).apply_env().configure()
    light_module.configure()


def queue_script(script) -> job_control.Agent:
    return LsModule.queue_script(script) or job_control.failed_job()
