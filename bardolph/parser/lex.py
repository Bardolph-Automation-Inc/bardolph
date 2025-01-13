import re
import sys

from bardolph.lib.time_pattern import TimePattern
from bardolph.parser.token import Token, TokenTypes


class Lex:
    _CMP_SPEC = r'==|<=|>=|!=|[<>]'
    _REG = ('hue saturation brightness kelvin red green blue default duration '
             'time')
    _REG_LIST = _REG.split()
    _NAME_SPEC = r'[a-zA-Z_][a-zA-Z0-9_]*'
    _NON_ALNUM_LIST = r'[]{}()+-*/#:^'
    _NON_ALNUM_SPEC = r'==|<=|>=|[\[\]\(\){}+\-*<>/#:\^]'
    _NUMBER_SPEC = r'[0-9]*\.?[0-9]+'
    _LITERAL_STRING_SPEC = r'"([^"]|(?<=\\)")*"'
    _DEFAULT_SPEC = '[^\s]+'

    _STRING = re.compile(_LITERAL_STRING_SPEC)
    _TOKEN_SPEC = '|'.join((
        TimePattern.REGEX_SPEC,
        _CMP_SPEC,
        _LITERAL_STRING_SPEC,
        _NUMBER_SPEC,
        _NAME_SPEC,
        _NON_ALNUM_SPEC,
        _DEFAULT_SPEC))

    _CMP = re.compile(_CMP_SPEC)
    _TOKEN = re.compile(_TOKEN_SPEC)
    _NAME = re.compile(_NAME_SPEC)
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
                matched = match.string[match.start():match.end()]
                u_matched = self._unabbreviate(matched)
                if u_matched == '#':
                    break
                if u_matched in self._NON_ALNUM_LIST:
                    token_type = TokenTypes.MARK
                else:
                    token_type = self._token_type(u_matched)
                    if token_type is TokenTypes.LITERAL_STRING:
                        u_matched = u_matched[1:-1]
                        u_matched = u_matched.replace(r'\"', '"')
                yield Token(token_type, u_matched, line_num, self._source)
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


def main():
    args = sys.argv[1:]
    for arg in args:
        print("lexing: {}\n".format(arg))
        lexer = Lex(arg)
        for token in lexer.tokens():
            print("token: {}\ntype: {}\n".format(
                str(token), token.token_type))


if __name__ == '__main__':
    main()
