#!/usr/bin/env python

import unittest

from bardolph.lib import injection, settings
from web.web_app import WebApp

class WebAppTest(unittest.TestCase):
    def setUp(self):
        injection.configure()
        settings.using({'manifest_name': None}).configure()

    def test_get_title(self):
        app = WebApp()
        script = {'path': 'test-get_title'}
        self.assertEqual(app.get_script_title(script), 'Test Get Title')
        script = {'file_name': 'test-get_title.ls'}
        self.assertEqual(app.get_script_title(script), 'Test Get Title')
        script = {'file_name': 'test-get_title'}
        self.assertEqual(app.get_script_title(script), 'Test Get Title')

    def test_get_path(self):
        app = WebApp()
        script = {'file_name': 'test.ls'}
        self.assertEqual(app.get_script_path(script), 'test')
        script = {'file_name': 'test.ls', 'path': 'test-path'}
        self.assertEqual(app.get_script_path(script), 'test-path')


if __name__ == '__main__':
    unittest.main()
