from bardolph.parser.code_gen import CodeGen
from bardolph.parser.context import Context
from bardolph.parser.token import Token
from bardolph.vm.vm_codes import Register

class SubParser:
    def __init__(self, parser):
        self.parser = parser

    @property
    def current_token(self) -> Token:
        return self.parser.current_token

    @property
    def code_gen(self) -> CodeGen:
        return self.parser._code_gen

    @property
    def context(self) -> Context:
        return self.parser._context

    @property
    def current_int(self) -> int | None:
        return self.parser._current_int()

    @property
    def current_float(self) -> float | None:
        return self.parser._current_float()

    @property
    def current_str(self) -> str | None:
        return self.parser._current_str()

    @property
    def current_reg(self) -> Register | None:
        return self.parser._current_reg()

    @property
    def current_literal(self) -> str | None:
        return self.parser._current_literal()

    def next_token(self) -> bool:
        return self.parser.next_token()

    def rvalue(self, code_gen: CodeGen = None):
        return self.parser._rvalue(code_gen or self.code_gen)

    def rvalue_str(self, code_gen: CodeGen = None):
        return self.parser._rvalue_str(code_gen or self.code_gen)

    def at_rvalue(self, include_reg: bool = True):
        return self.parser._at_rvalue(include_reg)

    def trigger_error(self, msg: str) -> bool:
        return self.parser.trigger_error(msg)

    def token_error(self, fmt: str) -> bool:
        return self.parser.token_error(fmt)
