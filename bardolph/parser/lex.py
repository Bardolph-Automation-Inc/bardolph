import re

from .token_types import TokenTypes


class Lex:
    TOKEN_REGEX = re.compile(r'#.*$|".*?"|\S+')
    NUMBER_REGEX = re.compile(r'^[0-9]*\.?[0-9]+$')

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

    @classmethod
    def _unabbreviate(cls, token):
        return {
            'h': 'hue', 's': 'saturation', 'b': 'brightness', 'k': 'kelvin'
        }.get(token, token)

    def get_line_number(self):
        return self._line_num

    def next_token(self):
        token_type = None
        while token_type is None:
            match = next(self._tokens, None)
            while match is None:
                self._next_line()
                if self._tokens is None:
                    return (TokenTypes.EOF, '')
                match = next(self._tokens, None)

            token = Lex._unabbreviate(match.string[match.start():match.end()])
            if token[0] != '#':
                if token[0] == '"':
                    token = token[1:-1]
                    token_type = TokenTypes.LITERAL
                elif self.NUMBER_REGEX.search(token):
                    token_type = TokenTypes.NUMBER
                else:
                    token_type = TokenTypes.__members__.get(
                        token.upper(), TokenTypes.UNKNOWN)

        return (token_type, token)
