import copy
import html
import json
from os.path import join
import platform

from bardolph.lib.i_lib import Settings
from bardolph.lib.injection import inject
from bardolph.lib.job_control import JobControl

from bardolph.controller.script_job import ScriptJob
from bardolph.controller.snapshot import ScriptSnapshot, TextSnapshot


class ScriptControl:
    def __init__(self, file_name, run_background=False, title='', path='',
                background='', color='', icon=''):
        self.file_name = html.escape(file_name)
        self.run_background = run_background
        self.path = html.escape(path)
        self.title = html.escape(title)
        self.background = html.escape(background)
        self.color = html.escape(color)
        self.icon = icon
        self.running = None

class WebApp:
    """
    The URL path for a script is also the name of the job for job_control.
    """

    def __init__(self):
        self._scripts = {}
        self._jobs = JobControl()
        self._load_manifest()

    @inject(Settings)
    def _load_manifest(self, settings):
        # If manifest_name is explicitly None, don't attempt to load a file.
        basename = settings.get_value('manifest_file_name', 'manifest.json')
        if basename is None:
            return
        fname = join('web', basename)
        config_list = json.load(open(fname))
        self._scripts = {}
        for script_config in config_list:
            file_name = script_config['file_name']
            run_background = script_config.get('run_background', False)
            title = self.get_script_title(script_config)
            path = self.get_script_path(script_config)
            background = script_config['background']
            color = script_config['color']
            icon = script_config.get('icon', 'litBulb')
            new_script = ScriptControl(file_name, run_background, title, path,
                                        background, color, icon)
            self._scripts[path] = new_script

    @inject(Settings)
    def queue_script(self, script_control, settings):
        fname = join(
            settings.get_value("script_path", "."), script_control.file_name)
        job = ScriptJob.from_file(fname)
        if script_control.run_background:
            self._jobs.spawn_job(job, script_control.path)
        else:
            self._jobs.add_job(job, script_control.path)
        return True

    def queue_file(self, file_name, run_background=False):
        # Use the file name for the title.
        self.queue_script(
            ScriptControl(file_name, file_name, run_background))

    def get_script_control(self, path) -> ScriptControl:
        script_control = self._scripts.get(path, None)
        if script_control is not None:
            script_control = copy.copy(script_control)
            script_control.running = self._jobs.is_running(script_control.path)
        return script_control

    def get_script_list(self):
        result = []
        for script in self._scripts.values():
            script = copy.copy(script)
            script.running = self._jobs.is_running(script.path)
            result.append(script)
        return result

    def get_status(self):
        status = {
            'background_jobs': self._jobs.get_background(),
            'current_job': self._jobs.get_current(),
            'queued_jobs': self._jobs.get_queued(),
            'lights': TextSnapshot().generate().text,
            'py_version': platform.python_version()
        }
        return status

    @inject(Settings)
    def get_path_root(self, settings):
        return settings.get_value('path_root', '/')

    def get_script_title(self, script_config):
        title = script_config.get('title', '')
        if len(title) == 0:
            name = self.get_script_path(script_config)
            spaced = name.replace('_', ' ').replace('-', ' ')
            title = spaced.title()
        return title

    def get_script_path(self, script_config):
        path = script_config.get('path', '')
        if len(path) == 0:
            path = script_config['file_name']
            if path[-3:] == ".ls":
                path = path[:-3]
        return path

    def stop_script(self, path) -> bool:
        return self._jobs.stop_job(path)

    def stop_current(self) -> bool:
        return self._jobs.stop_current()

    def stop_all(self) -> bool:
        self._jobs.clear_queue()
        result1 = self._jobs.stop_current()
        result2 = self._jobs.stop_background()
        return result1 and result2

    @inject(Settings)
    def snapshot(self, settings):
        output_name = join(
            settings.get_value('script_path', '.'), '__snapshot__.ls')
        out_file = open(output_name, 'w')
        out_file.write(ScriptSnapshot().generate().text)
        out_file.close()
