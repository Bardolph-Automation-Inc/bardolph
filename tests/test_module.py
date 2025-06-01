
import logging

from bardolph.controller import light_set
from bardolph.fakes import fake_clock, fake_light_api
from bardolph.lib import (i_lib, injection, log_config, object_list_output,
                          settings, std_out_output)
from bardolph.runtime import runtime_module


def configure(small_set=False):
    injection.configure()
    settings.using({
        'log_level': logging.ERROR,
        'log_to_console': True,
        'use_fakes': True
    }).configure()
    log_config.configure()
    fake_clock.configure()
    if small_set:
        fake_light_api.using_small_set().configure()
    else:
        fake_light_api.configure()
    light_set.configure()
    std_out_output.configure()
    runtime_module.configure()


def using_small_set():
    class _Reinit:
        @staticmethod
        def configure():
            configure(True)
    return _Reinit()


def replace_print():
    output = object_list_output.ObjectListOutput()
    injection.bind_instance(output).to(i_lib.Output)
    return output
