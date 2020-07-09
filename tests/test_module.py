import logging

from bardolph.controller import light_set
from bardolph.lib import injection, log_config, settings
from bardolph.fakes import fake_clock, fake_lifx

def configure():
    injection.configure()
    settings.using({
        'log_level': logging.ERROR,
        'log_to_console': True,
        'single_light_discover': True,
        'use_fakes': True
    }).configure()
    log_config.configure()
    fake_clock.configure()
    fake_lifx.configure()
    light_set.configure()
