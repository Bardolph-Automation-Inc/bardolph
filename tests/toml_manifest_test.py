#!/usr/bin/env python

import unittest

from tests.file_reading_test import FileReadingTest
from web.manifest import ButtonSpec, Manifest


class ManifestTest(FileReadingTest):
    def test_get_script_path(self):
        cases = [("on-all", "On All"),
                 ("off-all-now", "Off All Now"), ("", "")]
        manifest = Manifest()
        for test_case in cases:
            basename = test_case[0]
            settings = {'path': basename}
            actual = manifest._get_script_title(basename, settings)
            self.assertEqual(actual, test_case[1])

    def _verify(self, manifest: Manifest, expected: list[dict[str, str]]):
        actual = manifest.get_scripts()
        self.assertListEqual(actual, expected)

    def _verify_minimal(
            self, manifest: Manifest, expected: list[dict[str, str]]):
        self._verify([
            ButtonSpec(
                "minimal.ls", False, "Minimal", "minimal", "222", "333", "")])

    def test_minimal_toml(self):
        content = """
        [[button]]
        basename = "minimal"
        background = "222"
        color = "333"
        """
        path = self.create_temp_file(content, '.toml')
        manifest = Manifest()
        self.assertTrue(manifest.load(path))
        self._verify_minimal(manifest)

    def test_minimal_json(self):
        content = """
        [{
            "file_name": "minimal.ls",
            "background": "222",
            "color": "333"
        }]
        """
        path = self.create_temp_file(content, '.json')
        manifest = Manifest()
        self.assertTrue(manifest.load(path))
        self._verify_minimal(manifest)

    def test_no_defaults_toml(self):
        content = """
        [[button]]
        basename = "living-room-off"
        path = "first_path"
        file_name = "first_script.ls"
        title = "The First Script"
        icon = "darkBulb"
        background = "#333"
        color = "Cornsilk"
        run_background = "True"

        [[button]]
        basename = "living-room-off"
        path = "second_path"
        file_name = "second_script.ls"
        icon = "litBulb"
        background = "Black"
        color = "#444"
        run_background = "True"
        """
        path = self.create_temp_file(content, '.toml')
        manifest = Manifest()
        self.assertTrue(manifest.load(path))

if __name__ == "__main__":
    unittest.main()
