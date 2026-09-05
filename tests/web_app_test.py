#!/usr/bin/env python

import time
import unittest
from typing import Any
from unittest.mock import MagicMock, patch

from bardolph.controller.script_job import ScriptJob
from bardolph.lib import i_lib, injection
from bardolph.lib.job_control import Job
from tests.file_reading_test import FileReadingTest
from web.manifest import ButtonSpec, ScriptSpec
from web.web_app import WebApp


class _TestSettings(i_lib.Settings):
    def __init__(self):
        self._values: dict[str, Any] = {}

    def set_value(self, name: str, value: any) -> None:
        self._values[name] = value

    def get_value(self, name: str, default: Any = None) -> Any:
        return self._values.get(name, default)


class _TestJob(Job):
    def __init__(self):
        self._keep_running = True
        self._call_count = 0

    @property
    def call_count(self) -> int:
        return self._call_count

    def execute(self) -> None:
        self._call_count += 1
        while self._keep_running:
            time.sleep(0.01)

    def request_stop(self) -> None:
        self._keep_running = False


class WebAppTest(FileReadingTest):
    def setUp(self) -> None:
        super().setUp()
        self._test_settings = _TestSettings()
        injection.bind(self._get_test_settings).to(i_lib.Settings)

    def _get_test_settings(self) -> _TestSettings:
        return self._test_settings

    def _create_manifest(self, manifest_text: str) -> None:
        path = self.create_temp_file(manifest_text, '.toml')
        self._test_settings.set_value('manifest_file_name', path.resolve())

    def _create_basic_manifest(self) -> None:
        manifest_text = """
        [[button]]
        file_name = "file1.ls"
        path = "path1"
        run_background = true
        clear_foreground = true
        clear_background = true
        title = "title1.ls"
        background = "bkg1"
        color = "color1"
        icon = "icon1"

        [[button]]
        file_name = "file2.ls"
        path = "path2"
        run_background = false
        clear_foreground = false
        clear_background = false
        title = "title2.ls"
        background = "bkg2"
        color = "color2"
        icon = "icon2"

        [[script]]
        file_name = "unused.ls"
        """
        self._create_manifest(manifest_text)

    def test_get_buttons(self) -> None:
        self._create_basic_manifest()
        expected = [
            ScriptSpec(
                'file1.ls', 'path1', True, True, True,
                ButtonSpec('title1.ls', 'bkg1', 'color1', 'icon1')),
            ScriptSpec(
                'file2.ls', 'path2', False, False, False,
                ButtonSpec('title2.ls', 'bkg2', 'color2', 'icon2'))
        ]
        buttons = WebApp().get_buttons()
        self.assertListEqual(buttons, expected)

    def test_get_button_script(self) -> None:
        self._create_basic_manifest()
        actual, running = WebApp().get_script('path2')
        expected = ScriptSpec(
            'file2.ls', 'path2', False, False, False,
            ButtonSpec('title2.ls', 'bkg2', 'color2', 'icon2'))
        self.assertEqual(actual, expected)
        self.assertFalse(running)

    def test_get_script(self) -> None:
        self._create_basic_manifest()
        actual, running = WebApp().get_script('unused')
        expected = ScriptSpec('unused.ls', 'unused', False, False, False)
        self.assertEqual(actual, expected)
        self.assertFalse(running)

    def test_run_foreground_script(self) -> None:
        job = MagicMock()

        with patch.object(ScriptJob, "from_path", return_value=job):
            file_name = str(self.create_temp_file('# empty script', '.ls'))
            script_spec = ScriptSpec(
                file_name, 'test_path', False, False, False)
            app = WebApp(False)
            app.run_script(script_spec)
            pause_count = 0
            while len(app._path_agents) > 0:
                time.sleep(0.1)
                pause_count += 1
                self.assertLess(pause_count, 10)
            job.execute.assert_called_once()

    def test_run_background_script(self) -> None:
        job = _TestJob()
        with patch.object(ScriptJob, "from_path", return_value=job):
            file_name = str(self.create_temp_file('# empty script', '.ls'))
            script = ScriptSpec(file_name, 'test_path', True, False, False)
            app = WebApp(False)
            app._script_list = [script]
            app._path_scripts['test_path'] = script
            app.run_script(script)

            time.sleep(0.01)
            _, running = app.get_script('test_path')
            self.assertTrue(running)

            self.assertTrue(app.stop_script('test_path'))
            self.assertEqual(job.call_count, 1)

            pause_count = 0
            while len(app._path_agents) > 0:
                time.sleep(0.1)
                app._refresh_is_running()
                pause_count += 1
                self.assertLess(pause_count, 10)


if __name__ == '__main__':
    unittest.main()
