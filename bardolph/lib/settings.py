import configparser

from . import i_lib
from . import injection


class Settings:
    _the_config = {}

    def __init__(self):
        self._config = Settings._the_config
        
    def __contains__(self, name):
        return name in self._config

    def get_value(self, name, default=None):
        return self._config.get(name, default)


class Builder:
    def __init__(self, initial=None):
        self._config = initial.copy() if initial is not None else {}

    def add_overrides(self, overrides):
        self._config.update(overrides)
        return self

    def apply_file(self, file_name):
        if self._config is None:
            self._config = {}
        config = configparser.ConfigParser()
        config.read(file_name)
        for section in config.sections():
            for key in config[section]:
                value = config[section][key]
                self._config[key] = {
                    'True': True,
                    'False': False
                }.get(value, value)
        return self

    def configure(self):
        Settings._the_config = self._config
        injection.bind(Settings).to(i_lib.Settings)
        

def use_base(initial=None):
    return Builder(initial)


def empty():
    return Builder(None)
