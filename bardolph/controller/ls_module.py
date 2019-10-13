from bardolph.lib import injection, settings
from bardolph.controller import config_values, light_module
from bardolph.lib import job_control
from bardolph.controller.script_runner import ScriptRunner

class LsModule:
    jobs = None

    def configure(self):
        injection.configure()
        settings.using_base(config_values.functional).configure()
        light_module.configure()
        LsModule.jobs = job_control.JobControl()

    def queue_script(self, script):
        LsModule.jobs.add_job(ScriptRunner.from_string(script))

    def request_stop(self):
        LsModule.jobs.request_stop()

def configure():
    LsModule().configure()

def queue_script(script):
    LsModule().queue_script(script)

def request_stop():
    LsModule().request_stop()
