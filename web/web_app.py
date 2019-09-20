import html
import json
from os.path import join
import platform
import time

from bardolph.lib.i_lib import Settings
from bardolph.lib.injection import inject
from bardolph.lib.job_control import JobControl

from bardolph.controller.i_controller import LightSet
from bardolph.controller.script_runner import ScriptRunner
from bardolph.controller.snapshot import DictSnapshot, ScriptSnapshot


class Script:
    def __init__(self, file_name, repeat, title, path, background, color, icon):
        self.file_name = html.escape(file_name)
        self.repeat = repeat
        self.path = html.escape(path)
        self.title = html.escape(title)
        self.background = html.escape(background)
        self.color = html.escape(color)
        self.icon = icon

class WebApp:
    def __init__(self):
        self.scripts = {}
        self.scripts_list = []
        self.jobs = JobControl()
        self.load_manifest()           

    @inject(Settings)        
    def queue_script(self, script, settings):
        """ 
        If a repeating script is to be queued up, first clear the entire
        queue. For a non-repeating script, append the incoming script and turn
        off repeating, but allow the current cycle of the running script
        to complete.
        """
        if script.repeat:
            self.request_stop()
            self.jobs.set_repeat(True)
        else:
            self.jobs.set_repeat(False)
        fname = join(settings.get_value("script_path", "."), script.file_name)
        self.jobs.add_job(ScriptRunner.from_file(fname))
    
    def get_script(self, path):
        return self.scripts.get(path, None)
    
    def get_script_list(self):
        return self.scripts_list
    
    def get_snapshot(self):
        return DictSnapshot().generate().get_list()
    
    def set_repeat(self, repeat):
        self.jobs.set_repeat(repeat)
    
    @inject(LightSet)
    def get_status(self, lights):
        last_discover_time = lights.get_last_discover()
        if last_discover_time is not None:
            last_discover = time.strftime(
                "%A %m/%d %I:%M:%S %p", last_discover_time)
        else:
            last_discover = "none"

        return {
            'lights': self.get_snapshot(),
            'last_discover': last_discover,
            'num_successes': lights.get_successful_discovers(),
            'num_failures': lights.get_failed_discovers(),
            'py_version': platform.python_version()
        }

    @inject(Settings)
    def get_path_root(self, settings):
        return settings.get_value('path_root', '/')
    
    @inject(Settings)
    def load_manifest(self, settings):
        # If manifest_name is explicitly None, don't attempt to load a file.
        basename = settings.get_value('manifest_name', 'manifest.json')
        if basename is None:
            return

        fname = join('web',  basename)
        script_list = json.load(open(fname))
        self.scripts = {}
        self.script_order = []
        for script_info in script_list:
            file_name = script_info['file_name']
            repeat = script_info.get('repeat', False) 
            title = self.get_script_title(script_info)
            path = self.get_script_path(script_info)
            background = script_info['background']
            color = script_info['color']
            icon = script_info.get('icon', 'litBulb')
            new_script = Script(
                file_name, repeat, title, path, background, color, icon)
            self.scripts[path] = new_script
            self.scripts_list.append(new_script)
    
    def get_script_title(self, script_info):
        title = script_info.get('title', '')
        if len(title) == 0:
            name = self.get_script_path(script_info)
            spaced = name.replace('_', ' ').replace('-', ' ')
            title = spaced.title()
        return title
            
    def get_script_path(self, script_info):
        path = script_info.get('path', '')
        if len(path) == 0:
            path = script_info['file_name']
            if path[-3:] == ".ls":
                path = path[:-3]
        return path
    
    def request_finish(self):
        self.jobs.request_finish()
    
    def request_stop(self):
        self.jobs.request_stop()
    
    @inject(Settings)    
    def snapshot(self, settings):
        output_name = join(
            settings.get_value('script_path', '.'), '__snapshot__.ls')
        out_file = open(output_name, 'w')
        out_file.write(ScriptSnapshot().generate().get_text())
        out_file.close()
