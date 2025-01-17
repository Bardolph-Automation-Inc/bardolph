#!/usr/bin/env python

from re import LOCALE
import unittest

from bardolph.parser.lex import Lex
from bardolph.parser.token import Token, TokenTypes

class LexTest(unittest.TestCase):
    def test_time_pattern(self):
        lexer = Lex('12:*4 *2:10 1*:01 *:21')
        token_num = 0
        for token in lexer.tokens():
            if token_num < 4:
                self.assertEqual(TokenTypes.TIME_PATTERN, token.token_type)
            else:
                self.assertEqual(TokenTypes.EOF, token.token_type)
            token_num += 1
        self.assertEqual(token_num, 5)

    def test_all_tokens(self):
        input_string = """(99) all and as at blue brightness
            define # comment \n column default duration green hue if in
            off on or kelvin logical print printf println raw red return rgb
            row saturation set stage time wait zone 12:*4 {3 * 4} ^
            -1.0 01.234\n"Hello There" x _abc @ [ ] < <= > >= == !="""
        expected = [
            TokenTypes.MARK, '(',
            TokenTypes.NUMBER,'99',
            TokenTypes.MARK, ')',
            TokenTypes.ALL, 'all',
            TokenTypes.AND, 'and',
            TokenTypes.AS, 'as',
            TokenTypes.AT, 'at',
            TokenTypes.REGISTER, 'blue',
            TokenTypes.REGISTER, 'brightness',
            TokenTypes.DEFINE,'define',
            TokenTypes.COLUMN, 'column',
            TokenTypes.DEFAULT, 'default',
            TokenTypes.REGISTER, 'duration',
            TokenTypes.REGISTER, 'green',
            TokenTypes.REGISTER,'hue',
            TokenTypes.IF, 'if',
            TokenTypes.IN, 'in',
            TokenTypes.OFF, 'off',
            TokenTypes.ON,'on',
            TokenTypes.OR, 'or',
            TokenTypes.REGISTER, 'kelvin',
            TokenTypes.LOGICAL,'logical',
            TokenTypes.PRINT, 'print',
            TokenTypes.PRINTF, 'printf',
            TokenTypes.PRINTLN,'println',
            TokenTypes.RAW, 'raw',
            TokenTypes.REGISTER, 'red',
            TokenTypes.RETURN, 'return',
            TokenTypes.RGB,'rgb',
            TokenTypes.ROW, 'row',
            TokenTypes.REGISTER, 'saturation',
            TokenTypes.SET, 'set',
            TokenTypes.STAGE, 'stage',
            TokenTypes.REGISTER, 'time',
            TokenTypes.WAIT, 'wait',
            TokenTypes.ZONE, 'zone',
            TokenTypes.TIME_PATTERN, '12:*4',
            TokenTypes.MARK, '{',
            TokenTypes.NUMBER, '3',
            TokenTypes.MARK, '*',
            TokenTypes.NUMBER, '4',
            TokenTypes.MARK, '}',
            TokenTypes.MARK, '^',
            TokenTypes.MARK, '-',
            TokenTypes.NUMBER,'1.0',
            TokenTypes.NUMBER, '01.234',
            TokenTypes.LITERAL_STRING, 'Hello There',
            TokenTypes.NAME,'x',
            TokenTypes.NAME, '_abc',
            TokenTypes.ERROR, '@',
            TokenTypes.MARK, '[',
            TokenTypes.MARK, ']',
            TokenTypes.COMPARE, '<',
            TokenTypes.COMPARE, '<=',
            TokenTypes.COMPARE, '>',
            TokenTypes.COMPARE, '>=',
            TokenTypes.COMPARE, '==',
            TokenTypes.COMPARE, '!=' ]
        self._lex_and_compare_pairs(input_string, expected)

    def test_unary_ops(self):
        input_string = "-2+34"
        expected = [
            TokenTypes.MARK, '-',
            TokenTypes.NUMBER,'2',
            TokenTypes.MARK, '+',
            TokenTypes.NUMBER, '34',
        ]
        self._lex_and_compare_pairs(input_string, expected)

    def test_abbreviations(self):
        input_string = 'H S B K'
        expected = ('hue', 'saturation', 'brightness', 'kelvin')
        self._lex_and_compare_same(input_string, TokenTypes.REGISTER, expected)

    def test_embedded_keywords(self):
        input_string = '''
            a_hue saturation_z _brightness_ kelvinkelvin xblue
            y_green redred
        '''
        expected = ('a_hue', 'saturation_z', '_brightness_', 'kelvinkelvin',
            'xblue','y_green', 'redred')
        self._lex_and_compare_same(input_string, TokenTypes.NAME, expected)

    def test_comment(self):
        input_string = 'a "b # c" # def "ghi" jkl'
        expected = [
            TokenTypes.NAME, 'a',
            TokenTypes.LITERAL_STRING, 'b # c']
        self._lex_and_compare_pairs(input_string, expected)

    def test_paren_name(self):
        input_string = '(abc)'
        expected = [
            TokenTypes.MARK, '(',
            TokenTypes.NAME, 'abc',
            TokenTypes.MARK, ')']
        self._lex_and_compare_pairs(input_string, expected)

    def test_mixed_in_string(self):
        input_string = r'assign a "hello\"there" b'
        expected = [
            TokenTypes.ASSIGN, 'assign',
            TokenTypes.NAME, 'a',
            TokenTypes.LITERAL_STRING, 'hello"there',
            TokenTypes.NAME, 'b'
        ]
        self._lex_and_compare_pairs(input_string, expected)

    def _lex_and_compare_pairs(self, input_string, expected):
        it = iter(expected)
        expected_tokens = [Token(token_type, next(it)) for token_type in it]
        self._lex_and_compare(input_string, expected_tokens)

    def _lex_and_compare_same(self, input_string, token_type, expected):
        expected_tokens = [Token(token_type, word) for word in expected]
        self._lex_and_compare(input_string, expected_tokens)

    def _lex_and_compare(self, input_string, expected):
        expected.append(Token(TokenTypes.EOF))
        actual = list(Lex(input_string).tokens())
        self.assertListEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
