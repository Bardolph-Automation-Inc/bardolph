from bardolph.lib import injection, settings
from . import fake_clock, fake_light_set

def configure():
    injection.configure()
    settings.configure()
    fake_clock.configure()
    fake_light_set.configure()
