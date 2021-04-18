from enum import Enum, auto


class Assoc(Enum):
    LEFT = auto()
    RIGHT = auto()


class TokenTypes(Enum):
    ALL = auto()
    AND = auto()
    AS = auto()
    ASSIGN = auto()
    AT = auto()
    BEGIN = auto()
    BREAK = auto()
    BREAKPOINT = auto()
    COMPARE = auto()
    CYCLE = auto()
    DEFINE = auto()
    ELSE = auto()
    END = auto()
    EOF = auto()
    ERROR = auto()
    FROM = auto()
    GET = auto()
    GROUP = auto()
    IF = auto()
    IN = auto()
    LITERAL_STRING = auto()
    LOCATION = auto()
    LOGICAL = auto()
    MARK = auto()
    NAME = auto()
    NOT = auto()
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
    REGISTER = auto()
    REPEAT = auto()
    RETURN = auto()
    RGB = auto()
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

    def has_string(self):
        return self in (TokenTypes.LITERAL_STRING, TokenTypes.MARK,
            TokenTypes.NAME, TokenTypes.NUMBER, TokenTypes.REGISTER,
            TokenTypes.TIME_PATTERN)

    def is_executable(self):
        return self in (
            TokenTypes.ASSIGN, TokenTypes.BREAKPOINT,
            TokenTypes.GET, TokenTypes.IF, TokenTypes.OFF, TokenTypes.ON,
            TokenTypes.PRINT, TokenTypes.PRINTF, TokenTypes.PRINTLN,
            TokenTypes.PAUSE, TokenTypes.REGISTER, TokenTypes.REPEAT,
            TokenTypes.SET, TokenTypes.UNITS, TokenTypes.WHILE, TokenTypes.WAIT)

class Token:
    def __init__(self,
            token_type, content='', line_number=0, file_name=''):
        self._token_type = token_type
        self._content = content
        self._line_number = line_number
        self._file_name = file_name

    def __eq__(self, other):
        if isinstance(other, str):
            if self._token_type.has_string():
                return self._content == other
            else:
                return False
        if isinstance(other, TokenTypes):
            return (not self._token_type.has_string()
                and self._token_type is other)
        if isinstance(other, Token):
            if self._token_type is not other._token_type:
                return False
            if not self._token_type.has_string():
                return True
        return self._content == other._content

    def __repr__(self):
        fmt = "Token({}"
        if len(self._content) > 0:
            fmt += ", '{}'"
        if self._line_number > 0:
            fmt += ", {}"
        if len(self._file_name) > 0:
            fmt += ", '{}'"
        fmt += ')'
        return fmt.format(
            self._token_type, self._content, self._line_number, self._file_name)

    def __str__(self):
        if self._token_type.has_string():
            return self._content
        return self._token_type.name.lower()

    def is_a(self, token_type) -> bool:
        return self._token_type is token_type

    @property
    def token_type(self):
        return self._token_type

    @property
    def content(self):
        return self._content

    @property
    def file_name(self):
        return self.file_name

    @property
    def is_binop(self):
        return (self.is_a(TokenTypes.COMPARE)
                or self.content in '+-*/^'
                or self.content in ('and', 'or'))

    @property
    def line_number(self):
        return self._line_number

    @property
    def prec(self):
        return {
            'not': 1,
            'or': 2,
            'and': 3,
            '==': 4,
            '<=': 4,
            '>=': 4,
            '!=': 4,
            '<': 4,
            '>': 4,
            '+': 5,
            '-': 5,
            '*': 6,
            '/': 6,
            '^': 7
        }.get(self.content, -1)

    @property
    def assoc(self):
        if self.content in ('not', '^'):
            return Assoc.RIGHT
        return Assoc.LEFT
