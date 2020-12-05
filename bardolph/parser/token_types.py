from enum import Enum, auto


class TokenTypes(Enum):
    ALL = auto()
    AND = auto()
    AS = auto()
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
    IN = auto()
    LITERAL_STRING = auto()
    LOCATION = auto()
    LOGICAL = auto()
    NAME = auto()
    NULL = auto()
    NUMBER = auto()
    OFF = auto()
    ON = auto()
    OR = auto()
    PRINT = auto()
    PRINTF = auto()
    PRINTLN = auto()
    PAUSE = auto()
    RAW = auto()
    RGB = auto()
    REGISTER = auto()
    REPEAT = auto()
    SET = auto()
    SYNTAX_ERROR = auto()
    TIME_PATTERN = auto()
    TO = auto()
    UNITS = auto()
    UNKNOWN = auto()
    WHILE = auto()
    WITH = auto()
    WAIT = auto()
    ZONE = auto()

    def is_executable(self):
        return self in (
            TokenTypes.ASSIGN, TokenTypes.BREAKPOINT,
            TokenTypes.GET, TokenTypes.IF, TokenTypes.OFF, TokenTypes.ON,
            TokenTypes.PRINT, TokenTypes.PRINTF, TokenTypes.PRINTLN,
            TokenTypes.PAUSE, TokenTypes.REGISTER, TokenTypes.REPEAT,
            TokenTypes.SET, TokenTypes.UNITS, TokenTypes.WHILE, TokenTypes.WAIT)
