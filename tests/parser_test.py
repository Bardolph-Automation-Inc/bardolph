#!/usr/bin/env python

import logging
import unittest

from bardolph.controller.instruction import Instruction, OpCode
from bardolph.parser.parse import Parser

class ParserTest(unittest.TestCase):
    def setUp(self):
        logging.getLogger().addHandler(logging.NullHandler())
        self.parser = Parser()
        
    def good_input(self, input_string):
        self.assertTrue(self.parser.parse(input_string))
    
    def test_good_strings(self):
        input_strings = [ 
            '#abcde \n hue 5 \n #efghi \n ',
            '',
            'set "name with spaces"',
            'define table "Table" set table',
            'hue 5 saturation 10 set "Table"',
            'hue 5 set all',
            'get all get "Table" get group "group" get location "location"'
        ]
        for s in input_strings:    
            self.assertIsNotNone(self.parser.parse(s), s)

    def test_bad_keyword(self):
        input_string = 'on "Top" on "Bottom" on\n"Middle" Frank'
        self.assertFalse(self.parser.parse(input_string))
        self.assertIn("Unexpected input", self.parser.get_errors())

    def test_bad_number(self):
        input_string = "hue 5 saturation x"
        self.assertFalse(self.parser.parse(input_string))
        self.assertIn("Unknown parameter value", self.parser.get_errors())

    def test_optimizer(self):
        input_string = 'hue 5 saturation 10 hue 5 brightness 20'
        expected = [
            Instruction(OpCode.set_reg, "hue", 5), 
            Instruction(OpCode.set_reg, "saturation", 10), 
            Instruction(OpCode.set_reg, "brightness", 20)
        ]
        actual = self.parser.parse(input_string)
        self.assertEqual(expected, actual,
            "Optimizer failed: {} {}".format(expected, actual))
        
if __name__ == '__main__':
    unittest.main()
