from enum import Enum

from ..lib.auto_repl import auto

class TokenTypes(Enum):
    ALL = auto()
    AND = auto()
    ASSIGN = auto()
    AT = auto()
    BEGIN = auto()
    BREAKPOINT = auto()
    CYCLE = auto()
    DEFINE = auto()
    ELSE = auto()
    END = auto()
    EOF = auto()
    EXPRESSION = auto()
    FROM = auto()
    GET = auto()
    GROUP = auto()
    IF = auto()
    LITERAL_STRING = auto()
    LOCATION = auto()
    LOGICAL = auto()
    NAME = auto()
    NUMBER = auto()
    OFF = auto()
    ON = auto()
    OR = auto()
    POWER = auto()
    PAUSE = auto()
    RANGE = auto()
    RAW = auto()
    REGISTER = auto()
    REPEAT = auto()
    SET = auto()
    SYNTAX_ERROR = auto()
    TIME_PATTERN = auto()
    TO = auto()
    UNITS = auto()
    UNTIL = auto()
    UNKNOWN = auto()
    WHILE = auto()
    WITH = auto()
    WAIT = auto()
    ZONE = auto()

    @classmethod
    def commands(cls):
        return (TokenTypes.ASSIGN,
                TokenTypes.GET,
                TokenTypes.OFF,
                TokenTypes.ON,
                TokenTypes.POWER,
                TokenTypes.PAUSE,
                TokenTypes.REGISTER,
                TokenTypes.SET,
                TokenTypes.UNITS,
                TokenTypes.WAIT)
