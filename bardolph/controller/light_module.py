from bardolph.lib import clock
from bardolph.lib import log_config
from bardolph.lib.i_lib import Settings
from bardolph.lib.injection import provide

from . import light_set

def configure():
    # Assumes injection and settings are already initialized.
    log_config.configure()
    clock.configure()

    settings = provide(Settings)
    if settings.get_value('use_fakes'):
        from bardolph.fakes import fake_light_api
        fake_light_api.configure()
    else:
        from bardolph.controller import lifx_lan_api
        lifx_lan_api.configure()

    light_set.configure()
