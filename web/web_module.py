import logging

from bardolph.lib import injection, settings

from bardolph.controller import config_values, light_module
from .web_app import WebApp

debug = False

def configure():
    injection.configure()   
    settings.using_base(config_values.functional).configure()
    
    global debug
    if debug:
        settings.specialize({
            'use_fakes': True,
            'log_level': logging.DEBUG
        })
    light_module.configure()
    injection.bind_instance(WebApp()).to(WebApp)
