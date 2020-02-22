#!/usr/bin/env python

import logging
import unittest

from bardolph.controller.instruction import Instruction, OpCode, Operand
from bardolph.controller.instruction import Register
from bardolph.controller.units import UnitMode
from bardolph.parser.parse import Parser


def _filter(inst_list):
    return [inst for inst in inst_list if inst.op_code == OpCode.MOVEQ]

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
        self.assertIn('Unknown name: "Frank"', self.parser.get_errors())

    def test_bad_number(self):
        input_string = "hue 5 saturation x"
        self.assertFalse(self.parser.parse(input_string))
        self.assertIn('Not a data variable: "x"', self.parser.get_errors())

    def test_single_zone(self):
        input_string = 'set "Strip" zone 7'
        expected = [
            Instruction(OpCode.MOVEQ, "Strip", Register.NAME),
            Instruction(OpCode.MOVEQ, 7, Register.FIRST_ZONE),
            Instruction(OpCode.MOVEQ, None, Register.LAST_ZONE),
            Instruction(OpCode.MOVEQ, Operand.MZ_LIGHT, Register.OPERAND),
        ]
        actual = _filter(self.parser.parse(input_string))
        self.assertEqual(expected, actual,
                         "Single zone failed: {} {}".format(expected, actual))

    def test_multi_zone(self):
        input_string = 'set "Strip" zone 3 5'
        expected = [
            Instruction(OpCode.MOVEQ, "Strip", Register.NAME),
            Instruction(OpCode.MOVEQ, 3, Register.FIRST_ZONE),
            Instruction(OpCode.MOVEQ, 5, Register.LAST_ZONE),
            Instruction(OpCode.MOVEQ, Operand.MZ_LIGHT, Register.OPERAND),
        ]
        actual = _filter(self.parser.parse(input_string))
        self.assertEqual(expected, actual,
                         "Multi-zone failed: {} {}".format(expected, actual))

    def test_optimizer(self):
        input_string = 'units raw set "name" brightness 20 set "name"'
        expected = [
            Instruction(OpCode.MOVEQ, UnitMode.RAW, Register.UNIT_MODE),
            Instruction(OpCode.MOVEQ, "name", Register.NAME),
            Instruction(OpCode.MOVEQ, Operand.LIGHT, Register.OPERAND),
            Instruction(OpCode.MOVEQ, 20.0, Register.BRIGHTNESS)
        ]
        raw_output = self.parser.parse(input_string)
        self.assertIsNotNone(raw_output, self.parser.get_errors())
        actual = _filter(raw_output)
        self.assertEqual(expected, actual,
                         "Optimizer failed: {} {}".format(expected, actual))

if __name__ == '__main__':
    unittest.main()
