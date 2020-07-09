from enum import Enum

from bardolph.controller.units import UnitMode
from bardolph.lib.auto_repl import auto
from bardolph.vm.vm_codes import LoopVar, OpCode, Operand
from bardolph.vm.vm_codes import Operator
from bardolph.vm.vm_codes import Register
from bardolph.vm.instruction import Instruction

from .code_gen import CodeGen
from .expr_parser import ExprParser
from .token_types import TokenTypes

class LoopType(Enum):
    ALL = auto()
    COUNTED = auto()
    GROUPS = auto()
    INFINITE = auto()
    LIGHTS = auto()
    LOCATIONS = auto()
    WHILE = auto()
    WITH = auto()

    def is_iter(self):
        # Some sort of iteration over lights.
        return self in (
            LoopType.ALL, LoopType.LIGHTS, LoopType.GROUPS, LoopType.LOCATIONS)

    def is_unbounded(self):
        # Number of iterations is indefinite.
        return self in (LoopType.INFINITE, LoopType.WHILE)


class LoopParser:
    def __init__(self, parser):
        self._loop_type = None
        self._parser = parser
        self._index_var = None
        self._light_var = None
        self._counter = None

    def repeat(self, code_gen, call_context) -> bool:
        # repeat
        # repeat numeric rvalue
        # repeat in
        # repeat all
        # repeat group, repeat location
        self._next_token()
        code_gen.add_instruction(OpCode.LOOP)
        if not self._detect_loop_type(code_gen):
            return False
        if not self._pre_loop(code_gen, call_context):
            return False
        loop_top = code_gen.mark()
        if not self._loop_test(code_gen):
            return False
        exit_loop_marker = code_gen.if_true_start()
        if not (self._loop_body(code_gen) and self._loop_post(code_gen)):
            return False
        code_gen.jump_back(loop_top)
        code_gen.if_end(exit_loop_marker)
        code_gen.add_instruction(OpCode.END_LOOP)
        return True

    def _next_token(self):
        return self._parser.next_token()

    def _detect_loop_type(self, code_gen) -> bool:
        self._loop_type = {
            TokenTypes.WHILE: LoopType.WHILE,
            TokenTypes.WITH: LoopType.WITH,
            TokenTypes.IN: LoopType.LIGHTS,
            TokenTypes.ALL: LoopType.ALL,
            TokenTypes.GROUP: LoopType.GROUPS,
            TokenTypes.LOCATION: LoopType.LOCATIONS
        }.get(self._current_token_type, None)
        if self._loop_type is None:
            if self._parser.at_rvalue():
                self._loop_type = LoopType.COUNTED
                if not self._parser.at_rvalue():
                    return False
            else:
                self._loop_type = LoopType.INFINITE
        elif self._loop_type not in (LoopType.ALL, LoopType.WITH):
            self._next_token()
        return True

    def _pre_loop(self, code_gen, call_context) -> bool:
        if self._loop_type.is_unbounded():
            return True

        if self._loop_type in (LoopType.ALL, LoopType.LIGHTS):
            code_gen.add_instruction(OpCode.MOVEQ, 0, LoopVar.COUNTER)
            if not (self._pre_loop_lights(code_gen, call_context) and
                    self._pre_loop_as(code_gen, call_context)):
                return False
        elif self._loop_type in (LoopType.GROUPS, LoopType.LOCATIONS):
            code_gen.add_instruction(OpCode.MOVEQ, 0, LoopVar.COUNTER)
            if not (self._pre_loop_sets(code_gen) and
                    self._pre_loop_as(code_gen, call_context)):
                return False
        elif (self._loop_type == LoopType.COUNTED
                and not self._parser.rvalue(LoopVar.COUNTER)):
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
            self._next_token()
            if not self._cycle_var_range(code_gen):
                return False
        else:
            return self._parser.token_error(
                'Needed "from" or "cycle", got "{}"')

        return True

    def _pre_loop_lights(self, code_gen, call_context) -> bool:
        """
        Process "all" or the list that follows "in" keyword.

        In that list, a light can be either a literal or an rvalue that
        evaluates to a string containing the light's name.

        Push each operand on the stack, last to first. Increment
        LoopVar.COUNTER so that it has the number of elements
        on the stack and can be used to control the loop.
        """
        if self._current_token_type == TokenTypes.AS:
            return True

        inner_coder = CodeGen()
        operand = {
            TokenTypes.ALL: Operand.ALL,
            TokenTypes.GROUP: Operand.GROUP,
            TokenTypes.LOCATION: Operand.LOCATION
        }.get(self._current_token_type, None)
        if operand is not None:
            self._next_token()
            self._push_set_contents(inner_coder, operand)
        else:
            # Name of a light
            if not self._parser.rvalue(Register.RESULT, inner_coder):
               return False
            inner_coder.push(Register.RESULT)
            inner_coder.plus_equals(LoopVar.COUNTER)

        if operand != Operand.ALL:
            if self._current_token_type == TokenTypes.AND:
                self._next_token()
                if (self._current_token_type not in
                            (TokenTypes.GROUP, TokenTypes.LOCATION)
                        and not self._parser.at_rvalue()):
                    return self._parser.token_error(
                        'Needed lights after "and", got "{}".')
                if not self._pre_loop_lights(code_gen, call_context):
                    return False

        code_gen.add_instructions(inner_coder.program)
        return True

    def _pre_loop_sets(self, code_gen) -> bool:
        """Generate code to push all group or location names onto the stack. """
        inner_code = CodeGen()
        inner_code.plus_equals(LoopVar.COUNTER)
        inner_code.push(LoopVar.CURRENT)
        if self._loop_type == LoopType.GROUPS:
            operand = Operand.GROUP
        else:
            operand = Operand.LOCATION
        code_gen.iter_sets_reverse(operand, inner_code.program)
        return True

    def _pre_loop_as(self, code_gen, call_context) -> bool:
        if self._current_token_type != TokenTypes.AS:
            return self._parser.token_error('Expected "as", got "{}"')
        self._next_token()
        if self._current_token_type != TokenTypes.NAME:
            return self._parser.token_error(
                'Expected name for lights, got "{}"')
        self._light_var = self._current_token
        call_context.add_variable(self._light_var)
        return self._next_token()

    def _push_set_contents(self, code_gen, operand) -> bool:
        """
        Generate code to push all light names, or the contents of a group
        or location onto the stack.
        """
        if (operand != Operand.ALL
                and not self._parser.rvalue(LoopVar.FIRST, code_gen)):
            return self._parser.token_error(
                'Needed name of a group or location, got "{}"')
        inner_code = CodeGen()
        inner_code.plus_equals(LoopVar.COUNTER)
        inner_code.push(LoopVar.CURRENT)
        code_gen.iter_lights_reverse(operand, inner_code.program)
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
        code_gen.add_instruction(OpCode.MOVE, LoopVar.FIRST, self._index_var)
        if self._loop_type == LoopType.WITH:
            if not self._calc_counter(code_gen):
                return False
        else:
            if not self._calc_incr(code_gen):
                return False
        return True

    def _calc_counter(self, code_gen) -> bool:
        # abs(last - first) + 1
        code_gen.subtraction(LoopVar.LAST, LoopVar.FIRST)
        code_gen.pop(LoopVar.COUNTER)
        code_gen.test_op(Operator.LT, LoopVar.COUNTER, 0)
        marker = code_gen.if_true_start()
        code_gen.times_equals(LoopVar.COUNTER, -1)
        code_gen.add_instruction(OpCode.MOVEQ, -1, LoopVar.INCR)
        code_gen.if_else(marker)
        code_gen.add_instruction(OpCode.MOVEQ, 1, LoopVar.INCR)
        code_gen.if_end(marker)
        code_gen.plus_equals(LoopVar.COUNTER)
        return True

    def _calc_incr(self, code_gen) -> bool:
        # increment = (last - first) / (count - 1)
        # If count == 1, increment = 0.
        code_gen.test_op(Operator.NOTEQ, LoopVar.COUNTER, 1)
        marker = code_gen.if_true_start()
        code_gen.subtraction(LoopVar.LAST, LoopVar.FIRST)
        code_gen.subtraction(LoopVar.COUNTER, 1)
        code_gen.add_list([
            (OpCode.OP, Operator.DIV),
            (OpCode.POP, LoopVar.INCR)
        ])
        code_gen.if_else(marker)
        code_gen.add_instruction(OpCode.MOVEQ, 0, LoopVar.INCR)
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
        marker = code_gen.if_true_start()
        code_gen.push(65536)
        code_gen.if_else(marker)
        code_gen.push(360)
        code_gen.if_end(marker)
        code_gen.push(LoopVar.COUNTER)
        code_gen.add_instruction(OpCode.OP, Operator.DIV)
        code_gen.add_instruction(OpCode.POP, LoopVar.INCR)
        return True

    def _loop_test(self, code_gen) -> bool:
        """Generate code to leave True or False in the result register,
        depending on whether the loop should continue.
        """
        if self._loop_type == LoopType.INFINITE:
            code_gen.add_instruction(OpCode.MOVEQ, True, Register.RESULT)
            return True
        if self._loop_type == LoopType.WHILE:
            exp = ExprParser(self._current_token)
            if not exp.generate_code(code_gen):
                return False
            code_gen.add_instruction(OpCode.POP, Register.RESULT)
            self._next_token()
        else:
            code_gen.test_op(Operator.GT, LoopVar.COUNTER, 0)
        return True

    def _loop_body(self, code_gen) -> bool:
        if self._loop_type.is_iter():
            code_gen.add_instruction(OpCode.POP, self._light_var)
        return self._parser.command_seq()

    def _loop_post(self, code_gen) -> bool:
        if self._loop_type in (LoopType.INFINITE, LoopType.WHILE):
            return True
        code_gen.minus_equals(LoopVar.COUNTER, 1)
        if self._index_var is not None:
            code_gen.plus_equals(self._index_var, LoopVar.INCR)
        return True

    @property
    def _current_operand_token(self):
        return {
            TokenTypes.GROUP: Operand.GROUP,
            TokenTypes.LOCATION: Operand.LOCATION
        }.get(self._current_token_type, None)

    @property
    def _current_token(self):
        return self._parser.current_token

    @property
    def _current_token_type(self):
        return self._parser.current_token_type

    def _next_token(self):
        return self._parser.next_token()
