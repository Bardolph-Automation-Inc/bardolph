from bardolph.lib import clock
from bardolph.lib import log_config
from bardolph.lib.i_lib import Settings
from bardolph.lib.injection import provide

from . import light_set

def configure():
    """ Assumes injection and settings are already initialized. """
    log_config.configure()
    clock.configure()

    settings = provide(Settings)
    if settings.get_value('use_fakes'):
        from ..fakes import fake_lifx
        fake_lifx.configure()
    else:
        from . import lifx
        lifx.configure()

    light_set.configure()
