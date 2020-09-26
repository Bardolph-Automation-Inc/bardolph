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
    LIGHTS = auto()
    LITERAL_STRING = auto()
    LOCATION = auto()
    LOGICAL = auto()
    NAME = auto()
    NULL = auto()
    NUMBER = auto()
    OFF = auto()
    ON = auto()
    OR = auto()
    POWER = auto()
    PRINT = auto()
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

    @staticmethod
    def commands():
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

    def is_command(self):
        return self in TokenTypes.commands()

    def is_printable(self):
        return self in (
            TokenTypes.EXPRESSION, TokenTypes.LITERAL_STRING, TokenTypes.NAME,
            TokenTypes.NUMBER, TokenTypes.REGISTER, TokenTypes.TIME_PATTERN,
            TokenTypes.UNKNOWN
        )
