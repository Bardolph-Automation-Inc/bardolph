import os
from dataclasses import dataclass
from typing import Any

from bardolph.vm.vm_codes import OpCode


@dataclass
class Instruction:
    op_code: OpCode
    param0: Any | None = None
    param1: Any | None = None

    def __repr__(self):
        if self.op_code is OpCode.TIME_PATTERN:
            return 'Instruction({}, {}, {})'.format(
                OpCode.TIME_PATTERN, self.param0, repr(self.param1))
        if self.param1 is None:
            if self.param0 is None:
                return 'Instruction({})'.format(self.op_code)
            return 'Instruction({}, {})'.format(
                self.op_code,
                Instruction.quote_if_string(self.param0))
        return 'Instruction({}, {}, {})'.format(
            self.op_code,
            Instruction.quote_if_string(self.param0),
            Instruction.quote_if_string(self.param1))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError
        return (self.op_code == other.op_code
                and self.param0 == other.param0
                and self.param1 == other.param1)

    def nop(self):
        self.op_code = OpCode.NOP

    def _code_output(self, op_code_str) -> str:
        if self.param0 is None and self.param1 is None:
            return str(op_code_str)
        if self.param1 is None:
            return '{}, {}'.format(
                op_code_str,
                Instruction.quote_if_string(self.param0))
        if self.param1 is os.linesep:
            param1 = repr(os.linesep)
        else:
            param1 = Instruction.quote_if_string(self.param1)
        return '{}, {}, {}'.format(
            op_code_str, Instruction.quote_if_string(self.param0), param1)

    def as_list_text(self) -> str:
        return self._code_output(self.op_code.name)

    def asm(self) -> str:
        return self._code_output(str(self.op_code.name))

    def ctor(self) -> str:
        return self._code_output('OpCode.' + str(self.op_code.name))

    @staticmethod
    def quote_if_string(obj):
        if obj == '\n':
            obj = r'\n'
        return ('"{}"' if isinstance(obj, str) else '{}').format(obj)

    @staticmethod
    def do_listing(program):
        result = ''
        for inst_num, inst in enumerate(program):
            result += '{:5d} {}\n'.format(inst_num, inst)
        return result
