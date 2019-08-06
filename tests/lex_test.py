#!/usr/bin/env python

import unittest

from bardolph.parser.lex import Lex
from bardolph.parser.token_types import TokenTypes

class LexTest(unittest.TestCase):
    def test_all_tokens(self):
        input_string = 'all and brightness define # \n duration hue \
            off on kelvin saturation set time 01234 "Hello There"'
        
        expected_tokens = [
            TokenTypes.all, TokenTypes.and_operand, 
            TokenTypes.brightness, TokenTypes.define, TokenTypes.duration,
            TokenTypes.hue, TokenTypes.off, TokenTypes.on,
            TokenTypes.kelvin, TokenTypes.saturation, TokenTypes.set, 
            TokenTypes.time, TokenTypes.integer, TokenTypes.literal
        ]
        expected_strings = [
            "all", "and", "brightness", "define", "duration",
            "hue", "off", "on", "kelvin", "saturation", "set", "time", "01234",
            "Hello There"
        ]
        
        actual_tokens = []
        actual_strings = []
        
        lexer = Lex(input_string)
        (token_type, token) = lexer.next_token()
        while token_type != TokenTypes.eof and token_type != None:
            actual_tokens.append(token_type)
            actual_strings.append(token)
            (token_type, token) = lexer.next_token()
            
        self.assertEqual(token_type, TokenTypes.eof)
        self.assertListEqual(actual_tokens, expected_tokens)  
        self.assertListEqual(actual_strings, expected_strings)
        
        
if __name__ == '__main__':
    unittest.main()
