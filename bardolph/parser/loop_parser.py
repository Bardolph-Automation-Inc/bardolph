from enum import Enum, auto

from bardolph.controller.units import UnitMode
from bardolph.vm.vm_codes import LoopVar, OpCode, Operand, Operator, Register

from .code_gen import CodeGen
from .sub_parser import SubParser
from .token import TokenTypes


class _LoopType(Enum):
    ALL = auto()
    COUNTED = auto()
    GROUPS = auto()
    INFINITE = auto()
    LIST = auto()
    LOCATIONS = auto()
    WHILE = auto()
    WITH = auto()

    def is_unbounded(self):
        # Number of iterations is indefinite.
        return self in (_LoopType.INFINITE, _LoopType.WHILE)

    def is_iter(self):
        # Iteration that pushes names onto the stack.
        return self in (_LoopType.ALL, _LoopType.GROUPS, _LoopType.LIST,
            _LoopType.LOCATIONS)


class LoopParser(SubParser):
    def __init__(self, parser):
        super().__init__(parser)
        self._loop_type = None
        self._index_var = None
        self._light_var = None
        self._counter = None

    def repeat(self, code_gen, context_stack) -> bool:
        self.next_token()
        context_stack.enter_loop()
        code_gen.add_instruction(OpCode.LOOP)
        if not self._detect_loop_type():
            return False
        if not self._pre_loop(code_gen, context_stack):
            return False
        loop_top = code_gen.mark()
        if not self._loop_test(code_gen):
            return False
        exit_loop_marker = code_gen.if_true_start()
        if not (self._loop_body(code_gen) and self._loop_post(code_gen)):
            return False
        code_gen.jump_back(loop_top)
        code_gen.if_end(exit_loop_marker)
        context_stack.fix_break_addrs(code_gen)
        code_gen.add_instruction(OpCode.END_LOOP)
        context_stack.exit_loop()
        return True

    def _detect_loop_type(self) -> bool:
        self._loop_type = {
            TokenTypes.WHILE: _LoopType.WHILE,
            TokenTypes.WITH: _LoopType.WITH,
            TokenTypes.IN: _LoopType.LIST,
            TokenTypes.ALL: _LoopType.ALL,
            TokenTypes.GROUP: _LoopType.GROUPS,
            TokenTypes.LOCATION: _LoopType.LOCATIONS
        }.get(self.current_token.token_type)
        if self._loop_type is None:
            if self.at_rvalue():
                self._loop_type = _LoopType.COUNTED
            else:
                self._loop_type = _LoopType.INFINITE
        elif self._loop_type not in (_LoopType.ALL, _LoopType.WITH):
            self.next_token()
        return True

    def _pre_loop(self, code_gen, context_stack) -> bool:
        if self._loop_type.is_unbounded():
            return True

        if (self._loop_type is _LoopType.COUNTED
                and not self.rvalue(LoopVar.COUNTER)):
            return False
        if self._loop_type in (_LoopType.ALL, _LoopType.LIST):
            code_gen.add_instruction(OpCode.MOVEQ, 0, LoopVar.COUNTER)
            if not (self._pre_loop_list(code_gen, context_stack) and
                    self._pre_loop_as(context_stack)):
                return False
        elif self._loop_type in (_LoopType.GROUPS, _LoopType.LOCATIONS):
            code_gen.add_instruction(OpCode.MOVEQ, 0, LoopVar.COUNTER)
            if not (self._push_set_names(code_gen) and
                    self._pre_loop_as(context_stack)):
                return False

        if self.current_token.is_a(TokenTypes.WITH):
            self.next_token()
            return self._pre_loop_with(code_gen, context_stack)
        return True

    def _pre_loop_list(self, code_gen, context_stack) -> bool:
        """ Push everything from the "in" clause onto the stack. """
        if self.current_token.is_a(TokenTypes.AS):
            return True
        inner_coder = CodeGen()
        operand = {
            TokenTypes.ALL: Operand.LIGHT,
            TokenTypes.GROUP: Operand.GROUP,
            TokenTypes.LOCATION: Operand.LOCATION
        }.get(self.current_token.token_type)
        if operand is not None:
            # Push all lights, or all members of a group/location.
            self.next_token()
            if not self._push_light_names(inner_coder, operand):
                return False
        else:
            # Push and count one light.
            if not self.rvalue(Register.RESULT, inner_coder):
               return False
            inner_coder.push(Register.RESULT)
            inner_coder.plus_equals(LoopVar.COUNTER)

        if self.current_token.is_a(TokenTypes.AND):
            if operand == Operand.ALL:
                return self.trigger_error('"and" is not allowed with "all"')
            if not (self._pre_loop_and() and
                    self._pre_loop_list(code_gen, context_stack)):
                return False

        code_gen.add_instructions(inner_coder.program)
        return True

    def _push_light_names(self, code_gen, operand) -> bool:
        inner_code = CodeGen()
        inner_code.plus_equals(LoopVar.COUNTER)
        inner_code.push(LoopVar.CURRENT)
        if self._loop_type is _LoopType.LIST:
            if not self.rvalue(LoopVar.FIRST, code_gen):
                return self.token_error(
                    'Needed name of a group or location, got "{}"')
            code_gen.iter_members(operand, inner_code.program)
        else:
            code_gen.iter_lights(inner_code.program)
        return True

    def _push_set_names(self, code_gen) -> bool:
        """Generate code to push all group or location names onto the stack. """
        inner_code = CodeGen()
        inner_code.plus_equals(LoopVar.COUNTER)
        inner_code.push(LoopVar.CURRENT)
        if self._loop_type is _LoopType.GROUPS:
            operand = Operand.GROUP
        else:
            operand = Operand.LOCATION
        code_gen.iter_sets(operand, inner_code.program)
        return True

    def _pre_loop_with(self, code_gen, context_stack) -> bool:
        if not self._init_index_var(context_stack):
            return False
        if self.current_token.is_a(TokenTypes.IN):
            code_gen.add_instruction(OpCode.MOVEQ, 0, LoopVar.COUNTER)
            self._loop_type = _LoopType.LIST
            self.next_token()
            return self._pre_loop_list(code_gen, context_stack)
        if self.current_token.is_a(TokenTypes.FROM):
            self.next_token()
            if not self._index_var_range(code_gen):
                return False
        elif self.current_token.is_a(TokenTypes.CYCLE):
            self.next_token()
            if not self._cycle_var_range(code_gen):
                return False
        else:
            return self.token_error(
                'Needed "from" or "cycle", got "{}"')
        return True

    def _pre_loop_and(self) -> bool:
        self.next_token()
        if (self.current_token.token_type not in
            (TokenTypes.GROUP, TokenTypes.LOCATION)
                and not self.at_rvalue()):
            return self.token_error('Needed lights after "and", got "{}".')
        return True

    def _pre_loop_as(self, context_stack) -> bool:
        if not self.current_token.is_a(TokenTypes.AS):
            return self.token_error('Expected "as", got "{}"')
        self.next_token()
        if not self.current_token.is_a(TokenTypes.NAME):
            return self.token_error('Expected name for lights, got "{}"')
        self._light_var = str(self.current_token)
        context_stack.add_variable(self._light_var)
        return self.next_token()

    def _init_index_var(self, context_stack) -> bool:
        if not self.current_token.is_a(TokenTypes.NAME):
            return self.token_error('Not a variable name: "{}"')
        self._index_var = str(self.current_token)
        context_stack.add_variable(self._index_var)
        return self.next_token()

    def _index_var_range(self, code_gen) -> bool:
        if not self.rvalue(LoopVar.FIRST):
            return False
        if not self.current_token.is_a(TokenTypes.TO):
            return self.token_error('Needed "to", got "{}"')
        self.next_token()
        if not self.rvalue(LoopVar.LAST):
            return False
        code_gen.add_instruction(OpCode.MOVE, LoopVar.FIRST, self._index_var)
        if self._loop_type is _LoopType.WITH:
            if not self._calc_counter(code_gen):
                return False
        else:
            if not self._calc_incr(code_gen):
                return False
        return True

    @staticmethod
    def _calc_counter(code_gen) -> bool:
        # abs(last - first) + 1
        code_gen.subtract(LoopVar.LAST, LoopVar.FIRST)
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

    @staticmethod
    def _calc_incr(code_gen) -> bool:
        # increment = (last - first) / (count - 1)
        # If count == 1, increment = 0.
        code_gen.test_op(Operator.NOTEQ, LoopVar.COUNTER, 1)
        marker = code_gen.if_true_start()
        code_gen.subtract(LoopVar.LAST, LoopVar.FIRST)
        code_gen.subtract(LoopVar.COUNTER, 1)
        code_gen.add_list(
            (OpCode.OP, Operator.DIV),
            (OpCode.POP, LoopVar.INCR)
        )
        code_gen.if_else(marker)
        code_gen.add_instruction(OpCode.MOVEQ, 0, LoopVar.INCR)
        code_gen.if_end(marker)
        return True

    def _cycle_var_range(self, code_gen):
        if self._loop_type == (_LoopType.WITH):
            return self.trigger_error(
                "repeat with cycle missing number of iterations")
        if not self.at_rvalue():
            code_gen.add_instruction(OpCode.MOVEQ, 0, LoopVar.FIRST)
        elif not self.rvalue(LoopVar.FIRST):
            return False

        # increment = 360 / counter, or
        # increment = 65536 / counter, based on unit_mode register
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
        '''
        Generate code to leave True or False in the result register,
        depending on whether the loop should continue.
        '''
        if self._loop_type is _LoopType.INFINITE:
            code_gen.add_instruction(OpCode.MOVEQ, True, Register.RESULT)
            return True
        if self._loop_type is _LoopType.WHILE:
            return self.rvalue()
        else:
            code_gen.test_op(Operator.GT, LoopVar.COUNTER, 0)
        return True

    def _loop_body(self, code_gen) -> bool:
        if self._loop_type.is_iter():
            code_gen.add_instruction(OpCode.POP, self._light_var)
        return self.parser.command_seq()

    def _loop_post(self, code_gen) -> bool:
        if self._loop_type in (_LoopType.INFINITE, _LoopType.WHILE):
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
        }.get(self.current_token.token_type)
