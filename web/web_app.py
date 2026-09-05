import logging
import platform
from collections.abc import Iterable
from importlib import metadata
from pathlib import Path

from bardolph.controller.script_job import ScriptJob
from bardolph.controller.snapshot import ScriptSnapshot, TextSnapshot
from bardolph.lib.i_lib import Settings
from bardolph.lib.injection import inject
from bardolph.lib.job_control import Agent, JobControl
from web.manifest import Manifest, ScriptSpec


class WebApp:
    def __init__(self, load_manifest: bool = True):
        self._job_control = JobControl()
        self._script_list: list[ScriptSpec] = {}
        self._path_scripts: dict[str, ScriptSpec] = {}
        self._path_agents: dict[str, Agent] = {}
        if load_manifest:
            self._load_manifest()

    @inject(Settings)
    def _load_manifest(self, settings: Settings) -> None:
        manifest = Manifest()
        path = Path(settings.get_value('manifest_file_name', 'manifest.toml'))
        if not path.is_absolute():
            path = 'web' / path
        manifest.load(path)
        script_list = manifest.get_scripts()
        self._script_list = script_list
        self._path_scripts = {script.path: script for script in script_list}

    def get_buttons(self) -> list[ScriptSpec]:
        return [script for script in self._script_list
                if script.button_spec is not None]

    def get_script(self, path: str) -> tuple[ScriptSpec | None, bool]:
        script = self._path_scripts.get(path)
        if script is None:
            return (None, False)
        return (script,
                path in self._path_agents
                and self._path_agents[path].is_running())

    def get_scripts(self) -> list[ScriptSpec]:
        return [script for script in self._script_list
                if script.button_spec is None]

    def get_running(self) -> set[str]:
        self._refresh_is_running()
        return {path for path in self._path_agents
                 if self._path_agents[path].is_running()}

    @inject(Settings)
    def get_path_root(self, settings: Settings) -> str:
        return settings.get_value('path_root', '/')

    @inject(Settings)
    def run_script(self, script: ScriptSpec, settings: Settings) -> None:
        file_name = script.file_name
        if file_name is None or len(file_name) == 0:
            self._check_for_clear(script)
            return
        script_root = settings.get_value("script_path", ".")
        path = Path(script_root) / script.file_name
        if path.exists():
            if script.clear_background:
                self._job_control.clear_background()
            job = ScriptJob.from_path(path)
            if script.run_background:
                self._stop_if_running(script.path)
                agent = self._job_control.spawn(job)
            elif script.clear_foreground:
                agent = self._job_control.run_job(job)
            else:
                agent = self._job_control.append_job(job)
            if agent.is_running():
                self._path_agents[script.path] = agent
        else:
            msg = 'File not found: {}'.format(path.resolve())
            logging.warning(msg)

    def stop_script(self, path: str) -> bool:
        agent = self._path_agents[path]
        if agent is None:
            return False
        agent.request_stop()
        return True

    def _stop_if_running(self, path: str) -> None:
        agent = self._path_agents.get(path)
        if agent is not None:
            if agent.is_running():
                agent.request_stop()
            del self._path_agents[path]

    def _refresh_is_running(self) -> None:
        to_delete = [path for path in self._path_agents
                     if not self._path_agents[path].is_running()]
        for path in to_delete:
            del self._path_agents[path]

    @staticmethod
    def _get_version() -> str:
        try:
            version = metadata.version('bardolph')
        except metadata.PackageNotFoundError:
            version = None
        return version if version is not None else 'unknown'

    def _job_str(self, agent: Agent) -> str:
        for script in self._script_list:
            if self._path_agents.get(script.path) is agent:
                if script.button_spec is not None:
                    job_str = script.button_spec.title + ': '
                else:
                    job_str = ''
                file_name = script.file_name
                if file_name is not None and len(file_name) > 0:
                    job_str += file_name
                return job_str

    def _readable_jobs(self, agents: Iterable[Agent]) -> list[str] | None:
        if len(agents) == 0:
            return None
        job_list = []
        for agent in agents:
            job_str = self._job_str(agent)
            if job_str is not None:
                job_list.append(job_str)
        job_list.sort()
        return job_list

    def _readable_queue(self) -> list[str]:
        return self._readable_jobs(self._job_control.get_queued())

    def _readable_background(self):
        return self._readable_jobs(self._job_control.get_background())

    def _readable_foreground(self) -> str | None:
        agent = self._job_control.get_foreground()
        return None if agent is None else self._job_str(agent)

    def get_status(self) -> dict[str, str]:
        status = {
            'background_jobs': self._readable_background(),
            'foreground_job': self._readable_foreground(),
            'queued_jobs': self._readable_queue(),
            'lights': TextSnapshot().generate(None).text,
            'py_version': platform.python_version(),
            'bardolph_version': self._get_version()
        }
        return status

    @inject(Settings)
    def snapshot(self, settings):
        output = ScriptSnapshot().generate(None).text
        if output is None or len(output) == 0:
            return False
        path = Path(settings.get_value('script_path', '.')) / '__snapshot__.ls'
        with path.open('w') as f:
            f.write(output)
        return True

    def _check_for_clear(self, script_control: ScriptSpec) -> None:
        if script_control.clear_foreground:
            self._job_control.clear_foreground()
        if script_control.clear_background:
            self._job_control.clear_background()
