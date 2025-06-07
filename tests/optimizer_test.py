#!/usr/bin/env python

import unittest

from bardolph.controller import ls_asm
from bardolph.parser.optimizer import Optimizer
from bardolph.vm.vm_codes import JumpCondition, OpCode, Operand, Register


class OptimizerTest(unittest.TestCase):
    def test_quoted(self):
        raw_assembly = (
            OpCode.JUMP, JumpCondition.ALWAYS, 3,
            OpCode.PUSHQ, 1,
            OpCode.POP, Register.RESULT,
            OpCode.POWER,
            OpCode.WAIT
        )
        expected_assembly = (
            OpCode.JUMP, JumpCondition.ALWAYS, 2,
            OpCode.MOVEQ, 1, Register.RESULT,
            OpCode.POWER,
            OpCode.WAIT
        )
        expected_list = ls_asm.assemble(expected_assembly)
        optimized_list = Optimizer().optimize(ls_asm.assemble(raw_assembly))
        self.assertListEqual(expected_list, optimized_list)

    def test_unquoted(self):
        raw_assembly = (
            OpCode.JUMP, JumpCondition.ALWAYS, 3,
            OpCode.PUSH, "a",
            OpCode.POP, Register.RESULT,
            OpCode.POWER,
            OpCode.WAIT
        )
        expected_assembly = (
            OpCode.JUMP, JumpCondition.ALWAYS, 2,
            OpCode.MOVE, "a", Register.RESULT,
            OpCode.POWER,
            OpCode.WAIT
        )
        expected_list = ls_asm.assemble(expected_assembly)
        optimized_list = Optimizer().optimize(ls_asm.assemble(raw_assembly))
        self.assertListEqual(expected_list, optimized_list)

    def test_no_jump(self):
        raw_assembly = (
            OpCode.PUSH, "a",
            OpCode.POP, Register.RESULT,
            OpCode.POWER,
            OpCode.WAIT
        )
        expected_assembly = (
            OpCode.MOVE, "a", Register.RESULT,
            OpCode.POWER,
            OpCode.WAIT
        )
        expected_list = ls_asm.assemble(expected_assembly)
        optimized_list = Optimizer().optimize(ls_asm.assemble(raw_assembly))
        self.assertListEqual(expected_list, optimized_list)


if __name__ == '__main__':
    unittest.main()
