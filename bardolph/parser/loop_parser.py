from enum import Enum

from bardolph.controller.units import UnitMode
from bardolph.lib.auto_repl import auto
from bardolph.vm.vm_codes import LoopVar, OpCode
from bardolph.vm.vm_codes import Operator
from bardolph.vm.vm_codes import Register

from .expr_parser import ExprParser
from .token_types import TokenTypes

class LoopType(Enum):
    INFINITE = auto()
    COUNTED = auto()
    CYCLE = auto()
    UNTIL = auto()
    WHILE = auto()


class LoopParser:
    def __init__(self, parser):
        self._loop_type = None
        self._parser = parser
        self._index_var = None
        self._counter = None

    def repeat(self, code_gen, call_context) -> bool:
        self._next_token()
        if not self._detect_loop_type(code_gen):
            return False
        if not self._pre_loop(code_gen, call_context):
            return False
        loop_top = code_gen.mark()
        if not self._loop_test(code_gen):
            return False
        if self._loop_type != LoopType.INFINITE:
            exit_loop_marker = code_gen.if_start()
        if not (self._loop_body() and self._loop_post(code_gen)):
            return False
        code_gen.jump_back(loop_top)
        if self._loop_type != LoopType.INFINITE:
            code_gen.if_end(exit_loop_marker)
        code_gen.add_instruction(OpCode.END_LOOP)
        return True

    def _detect_loop_type(self, code_gen) -> bool:
        code_gen.add_instruction(OpCode.LOOP)
        self._loop_type = LoopType.INFINITE
        if self._current_token_type == TokenTypes.WHILE:
            self._loop_type = LoopType.WHILE
            self._next_token()
        elif self._parser.at_rvalue():
            self._loop_type = LoopType.COUNTED
        return True

    def _pre_loop(self, code_gen, call_context) -> bool:
        if self._loop_type != LoopType.COUNTED:
            return True
        if not self._parser.rvalue(LoopVar.COUNTER):
            return False
        if self._current_token_type != TokenTypes.WITH:
            return True
        self._next_token()
        if not self._init_index_var(call_context):
            return False
        if self._current_token_type == TokenTypes.FROM:
            self._next_token()
            if not self._index_var_range(code_gen):
                return False
        elif self._current_token_type == TokenTypes.CYCLE:
            self._loop_type = LoopType.CYCLE
            self._next_token()
            if not self._cycle_var_range(code_gen):
                return False
        else:
            return self._parser.token_error(
                'Needed "from" or "cycle", got "{}"')
        return True

    def _init_index_var(self, call_context) -> bool:
        if self._current_token_type != TokenTypes.NAME:
            return self._parser.token_error('Needed variable name, got "{}"')
        self._index_var = self._current_token
        call_context.add_variable(self._index_var)
        return self._next_token()

    def _index_var_range(self, code_gen) -> bool:
        if not self._parser.rvalue(LoopVar.FIRST):
            return False
        if self._current_token_type != TokenTypes.TO:
            return self._parser.token_error('Needed "to", got "{}"')
        self._next_token()
        if not self._parser.rvalue(LoopVar.LAST):
            return False

        # increment = (last - first) / (count - 1)
        # If count == 1, skip to avoid division by 0.
        code_gen.add_instruction(OpCode.MOVE, LoopVar.FIRST, self._index_var)
        code_gen.test_op(Operator.NOTEQ, LoopVar.COUNTER, 1)
        marker = code_gen.if_start()
        code_gen.subtraction(LoopVar.LAST, LoopVar.FIRST)
        code_gen.subtraction(LoopVar.COUNTER, 1)
        code_gen.add_list([
            (OpCode.OP, Operator.DIV),
            (OpCode.POP, LoopVar.INCR)
        ])
        code_gen.if_end(marker)
        return True

    def _cycle_var_range(self, code_gen):
        if not self._parser.at_rvalue():
            code_gen.add_instruction(OpCode.MOVEQ, 0, LoopVar.FIRST)
        elif not self._parser.rvalue(LoopVar.FIRST):
            return False

        # increment = 360 / counter, or
        # increment = 65536 / counter
        code_gen.add_instruction(OpCode.MOVE, LoopVar.FIRST, self._index_var)
        code_gen.test_op(Operator.EQ, Register.UNIT_MODE, UnitMode.RAW)
        marker = code_gen.if_start()
        code_gen.push(65536)
        code_gen.if_else(marker)
        code_gen.push(360)
        code_gen.if_end(marker)
        code_gen.add_instruction(OpCode.PUSH, LoopVar.COUNTER)
        code_gen.add_instruction(OpCode.OP, Operator.DIV)
        code_gen.add_instruction(OpCode.POP, LoopVar.INCR)
        return True

    def _loop_test(self, code_gen) -> bool:
        if self._loop_type == LoopType.INFINITE:
            return True
        if self._loop_type == LoopType.WHILE:
            exp = ExprParser(self._current_token)
            if not exp.generate_code(code_gen):
                return False
            self._next_token()
        else:
            code_gen.add_list([
                (OpCode.PUSH, LoopVar.COUNTER),
                (OpCode.PUSHQ, 0),
                (OpCode.OP, Operator.GT)
            ])
        code_gen.add_instruction(OpCode.POP, Register.RESULT)
        return True

    def _loop_body(self) -> bool:
        return self._parser.command_seq()

    def _loop_post(self, code_gen) -> bool:
        if self._loop_type not in (LoopType.COUNTED, LoopType.CYCLE):
            return True
        code_gen.decrement(LoopVar.COUNTER)
        if self._index_var is not None:
            code_gen.addition(self._index_var, LoopVar.INCR)
            code_gen.add_instruction(OpCode.POP, self._index_var)
        return True

    @property
    def _current_token(self):
        return self._parser.current_token

    @property
    def _current_token_type(self):
        return self._parser.current_token_type

    def _next_token(self):
        return self._parser.next_token()
