from bardolph.lib import injection, settings
from bardolph.controller import config_values, light_module
from bardolph.lib import job_control
from bardolph.controller.script_job import ScriptJob

class LsModule:
    _jobs = None

    @classmethod
    def configure(cls):
        injection.configure()
        settings.use_base(config_values.functional).configure()
        light_module.configure()
        LsModule._jobs = job_control.JobControl()

    @classmethod
    def queue_script(cls, script):
        LsModule._jobs.add_job(ScriptJob.from_string(script))

    @classmethod
    def request_stop(cls):
        LsModule._jobs.request_stop()


def configure():
    LsModule.configure()


def queue_script(script):
    LsModule.queue_script(script)


def request_stop():
    LsModule.request_stop()
