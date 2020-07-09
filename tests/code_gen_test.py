#!/usr/bin/env python

import unittest
from bardolph.parser.code_gen import CodeGen
from bardolph.vm.instruction import Instruction
from bardolph.vm.vm_codes import JumpCondition, OpCode

class CodeGenTest(unittest.TestCase):
    def test_if_else(self):
        code_gen = CodeGen()
        marker = code_gen.if_true_start()
        code_gen.add_instruction(OpCode.NOP)
        code_gen.if_else(marker)
        code_gen.add_instruction(OpCode.NOP)
        code_gen.if_end(marker)

        marker = code_gen.if_true_start()
        code_gen.add_instruction(OpCode.NOP)
        code_gen.if_end(marker)

        self.assertListEqual(code_gen.program, [
            Instruction(OpCode.JUMP, JumpCondition.IF_FALSE, 3),
            Instruction(OpCode.NOP),
            Instruction(OpCode.JUMP, JumpCondition.ALWAYS, 2),
            Instruction(OpCode.NOP),
            Instruction(OpCode.JUMP, JumpCondition.IF_FALSE, 2),
            Instruction(OpCode.NOP)
        ])

if __name__ == '__main__':
    unittest.main()
