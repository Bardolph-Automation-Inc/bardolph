#!/usr/bin/env python

import logging
import unittest
from bardolph.parser.code_gen import CodeGen

from bardolph.parser.parse import Parser
from bardolph.vm.instruction import Instruction
from bardolph.vm.vm_codes import OpCode, Operand, Operator, Register


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
        self.assertIn('Unknown: "x"', self.parser.get_errors())

    def test_overwrite_constant(self):
        input_string = 'define x 5 assign x 6'
        self.assertFalse(self.parser.parse(input_string))
        self.assertIn('Attempt to assign to constant', self.parser.get_errors())

    def test_single_zone(self):
        input_string = 'set "Strip" zone 7'
        code_gen = CodeGen()
        code_gen.add_list(
            OpCode.WAIT,
            (OpCode.MOVEQ, "Strip", Register.NAME),
            (OpCode.MOVEQ, 7, Register.FIRST_ZONE),
            (OpCode.MOVEQ, None, Register.LAST_ZONE),
            (OpCode.MOVEQ, Operand.MZ_LIGHT, Register.OPERAND),
            (OpCode.COLOR)
        )
        expected = code_gen.program
        self.assertTrue(self.parser.parse(input_string))
        actual = self.parser.get_program()
        self.assertEqual(expected, actual,
                         "Single zone failed: {} {}".format(expected, actual))

    def test_multi_zone(self):
        input_string = 'set "Strip" zone 3 5'
        code_gen = CodeGen()
        code_gen.add_list(
            OpCode.WAIT,
            (OpCode.MOVEQ, "Strip", Register.NAME),
            (OpCode.MOVEQ, 3, Register.FIRST_ZONE),
            (OpCode.MOVEQ, 5, Register.LAST_ZONE),
            (OpCode.MOVEQ, Operand.MZ_LIGHT, Register.OPERAND),
            (OpCode.COLOR)
        )
        expected = code_gen.program
        self.assertTrue(self.parser.parse(input_string))
        actual = self.parser.get_program()
        self.assertEqual(expected, actual,
                         "Multi-zone failed: {} {}".format(expected, actual))

    def test_expr_space(self):
        input_string = 'assign x { 3 * 4 }'
        code_gen = CodeGen()
        code_gen.add_list(
            (OpCode.PUSHQ, 3),
            (OpCode.PUSHQ, 4),
            (OpCode.OP, Operator.MUL),
            (OpCode.POP, "x")
        )
        expected = code_gen.program
        self.assertTrue(self.parser.parse(input_string))
        actual = self.parser.get_program()
        self.assertEqual(expected, actual, "Error with space in expression.")


if __name__ == '__main__':
    unittest.main()
