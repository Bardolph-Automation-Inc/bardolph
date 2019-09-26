from bardolph.lib import injection, settings
from bardolph.controller import config_values, light_module
from . import web_app, i_web

def configure():
    injection.configure()   
    settings.using_base(config_values.functional).configure()
    settings.specialize({
        'log_to_console': False
    })
    light_module.configure()
    injection.bind_instance(web_app.WebApp()).to(i_web.WebApp)
