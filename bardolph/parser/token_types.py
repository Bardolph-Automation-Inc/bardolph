from enum import Enum

from bardolph.lib.auto_repl import auto

class TokenTypes(Enum):
    ALL = auto()
    AND = auto()
    BRIGHTNESS = auto()
    DEFINE = auto()
    DURATION = auto()
    EOF = auto()
    GET = auto()
    GROUP = auto()
    HUE = auto()
    LITERAL = auto()
    LOCATION = auto()
    LOGICAL = auto()
    NUMBER = auto()
    OFF = auto()
    ON = auto()
    PAUSE = auto()
    KELVIN = auto()
    RAW = auto()
    SATURATION = auto()
    SET = auto()
    SYNTAX_ERROR = auto()
    TIME = auto()
    UNITS = auto()
    UNKNOWN = auto()
