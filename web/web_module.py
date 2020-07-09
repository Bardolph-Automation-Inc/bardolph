import os

from bardolph.lib import injection, settings
from bardolph.controller import config_values, light_module
from . import web_app, i_web

def configure():
    injection.configure()

    settings_init = settings.using(config_values.functional)
    settings_init.add_overrides({
        'log_to_console': False
    })
    ini = os.getenv('BARDOLPH_INI')
    if ini:
        settings_init.apply_file(ini)
    settings_init.configure()

    light_module.configure()
    injection.bind_instance(web_app.WebApp()).to(i_web.WebApp)
