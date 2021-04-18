import os
import string

from bardolph.lib.symbol import SymbolType
from bardolph.parser.token import TokenTypes
from bardolph.vm.vm_codes import IoOp, OpCode, Register

from .sub_parser import SubParser


class IoParser(SubParser):
    def print(self) -> bool:
        self.next_token()
        if not self._out_current_token():
            return False
        self.code_gen.add_instruction(OpCode.OUT, IoOp.PRINT, ' ')
        return True

    def println(self) -> bool:
        self.next_token()
        if not self._out_current_token():
            return False
        self.code_gen.add_instruction(OpCode.OUT, IoOp.PRINT, os.linesep)
        return True

    def printf(self) -> bool:
        self.next_token()
        format_str = self.current_str
        if len(format_str) == 0:
            return self.token_error('Expected format specifier, got {}')
        self.next_token()
        for field in string.Formatter().parse(format_str):
            spec = field[1] or ''
            if len(spec) == 0 or spec.isdecimal():
                if not self._out_current_token():
                    return False
        self.code_gen.add_instruction(OpCode.OUT, IoOp.PRINTF, format_str)
        return True

    def _out_current_token(self) -> bool:
        if not self.rvalue():
            return False
        self.code_gen.add_instruction(
            OpCode.OUT, IoOp.REGISTER, Register.RESULT)
        return True
