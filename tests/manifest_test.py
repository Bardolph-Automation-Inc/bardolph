#!/usr/bin/env python

import unittest

from tests.file_reading_test import FileReadingTest
from web.manifest import ButtonSpec, Manifest, ScriptSpec


class ManifestTest(FileReadingTest):
    def _verify_scripts(self,
                        manifest: Manifest,
                        expected: list[ScriptSpec | ButtonSpec]):
        actual = manifest.get_scripts()
        self.assertListEqual(actual, expected)

    def _load_and_check(self,
                        expected: list[ScriptSpec | ButtonSpec],
                        toml: str, json: str | None = None):
        path = self.create_temp_file(toml, '.toml')
        manifest = Manifest()
        manifest.load(path)
        self._verify_scripts(manifest, expected)

        if json is not None:
            path = self.create_temp_file(json, '.json')
            manifest = Manifest()
            manifest.load(path)
            self._verify_scripts(manifest, expected)

    def test_file_minimal(self):
        json = """
        [{
            "file_name": "minimal.ls",
            "background": "222",
            "color": "333"
        }]
        """
        toml = """
        [[button]]
        file_name = "minimal.ls"
        background = "222"
        color = "333"
        """
        expected = [
            ScriptSpec(
                "minimal.ls", "minimal", False, False, False,
                ButtonSpec("Minimal", "222", "333", "colorBulb"))
        ]
        self._load_and_check(expected, toml, json)

    def test_path_minimal(self):
        json = """
        [{
            "path": "minimal",
            "background": "222",
            "color": "333"
        }]
        """
        toml = """
        [[button]]
        path = "minimal"
        background = "222"
        color = "333"
        """
        expected = [
            ScriptSpec(
                "minimal.ls", "minimal", False, False, False,
                ButtonSpec("Minimal", "222", "333", "colorBulb"))
        ]
        self._load_and_check(expected, toml, json)

    def test_no_defaults(self):
        json = """
        [
            {
                "file_name": "first_script.ls",
                "path": "first_path",
                "run_background": "True",
                "clear_foreground": "False",
                "clear_background": "False",
                "title": "The First Script",
                "background": "#333",
                "color": "Cornsilk",
                "icon": "darkBulb"
            },
            {
                "file_name": "second_script.ls",
                "path": "second_path",
                "run_background": "False",
                "clear_foreground": "True",
                "clear_background": "False",
                "title": "The Second Script",
                "background": "Black",
                "color": "#444",
                "icon": "litBulb"
            }
        ]
        """
        toml = """
        [[button]]
        file_name = "first_script.ls"
        path = "first_path"
        run_background = true
        clear_foreground = false
        clear_background = false
        title = "The First Script"
        background = "#333"
        color = "Cornsilk"
        icon = "darkBulb"

        [[button]]
        file_name = "second_script.ls"
        path = "second_path"
        run_background = false
        clear_foreground = true
        clear_background = false
        title = "The Second Script"
        background = "Black"
        color = "#444"
        icon = "litBulb"
        """
        expected = [
            ScriptSpec(
                "first_script.ls", "first_path", True, False, False,
                ButtonSpec("The First Script", "#333", "Cornsilk", "darkBulb")),
            ScriptSpec(
                "second_script.ls", "second_path", False, True, False,
                ButtonSpec("The Second Script", "Black", "#444", "litBulb"))
        ]
        self._load_and_check(expected, toml, json)

    def test_script(self):
        toml = """
        [[script]]
        file_name = "first_script.ls"
        path = "first_path"
        run_background = true
        clear_foreground = false
        clear_background = false

        [[script]]
        file_name = "second_script.ls"

        [[script]]
        path = "third_script"
        """
        expected = [
            ScriptSpec('first_script.ls', 'first_path', True, False, False),
            ScriptSpec('second_script.ls', 'second_script',
                       False, False, False),
            ScriptSpec('third_script.ls', 'third_script', False, False, False)
        ]
        self._load_and_check(expected, toml)


if __name__ == "__main__":
    unittest.main()
