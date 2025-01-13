import string

from bardolph.vm.vm_codes import IoOp, OpCode, Register

from .sub_parser import SubParser


class IoParser(SubParser):
    def print(self) -> bool:
        self.next_token()
        if self.at_rvalue():
            if not self._out_rvalue():
                return False
            self.code_gen.add_instruction(OpCode.OUT, IoOp.PRINT)
        return True

    def println(self) -> bool:
        if not self.print():
            return False
        self.code_gen.add_instruction(OpCode.OUT, IoOp.PRINT_END)
        return True

    def printf(self) -> bool:
        self.next_token()
        format_str = self.current_str
        if len(format_str) == 0:
            return self.token_error('Expected format specifier, got {}')
        self.next_token()

        num_unnamed = sum(
            (1 for field in string.Formatter().parse(format_str)
             if field[1] is not None
             and (len(field[1]) == 0 or field[1].isdecimal())))
        for field in range(0, num_unnamed):
            if not self._out_rvalue():
                return False
        self.code_gen.add_instruction(OpCode.OUT, IoOp.PRINTF, format_str)
        return True

    def _out_rvalue(self, end=None) -> bool:
        if not self.rvalue():
            return False
        self.code_gen.add_instruction(
            OpCode.OUT, IoOp.REGISTER, Register.RESULT)
        if end is not None:
            self.code_gen.add_instruction(OpCode.OUT, IoOp.LITERAL, end)
        return True
