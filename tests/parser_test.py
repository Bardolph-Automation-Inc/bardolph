#!/usr/bin/env python

import logging
import unittest

from bardolph.controller.instruction import Instruction, OpCode, Operand 
from bardolph.controller.instruction import Register
from bardolph.controller.units import UnitMode
from bardolph.parser.parse import Parser


def _filter(inst_list):
    return [inst for inst in inst_list
            if inst.op_code == OpCode.SET_REG
                and inst.param0 != Register.SERIES]
        
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
            'get "Table"',
            'get "Table" zone 0'
        ]
        for string in input_strings:
            self.assertIsNotNone(self.parser.parse(string), string)

    def test_bad_keyword(self):
        input_string = 'on "Top" on "Bottom" on\n"Middle" Frank'
        self.assertFalse(self.parser.parse(input_string))
        self.assertIn("Unexpected input", self.parser.get_errors())

    def test_bad_number(self):
        input_string = "hue 5 saturation x"
        self.assertFalse(self.parser.parse(input_string))
        self.assertIn("Unknown parameter value", self.parser.get_errors())
        
    def test_multi_zone(self):
        input_string = 'set "Strip" zone 3 5'
        expected = [
            Instruction(OpCode.SET_REG, Register.NAME, "Strip"),
            Instruction(OpCode.SET_REG, Register.FIRST_ZONE, 3),
            Instruction(OpCode.SET_REG, Register.LAST_ZONE, 5),
            Instruction(OpCode.SET_REG, Register.OPERAND, Operand.MZ_LIGHT),
        ]
        actual = _filter(self.parser.parse(input_string))
        self.assertEqual(expected, actual,
                         "Multi-zone failed: {} {}".format(expected, actual))

    def test_optimizer(self):
        input_string = 'units raw set "name" brightness 20 set "name"'
        expected = [
            Instruction(OpCode.SET_REG, Register.UNIT_MODE, UnitMode.RAW),
            Instruction(OpCode.SET_REG, Register.NAME, "name"),
            Instruction(OpCode.SET_REG, Register.OPERAND, Operand.LIGHT),
            Instruction(OpCode.SET_REG, Register.BRIGHTNESS, 20)
        ]
        raw_output = self.parser.parse(input_string)
        self.assertIsNotNone(raw_output, self.parser.get_errors())
        actual = _filter(raw_output)
        self.assertEqual(expected, actual,
                         "Optimizer failed: {} {}".format(expected, actual))

if __name__ == '__main__':
    unittest.main()
