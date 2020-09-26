import re

from bardolph.lib.time_pattern import TimePattern
from .token_types import TokenTypes


class Lex:
    reg_list = 'hue saturation brightness kelvin red green blue duration time'
    REG_REGEX = re.compile(
        '^' + "$|^".join([reg for reg in reg_list.split()]) + '$')
    EXPR_REGEX = re.compile(r'^\{.*?\}$')
    TOKEN_REGEX = re.compile(r'#.*$|".*?"|\{.*?\}|\S+')
    NAME_REGEX = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
    NUMBER_REGEX = re.compile(r'^\-?[0-9]*\.?[0-9]+$')
    INT_REGEX = re.compile(r'^\-?[0-9]*$')


    def __init__(self, input_string):
        self._lines = iter(input_string.split('\n'))
        self._line_num = 0
        self._tokens = None
        self._next_line()

    def _next_line(self):
        current_line = next(self._lines, None)
        if current_line is None:
            self._tokens = None
        else:
            self._line_num += 1
            self._tokens = self.TOKEN_REGEX.finditer(current_line)

    @staticmethod
    def _unabbreviate(token):
        return {
            'h': 'hue', 's': 'saturation', 'b': 'brightness', 'k': 'kelvin'
        }.get(token, token)

    def get_line_number(self):
        return self._line_num

    def _token_type(self, token):
        token_type = TokenTypes.__members__.get(token.upper(), None)
        if token_type is not None:
            return token_type

        pairs = (
            (self.EXPR_REGEX, TokenTypes.EXPRESSION),
            (self.REG_REGEX, TokenTypes.REGISTER),
            (TimePattern.REGEX, TokenTypes.TIME_PATTERN),
            (self.NUMBER_REGEX, TokenTypes.NUMBER),
            (self.NAME_REGEX, TokenTypes.NAME)
        )
        for reg_expr, token_type in pairs:
            if reg_expr.match(token):
                return token_type

        return TokenTypes.UNKNOWN

    def next_token(self):
        token_type, token = TokenTypes.NULL, ''
        while token_type is TokenTypes.NULL:
            match = None if self._tokens is None else next(self._tokens, None)
            while match is None:
                self._next_line()
                if self._tokens is None:
                    return (TokenTypes.EOF, '')
                match = next(self._tokens, None)

            token = Lex._unabbreviate(match.string[match.start():match.end()])
            if token[0] != '#':
                if token[0] == '"':
                    token = token[1:-1]
                    token_type = TokenTypes.LITERAL_STRING
                else:
                    token_type = self._token_type(token)
                    if token_type is TokenTypes.EXPRESSION:
                        token = token[1:-1]

        return (token_type, token)
