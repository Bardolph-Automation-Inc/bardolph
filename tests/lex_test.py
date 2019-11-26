#!/usr/bin/env python

import unittest

from bardolph.parser.lex import Lex
from bardolph.parser.token_types import TokenTypes

class LexTest(unittest.TestCase):
    def test_token_regex(self):
        test_input = """word "hello there you " 123.456 -abc- %
            # comment1 # comment2"""
        expected_strings = [
            'word', '"hello there you "', '123.456', '-abc-', '%',
            '# comment1 # comment2'
        ]
        actual_strings = [m.string[m.start():m.end()]
                          for m in Lex.TOKEN_REGEX.finditer(test_input)]
        self.assertListEqual(actual_strings, expected_strings)

    def test_time_pattern(self):
        lexer = Lex('12:34')
        (token_type, _) = lexer.next_token()
        self.assertEqual(TokenTypes.TIME_PATTERN, token_type)
    
    def test_all_tokens(self):
        input_string = 'all and at brightness \
            define # comment \n duration hue \
            off on or kelvin saturation set time zone 12:*4 \
            01.234\n"Hello There"@'
        expected_tokens = [
            TokenTypes.ALL, TokenTypes.AND, TokenTypes.AT, TokenTypes.REGISTER,
            TokenTypes.DEFINE, TokenTypes.REGISTER, TokenTypes.REGISTER,
            TokenTypes.OFF, TokenTypes.ON, TokenTypes.OR, TokenTypes.REGISTER,
            TokenTypes.REGISTER, TokenTypes.SET, TokenTypes.REGISTER,
            TokenTypes.ZONE, TokenTypes.TIME_PATTERN, TokenTypes.NUMBER,
            TokenTypes.LITERAL, TokenTypes.UNKNOWN
        ]
        expected_strings = [
            'all', 'and', 'at', 'brightness', 'define', 'duration',
            'hue', 'off', 'on', 'or', 'kelvin', 'saturation', 'set',
            'time', 'zone', '12:*4', '01.234', 'Hello There', '@'
        ]
        self.lex_and_compare(input_string, expected_tokens, expected_strings)

    def test_abbreviations(self):
        input_string = 'h k s b'
        expected_tokens = [TokenTypes.REGISTER for _ in range(0, 4)]
        expected_strings = ['hue', 'kelvin', 'saturation', 'brightness']
        self.lex_and_compare(input_string, expected_tokens, expected_strings)

    def lex_and_compare(self, input_string, expected_tokens, expected_strings):
        actual_tokens = []
        actual_strings = []

        lexer = Lex(input_string)
        (token_type, token) = lexer.next_token()
        while token_type not in (TokenTypes.EOF, None):
            actual_tokens.append(token_type)
            actual_strings.append(token)
            (token_type, token) = lexer.next_token()

        self.assertEqual(token_type, TokenTypes.EOF)
        self.assertListEqual(actual_tokens, expected_tokens)
        self.assertListEqual(actual_strings, expected_strings)

if __name__ == '__main__':
    unittest.main()
