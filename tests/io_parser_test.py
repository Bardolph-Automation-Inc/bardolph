#!/usr/bin/env python

import logging
import os
import unittest

from bardolph.parser.parse import Parser
from bardolph.vm.instruction import Instruction
from bardolph.vm.vm_codes import IoOp, OpCode, Register


class IoParserTest(unittest.TestCase):
    def setUp(self):
        logging.getLogger().addHandler(logging.NullHandler())
        self.parser = Parser()

    def test_print(self):
        input_string = "print 1 print 2"
        self.assertIsNotNone(self.parser.parse(input_string))

    def test_println(self):
        input_string = 'println 10'
        self.assertIsNotNone(self.parser.parse(input_string))

    def test_printf(self):
        input_string = """
            assign y 60 define z "hello"
            printf "{} {brightness} {} {} {y} {}" 500 saturation "there" z
        """
        self.assertIsNotNone(self.parser.parse(input_string))


if __name__ == '__main__':
    unittest.main()
