import re

from bardolph.lib.time_pattern import TimePattern

from .token import Token, TokenTypes


class Lex:
    _CMP = re.compile(r'==|<=|>=|!=|[<>]')
    _REG = 'hue saturation brightness kelvin red green blue duration time'
    _REG_LIST = _REG.split()
    _NON_ALNUM_LIST = r'[]{}()+-*/#:^'
    _NON_ALNUM_SPEC = r'==|<=|>=|[\[\]\(\){}+\-*<>/#:\^]'
    _NUMBER_SPEC = r'[0-9]*\.?[0-9]+'
    _STRING_SPEC = r'"([^"]|(?<=\\)")*"'
    _WORD_SPEC = r'[^\s\[\]{}+\-*/#:]+'

    _STRING = re.compile(_STRING_SPEC)
    _TOKEN = re.compile(
        '|'.join((TimePattern.REGEX_SPEC, _STRING_SPEC,
                  _NUMBER_SPEC, _NON_ALNUM_SPEC, _WORD_SPEC)))
    _NAME = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
    _NUMBER = re.compile(_NUMBER_SPEC)
    _TIME_PATTERN = TimePattern.REGEX
    _INT = re.compile(r'^\-?[0-9]*$')

    def __init__(self, input_string, source=''):
        self._lines = iter(input_string.split('\n'))
        self._source = source

    def tokens(self):
        line_num = 0
        for line in self._lines:
            line_num += 1
            for match in self._TOKEN.finditer(line):
                word = self._unabbreviate(
                    match.string[match.start():match.end()])
                if word == '#':
                    break
                if word in self._NON_ALNUM_LIST:
                    token_type = TokenTypes.MARK
                else:
                    token_type = self._token_type(word)
                    if token_type is TokenTypes.LITERAL_STRING:
                        word = word[1:-1]
                        word = word.replace(r'\"', '"')
                yield Token(token_type, word, line_num, self._source)
        yield Token(TokenTypes.EOF)

    @staticmethod
    def is_int(text):
        return Lex._INT.match(text) is not None

    def _token_type(self, word):
        token_type = TokenTypes.__members__.get(word.upper())
        if token_type is not None:
            return token_type
        if word in self._REG_LIST:
            return TokenTypes.REGISTER
        pairs = (
            (self._CMP, TokenTypes.COMPARE),
            (self._TIME_PATTERN, TokenTypes.TIME_PATTERN),
            (self._STRING, TokenTypes.LITERAL_STRING),
            (self._NUMBER, TokenTypes.NUMBER),
            (self._NAME, TokenTypes.NAME))
        for reg_expr, token_type in pairs:
            if reg_expr.match(word):
                return token_type
        return TokenTypes.ERROR

    @staticmethod
    def _unabbreviate(token):
        return {
            'H': 'hue', 'S': 'saturation', 'B': 'brightness', 'K': 'kelvin'
        }.get(token, token)
