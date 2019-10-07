#!/usr/bin/env python

import unittest

from bardolph.parser.lex import Lex
from bardolph.parser.token_types import TokenTypes

class LexTest(unittest.TestCase):
    def test_token_regex(self):
        test_input = """word "hello there you " 123.456 -abc- % 
            # comment1 # comment2"""
        expected_strings = [
            'word', '"hello there you "', '123.456',  '-abc-', '%',
            '# comment1 # comment2'
        ]
        actual_strings = [m.string[m.start():m.end()]
            for m in Lex.token_regex.finditer(test_input)]
        self.assertListEqual(actual_strings, expected_strings)
    
    def test_all_tokens(self):
        input_string = 'all and brightness define # comment \n duration hue \
            off on kelvin saturation set time 01.234\n"Hello There" @'
        
        expected_tokens = [
            TokenTypes.ALL, TokenTypes.AND, 
            TokenTypes.BRIGHTNESS, TokenTypes.DEFINE, TokenTypes.DURATION,
            TokenTypes.HUE, TokenTypes.OFF, TokenTypes.ON,
            TokenTypes.KELVIN, TokenTypes.SATURATION, TokenTypes.SET, 
            TokenTypes.TIME, TokenTypes.NUMBER, TokenTypes.LITERAL,
            TokenTypes.UNKNOWN
        ]
        expected_strings = [
            "all", "and", "brightness", "define", "duration",
            "hue", "off", "on", "kelvin", "saturation", "set", "time", "01.234",
            "Hello There", "@"
        ]
        self.lex_and_compare(input_string, expected_tokens, expected_strings)

    def test_abbreviations(self):
        input_string = 'h k s b'
        expected_tokens = [
            TokenTypes.HUE, TokenTypes.KELVIN, TokenTypes.SATURATION, 
            TokenTypes.BRIGHTNESS]
        expected_strings = [ "hue", "kelvin", "saturation", "brightness"]
        self.lex_and_compare(input_string, expected_tokens, expected_strings)

    def lex_and_compare(self, input_string, expected_tokens, expected_strings):
        actual_tokens = []
        actual_strings = []
        
        lexer = Lex(input_string)
        (token_type, token) = lexer.next_token()
        while token_type != TokenTypes.EOF and token_type != None:
            actual_tokens.append(token_type)
            actual_strings.append(token)
            (token_type, token) = lexer.next_token()
            
        self.assertEqual(token_type, TokenTypes.EOF)
        self.assertListEqual(actual_tokens, expected_tokens)  
        self.assertListEqual(actual_strings, expected_strings)    
        
if __name__ == '__main__':
    unittest.main()
