from . import i_lib
from . import injection


class Settings:
    _active_config = {}

    def __contains__(self, name):
        return name in Settings._active_config

    @classmethod
    def get_value(cls, name, default=None):
        if cls._active_config is None and default is not None:
            return default
        if default is None:
            return Settings._active_config[name]
        return cls._active_config.get(name, default)

    @classmethod
    def configure(cls):
        cls._active_config = None
        injection.bind(Settings).to(i_lib.Settings)

    @classmethod
    def specialize(cls, overrides):
        if cls._active_config is None:
            cls._active_config = overrides.copy()
        else:
            cls._active_config.update(overrides)

    @classmethod
    def put_config(cls, config):
        cls._active_config = config


class Base:
    def __init__(self, overrides):
        self._overrides = overrides

    def and_override(self, override):
        return Overrider(self, override)

    def configure(self):
        Settings.configure()
        Settings.specialize(self._overrides)


class Overrider:
    def __init__(self, base, override):
        self._base = base
        self._override = override

    def configure(self):
        self._base.configure()
        Settings.specialize(self._override)


def using_base(overrides):
    return Base(overrides)


def configure():
    Settings.configure()


def specialize(overrides):
    return Settings.specialize(overrides)
