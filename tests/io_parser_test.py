#!/usr/bin/env python

import logging
import unittest

from bardolph.parser.parse import Parser
from bardolph.vm.instruction import Instruction
from bardolph.vm.vm_codes import IoOp, OpCode, Register


class IoParserTest(unittest.TestCase):
    def setUp(self):
        logging.getLogger().addHandler(logging.NullHandler())
        self.parser = Parser()

    def test_print(self):
        input_string = "assign y 100 print y print y"
        expected = [
            Instruction(OpCode.MOVEQ, 100, "y"),
            Instruction(OpCode.MOVE, "y", Register.RESULT),
            Instruction(OpCode.OUT, IoOp.REGISTER, Register.RESULT),
            Instruction(OpCode.OUT, IoOp.PRINT),
            Instruction(OpCode.MOVE, "y", Register.RESULT),
            Instruction(OpCode.OUT, IoOp.REGISTER, Register.RESULT),
            Instruction(OpCode.OUT, IoOp.PRINT)
        ]
        actual = self.parser.parse(input_string)
        self.assertEqual(
            expected, actual,
            "print test failed: {} {}".format(expected, actual))

    def test_println(self):
        input_string = 'println 10'
        expected = [
            Instruction(OpCode.MOVEQ, 10, Register.RESULT),
            Instruction(OpCode.OUT, IoOp.REGISTER, Register.RESULT),
            Instruction(OpCode.OUT, IoOp.PRINTLN)
        ]
        actual = self.parser.parse(input_string)
        self.assertEqual(
            expected, actual,
            'println test failed: {} {}'.format(expected, actual))

    def test_printf(self):
        input_string = """
            assign y 60 define z "hello"
            printf "{} {brightness} {} {} {y} {}" 500 saturation "there" z
        """
        expected = [
            Instruction(OpCode.MOVEQ, 60, 'y'),
            Instruction(OpCode.CONSTANT, 'z', 'hello'),

            Instruction(OpCode.MOVEQ, 500, Register.RESULT),
            Instruction(OpCode.OUT, IoOp.REGISTER, Register.RESULT),
            Instruction(OpCode.OUT, IoOp.REGISTER, Register.SATURATION),
            Instruction(OpCode.MOVEQ, 'there', Register.RESULT),
            Instruction(OpCode.OUT, IoOp.REGISTER, Register.RESULT),
            Instruction(OpCode.MOVE, 'z', Register.RESULT),
            Instruction(OpCode.OUT, IoOp.REGISTER, Register.RESULT),
            Instruction(
                OpCode.OUT, IoOp.PRINTF, "{} {brightness} {} {} {y} {}")
        ]
        actual = self.parser.parse(input_string)
        self.assertEqual(
            expected, actual,
            "printf test failed: {} {}".format(expected, actual))


if __name__ == '__main__':
    unittest.main()
