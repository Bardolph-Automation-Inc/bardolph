from . import i_lib
from . import injection


class Settings:
    active_config = None

    def __contains__(self, name):
        return self.active_config is not None and name in self.active_config

    def get_value(self, name, default=None):
        if self.active_config is None and default is not None:
            return default
        if default is None:
            return self.active_config[name]
        return self.active_config.get(name, default)

    @classmethod
    def configure(cls):
        Settings.active_config = None
        injection.bind(Settings).to(i_lib.Settings)

    @classmethod
    def specialize(cls, overrides):
        if Settings.active_config is None:
            Settings.active_config = overrides.copy()
        else:
            Settings.active_config.update(overrides)

    @classmethod
    def put_config(cls, config):
        cls.active_config = config


class Base:
    def __init__(self, overrides):
        self.overrides = overrides

    def and_override(self, override):
        return Overrider(self, override)

    def configure(self):
        Settings.configure()
        Settings.specialize(self.overrides)


class Overrider:
    def __init__(self, base, override):
        self.base = base
        self.override = override

    def configure(self):
        self.base.configure()
        Settings.specialize(self.override)


def using_base(overrides):
    return Base(overrides)


def configure():
    Settings.configure()


def specialize(overrides):
    return Settings.specialize(overrides)
