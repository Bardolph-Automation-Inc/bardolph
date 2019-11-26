from enum import Enum

from bardolph.lib.auto_repl import auto

class TokenTypes(Enum):
    ALL = auto()
    AND = auto()
    AT = auto()
    DEFINE = auto()
    EOF = auto()
    GET = auto()
    GROUP = auto()
    LITERAL = auto()
    LOCATION = auto()
    LOGICAL = auto()
    NUMBER = auto()
    OFF = auto()
    ON = auto()
    OR = auto()
    POWER = auto()
    PAUSE = auto()
    RAW = auto()
    REGISTER = auto()
    SET = auto()
    SYNTAX_ERROR = auto()
    TIME_PATTERN = auto()
    UNITS = auto()
    UNKNOWN = auto()
    ZONE = auto()
