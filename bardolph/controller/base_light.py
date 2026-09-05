import time
from abc import ABC, abstractmethod

from bardolph.controller import i_controller

_MAX_TRIES = 3


class BaseLight(ABC, i_controller.Light):
    def __init__(self, uid=None, name=None, group=None, location=None):
        self._uid = uid or hash(self)
        self._name = name
        self._group = group
        self._location = location
        self._birth = time.time()

    def __repr__(self):
        fmt = 'Light(_name="{}", _group="{}", _location="{}", _multizone={}, '
        fmt += ' _birth={})'
        rep = fmt.format(
            self._name, self._group, self._location, self._multizone,
            self._birth)
        return rep

    def get_uid(self):
        return self._uid

    def get_name(self):
        return self._name

    def get_group(self):
        return self._group

    def get_location(self):
        return self._location

    def get_height(self) -> int:
        return 1

    def get_width(self) -> int:
        return 1

    def get_age(self) -> float:
        # seconds
        return time.time() - self._birth

    @abstractmethod
    def get_color(self):
        'get_color() not implemented'
        pass

    @abstractmethod
    def set_color(self, *_):
        'set_color() not implemented'
        pass

    @abstractmethod
    def get_power(self):
        'get_power() not implemented'
        return None
        pass

    @abstractmethod
    def set_power(self, *_):
        'set_power() not implemented'
        pass
