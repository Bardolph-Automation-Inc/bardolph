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
        if str(self.current_token) == '{':
            return self._out_expr()
        fn =  {
            TokenTypes.REGISTER: self._out_reg,
            TokenTypes.NAME: self._out_symbol,
            TokenTypes.LITERAL_STRING:  self._out_literal,
            TokenTypes.NUMBER: self._out_literal
        }.get(self.current_token.token_type, self._out_unprintable)
        return fn()

    def _out_expr(self) -> bool:
        if not self.expr(Register.RESULT, self.code_gen):
            return False
        self._code_out_reg()
        return True

    def _out_reg(self) -> bool:
        self._code_out_reg(self.current_reg)
        return self.next_token()

    def _out_symbol(self) -> bool:
        name = str(self.current_token)
        if not self.context.has_symbol_typed(
                name, SymbolType.MACRO, SymbolType.VAR):
            return self.token_error('Unknown: {}')
        self.code_gen.add_instruction(OpCode.MOVE, name, Register.RESULT)
        self._code_out_reg()
        return self.next_token()

    def _out_literal(self) -> bool:
        literal = self.current_literal
        if literal is None:
            return False
        self.code_gen.add_instruction(OpCode.MOVEQ, literal, Register.RESULT)
        self._code_out_reg()
        return self.next_token()

    def _out_unprintable(self):
        return self.token_error('Unprintable: {}')

    def _code_out_reg(self, reg=Register.RESULT) -> None:
        self.code_gen.add_instruction(OpCode.OUT, IoOp.REGISTER, reg)

    def _code_out_string(self, out_str) -> None:
        self.code_gen.add_instruction(OpCode.MOVEQ, out_str, Register.RESULT)
        self._code_out_reg()
