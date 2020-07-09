#!/usr/bin/env python

import logging
import unittest
from unittest.mock import patch

from bardolph.lib import injection, log_config, settings

_log_settings = {
    'log_date_format': 'ldf',
    # Use default for log_file_name.
    'log_format': 'lf',
    'log_level': 'DEBUG'
}

class LogConfigTest(unittest.TestCase):
    def setUp(self):
        injection.configure()
        settings.using(_log_settings).configure()

    @patch('logging.basicConfig')
    @patch('logging.info')
    def test_log_config(self, info, basic_config):
        log_config.configure()
        self.assertTrue(basic_config.called)
        self.assertTrue(info.called)
        basic_config.assert_called_with(
            filename=log_config.logging_defaults['log_file_name'],
            level=logging.DEBUG,
            format='lf',
            datefmt='ldf')
        info.assert_called()


if __name__ == '__main__':
    unittest.main()
