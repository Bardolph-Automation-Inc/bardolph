import os

from .vm_codes import OpCode


class Instruction:
    def __init__(self, op_code, param0=None, param1=None):
        self.op_code = op_code
        self.param0 = param0
        self.param1 = param1

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

    def as_list_text(self) -> str:
        if self.param0 is None and self.param1 is None:
            return str(self.op_code)
        if self.param1 is None:
            return '{}, {}'.format(
                self.op_code,
                Instruction.quote_if_string(self.param0))
        if self.param1 is os.linesep:
            param1 = repr(os.linesep)
        else:
            param1 = Instruction.quote_if_string(self.param1)
        return '{}, {}, {}'.format(
            self.op_code, Instruction.quote_if_string(self.param0), param1)

    @staticmethod
    def quote_if_string(obj):
        return ('"{}"' if isinstance(obj, str) else '{}').format(obj)

    @staticmethod
    def do_listing(program):
        result = ''
        inst_num = 0
        for inst in program:
            result += '{:5d} {}\n'.format(inst_num, inst)
            inst_num += 1
        return result
