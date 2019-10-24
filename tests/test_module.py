from bardolph.lib import injection, settings
from bardolph.fakes import fake_clock, fake_light_set

def configure():
    injection.configure()
    settings.use_base(None).configure()
    fake_clock.configure()
    fake_light_set.configure()
