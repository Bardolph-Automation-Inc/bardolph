#!/usr/bin/env python

import unittest

from bardolph.vm.instruction import Instruction
from bardolph.vm.machine import Machine
from bardolph.vm.vm_codes import OpCode, Operator
from tests import test_module


class VmMathTest(unittest.TestCase):
    def setUp(self):
        self._test_cases = (
            (-31, [
                Instruction(OpCode.PUSH, 17),
                Instruction(OpCode.PUSH, 23),
                Instruction(OpCode.OP, Operator.ADD),
                Instruction(OpCode.PUSH, 3),
                Instruction(OpCode.OP, Operator.MUL),
                Instruction(OpCode.PUSH, 5),
                Instruction(OpCode.PUSH, 2),
                Instruction(OpCode.OP, Operator.MUL),
                Instruction(OpCode.OP, Operator.DIV),
                Instruction(OpCode.PUSH, 43),
                Instruction(OpCode.OP, Operator.SUB)
            ]),
            (4, [
                Instruction(OpCode.PUSH, 20),
                Instruction(OpCode.PUSH, 5),
                Instruction(OpCode.OP, Operator.DIV)
            ]),
            (-500, [
                Instruction(OpCode.PUSH, 10000),
                Instruction(OpCode.PUSH, 20),
                Instruction(OpCode.OP, Operator.DIV),
                Instruction(OpCode.OP, Operator.USUB)
            ]),
            (True, [
                Instruction(OpCode.PUSH, 5),
                Instruction(OpCode.PUSH, 20),
                Instruction(OpCode.OP, Operator.LT)
            ]),
            (True, [
                Instruction(OpCode.PUSH, 17),
                Instruction(OpCode.PUSH, 23),
                Instruction(OpCode.OP, Operator.GT),
                Instruction(OpCode.OP, Operator.NOT)
            ])
        )
        test_module.configure()

    def _eval_test(self, code, expected):
        code.append(Instruction(OpCode.POP, "x"))
        machine = Machine()
        machine.run(code)
        self.assertEqual(machine.get_variable("x"), expected)

    def test_ops(self):
        for test_case in self._test_cases:
            self._eval_test(test_case[1], test_case[0])


if __name__ == '__main__':
    unittest.main()
