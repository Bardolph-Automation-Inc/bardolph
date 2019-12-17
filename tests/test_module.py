from bardolph.controller import light_set
from bardolph.lib import injection, settings
from bardolph.fakes import fake_clock, fake_lifx

def configure():
    injection.configure()
    settings.use_base({
        'failure_sleep_time': 300,
        'log_to_console': True,
        'refresh_sleep_time': 300,
        'single_light_discover': True,
        'use_fakes': True
    }).configure()
    fake_clock.configure()
    fake_lifx.configure()
    light_set.configure()
