import logging
from enum import Enum, auto


class Action(Enum):
    FIRE_AND_FORGET = auto()
    GET_AGE = auto()
    GET_COLOR = auto()
    GET_MATRIX = auto()
    GET_POWER = auto()
    GET_ZONE_COLOR = auto()
    REQ_WITH_RESP = auto()
    SET_COLOR = auto()
    SET_MATRIX = auto()
    SET_POWER = auto()
    SET_ZONE_COLOR = auto()


class ActivityMonitor:
    def __init__(self):
        self._actions = []
        self._quiet = False

    def _expand_params(params):
        return "" if params is None else ", ".join([str(x) for x in params])

    def log_call(self, name, *params):
        if not self._quiet:
            self._actions.append(name if params is None else (name, *params))
        else:
            self._quiet = False

    def log_output(self, msg):
        logging.info(msg)

    def calls_to(self, name):
        # list of tuples and/or None's.
        return [action[1] for action in self._actions if action[0] == name]

    def get_call_list(self):
        return self._actions

    def clear(self):
        self._actions.clear()

    def quietly(self):
        self._quiet = True
        return self
