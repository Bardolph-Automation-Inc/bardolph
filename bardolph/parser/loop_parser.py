from enum import Enum, auto

from bardolph.controller.units import UnitMode
from bardolph.lib.symbol import SymbolType
from bardolph.parser.expr_parser import ExpressionParser
from bardolph.parser.light_list_parser import LightListParser
from bardolph.parser.sub_parser import SubParser
from bardolph.parser.token import TokenTypes
from bardolph.vm.vm_codes import LoopVar, OpCode, Operand, Operator, Register


class LoopType(Enum):
    ALL = auto()
    ARRAY = auto()
    COUNTED = auto()
    GROUPS = auto()
    INFINITE = auto()
    IN_ARRAY = auto()
    IN_LIST = auto()
    LOCATIONS = auto()
    WHILE = auto()
    WITH_RANGE = auto()

    def has_qualifier(self):
        # Has a qualifying keyword, i.e. "repeat in, repeat while".
        return self in (self.IN_LIST, self.WHILE)

    def has_name_list(self):
        # Pushes a list of names on the stack and sets the iteration variable.
        return self in (self.ALL, self.GROUPS, self.IN_LIST, self.LOCATIONS)


class LoopParser(SubParser):
    """
    Examples:
        repeat 5 with x from 10 to 20
        repeat 5 with x cycle
        repeat all as the_light with x from 10 to 20
        repeat all as the_light with x cycle
        repeat in light1, light2, group1, location1
            as the_light
            with x from 10 to 20
        repeat in light1, light2, group1, location1
            as the_light
            with x cycle

        repeat location as the_location
        repeat group as the_group

        repeat with x from 10 to 20
        repeat with x cycle

    In all of these examples, x is called the "index variable" (_index_var). In
    the examples where the_light appears, it is called the "iteration
    variable", and its name is saved in name in _iter_var_.

    In counted non-array cases, the number of iterations is controlled by
    LoopVar.COUNTER, and the loop keeps going as long as COUNTER > 0. In the
    array case, the number of iterations is kept in LoopVar.COUNT_LAST and the
    iteration keeps going as long as LoopVar.COUNTER < LoopVar.COUNT_LAST.
    """
    def __init__(self, parser):
        super().__init__(parser)
        self._loop_type = None
        self._index_var = None
        self._iter_var_name = None
        self._counter_var = None

    def repeat(self) -> bool:
        code_gen = self.code_gen
        context = self.context

        context.enter_loop()
        code_gen.add_instruction(OpCode.LOOP)
        self.next_token()
        self._detect_loop_type()
        if self._loop_type is not LoopType.WHILE and not self._init_loop():
            return False
        loop_top = code_gen.mark()
        if not self._loop_test():
            return False
        exit_loop_marker = code_gen.start_if_true()
        if not (self._loop_body() and self._loop_post()):
            return False
        code_gen.jump_back(loop_top)
        code_gen.end_if(exit_loop_marker)
        context.fix_break_addrs(self.code_gen)
        code_gen.add_instruction(OpCode.END_LOOP)
        context.exit_loop()
        return True

    _loop_type_map = {
        TokenTypes.ALL: LoopType.ALL,
        TokenTypes.GROUP: LoopType.GROUPS,
        TokenTypes.IN: LoopType.IN_LIST,
        TokenTypes.WITH: LoopType.WITH_RANGE,
        TokenTypes.LOCATION: LoopType.LOCATIONS,
        TokenTypes.WHILE: LoopType.WHILE
    }

    def _detect_loop_type(self) -> None:
        self._loop_type = self._loop_type_map.get(self.current_token.token_type)
        if self._loop_type is None:
            if self.at_rvalue():
                self._loop_type = LoopType.COUNTED
            else:
                self._loop_type = LoopType.INFINITE

    def _at_array(self) -> bool:
        return (self.current_token.is_a(TokenTypes.NAME) and
                self.context.has_symbol_typed(
            self.current_token.content, SymbolType.ARRAY))

    def _count_max(self) -> LoopVar:
        if self._loop_type is LoopType.ARRAY:
            return LoopVar.COUNT_LAST
        return LoopVar.COUNTER

    def _init_loop(self) -> bool:
        match self._loop_type:
            case LoopType.COUNTED:
                if not self.rvalue():
                    return False
                self.code_gen.pop(LoopVar.COUNTER)
            case LoopType.ALL:
                if not self._push_names(LightListParser.all_lights):
                    return False
            case LoopType.IN_LIST:
                self.next_token()
                if self._at_array():
                    if not self._count_from_array():
                        return False
                elif not self._push_names(LightListParser.light_list):
                    return False
            case LoopType.GROUPS:
                if not self._push_names(LightListParser.all_groups):
                    return False
            case LoopType.LOCATIONS:
                if not self._push_names(LightListParser.all_locations):
                    return False
            case LoopType.WITH_RANGE:
                # Example: repeat with i from a to b. Return immediately.
                self.next_token()
                return self._with_range()

        # Example: repeat 5 with i from a to b. If a count wasn't given, "with"
        # has already been processed in the code above.
        #
        if self.current_token.is_a(TokenTypes.WITH):
            self.next_token()
            return self._with_index()

        self._index_var = None
        return True

    def _count_from_array(self) -> bool:
        self._loop_type = LoopType.ARRAY
        code_gen = self.code_gen
        code_gen.push(self.current_token.content)
        self.next_token()
        if self.current_token.is_a(TokenTypes.BRACKET_PAIR):
            self.next_token()
        elif self.current_token == '[':
            ExpressionParser(self.parser).resolve_array()
        code_gen.add_instruction(OpCode.OP, Operator.SIZE)
        code_gen.pop(LoopVar.COUNT_LAST)
        return self._add_iter_var()

    def _push_names(self, fn) -> bool:
        """
        Push the names in a list onto the stack and keep count. When the
        generated code is done, LoopoVar.COUNTER will contain the number of
        iterations.

        fn contains a function that will generate VM code to go throush a set
        of light names, pushing each one onto the stack. That code also
        increments LoopVar.COUNTER each time a name gets pushed.
        """
        self.code_gen.add_instruction(OpCode.MOVEQ, 0, LoopVar.COUNTER)
        if not fn(LightListParser(self.parser)):
            return False
        return self._add_iter_var()

    def _add_iter_var(self) -> bool:
        if not self.current_token.is_a(TokenTypes.AS):
            return self.token_error('Expected "as", got "{}"')
        self.next_token()
        if not self.current_token.is_a(TokenTypes.NAME):
            return self.token_error('Expected variable name, got "{}"')
        self._iter_var_name = self.current_token.content
        self.context.add_variable(self._iter_var_name)
        if self._loop_type is LoopType.ARRAY:
            self.code_gen.add_instruction(OpCode.MOVEQ, 0, self._iter_var_name)
        return self.next_token()

    def _with_index(self) -> bool:
        """
        Uses "with" to supply values for the index var. Don't do anything to
        calculate the number of iterations, which is controlled by an explicit
        count or a light list. That count will be in LoopVar.COUNTER.
        """
        if not self._init_index_var():
            return False
        if self.current_token.token_type is TokenTypes.FROM:
            self.next_token()
            if not self._index_var_range():
                return False
            return self._index_var_range_incr()
        if self.current_token.token_type is TokenTypes.CYCLE:
            self.next_token()
            return self._cycle_incr()
        return self.token_error('Needed "from" or "cycle", got "{}"')

    def _init_index_var(self) -> bool:
        if not self.current_token.is_a(TokenTypes.NAME):
            return self.token_error('Not a variable name: "{}"')
        self._index_var = self.current_token.content
        self.context.add_variable(self._index_var)
        return self.next_token()

    def _index_var_range(self) -> bool:
        """
        Example: ... from 10 to 20
        Populate LoopVar.RANGE_FIRST and LoopVar.RANGE_LAST.
        """
        if not self.rvalue():
            return False
        code_gen = self.code_gen
        code_gen.pop(LoopVar.RANGE_FIRST)
        code_gen.add_instruction(
            OpCode.MOVE, LoopVar.RANGE_FIRST, self._index_var)
        if not self.current_token.is_a(TokenTypes.TO):
            return self.token_error('Needed "to", got "{}"')
        self.next_token()
        if not self.rvalue():
            return False
        code_gen.pop(LoopVar.RANGE_LAST)
        return True

    def _index_var_range_incr(self) -> bool:
        """
        Calculate the increment based on LoopVar.COUNTER, LoopVar.RANGE_FIRST,
        and LoopVar.RANGE_LAST. Put the result into LoopVar.INCREMENT.

        If count == 1, increment = 0.
        Otherwise, increment = (last - first) / (count - 1)
        """
        code_gen = self.code_gen

        # if the number of iterations is 1, set the increment to 0
        #
        code_gen.test_op(Operator.EQ, LoopVar.COUNTER, 1)
        marker = code_gen.start_if_true()
        code_gen.add_instruction(OpCode.MOVEQ, 0, LoopVar.INCREMENT)

        # else calculate the increment
        #
        code_gen.start_else(marker)
        if self._loop_type is LoopType.ARRAY:
            code_gen.subtract(LoopVar.RANGE_FIRST, LoopVar.RANGE_LAST)
        else:
            code_gen.subtract(LoopVar.RANGE_LAST, LoopVar.RANGE_FIRST)
        code_gen.subtract(self._count_max(), 1)
        code_gen.add_list(
            (OpCode.OP, Operator.DIV),
            (OpCode.POP, LoopVar.INCREMENT)
        )

        # end if
        #
        code_gen.end_if(marker)
        return True

    def _cycle_incr(self) -> bool:
        """
        Calculate the value for LoopVar.INCREMENT in a loop that uses "cycle".

        If an initial value is supplied, put it into LoopVar.RANGE_FIRST.
        Otherwise, set LoopVar.RANGE_FIRST to 0.

        increment = 360 / counter or
        increment = 65536 / counter,
        based on unit_mode register
        """
        code_gen = self.code_gen
        if not self.at_rvalue():
            code_gen.add_instruction(OpCode.MOVEQ, 0, LoopVar.RANGE_FIRST)
        else:
            if not self.rvalue():
                return False
            code_gen.pop(LoopVar.RANGE_FIRST)

        code_gen.add_instruction(
            OpCode.MOVE, LoopVar.RANGE_FIRST, self._index_var)
        code_gen.test_op(Operator.EQ, Register.UNIT_MODE, UnitMode.RAW)
        marker = code_gen.start_if_true()
        code_gen.push(65536)
        code_gen.start_else(marker)
        code_gen.push(360)
        code_gen.end_if(marker)
        code_gen.push(self._count_max())
        code_gen.add_instruction(OpCode.OP, Operator.DIV)
        code_gen.add_instruction(OpCode.POP, LoopVar.INCREMENT)
        return True

    def _with_range(self) -> bool:
        """
        Example: repeat with x from 10 to 20

        Parse everything after "with".

        In the case of "from", Calculate the number of iterations and the range
        of values. The increment is either 1 or -1, depending on the range.
        """
        if not self._init_index_var():
            return False
        if self.current_token.token_type is not TokenTypes.FROM:
            return self.token_error('Needed "from", got "{}"')

        self.next_token()
        if not self._index_var_range():
            return False
        self._counter_from_range()
        return True

    def _counter_from_range(self) -> None:
        """
        Set LoopVar.COUNTER to the number of iterations, which is
        abs(last - first) + 1

        This is used only in cases where there's just a "with" and no other code
        to control the number of iterations. For example:
            repeat with a from 5 to 10
        """
        code_gen = self.code_gen
        code_gen.subtract(LoopVar.RANGE_LAST, LoopVar.RANGE_FIRST)
        code_gen.pop(LoopVar.COUNTER)
        code_gen.test_op(Operator.LT, LoopVar.COUNTER, 0)
        marker = code_gen.start_if_true()
        code_gen.times_equals(LoopVar.COUNTER, -1)
        self.code_gen.add_instruction(
            OpCode.MOVEQ, -1, LoopVar.INCREMENT)
        code_gen.start_else(marker)
        self.code_gen.add_instruction(
            OpCode.MOVEQ, 1, LoopVar.INCREMENT)
        code_gen.end_if(marker)
        code_gen.plus_equals(LoopVar.COUNTER)

    def _loop_test(self) -> bool:
        """
        Generate code to leave True on top of the eval stack if the loop should
        continue, or False if it should exit. In the case of a "while", the
        value at the top of the stack is coerced with bool().
        """
        match self._loop_type:
            case LoopType.INFINITE:
                self.code_gen.add_instruction(OpCode.PUSHQ, True)
            case LoopType.WHILE:
                self.next_token()
                return self.rvalue()
            case LoopType.ARRAY:
                self.code_gen.test_op(
                    Operator.LT, self._iter_var_name, LoopVar.COUNT_LAST)
            case _:
                self.code_gen.test_op(Operator.GT, LoopVar.COUNTER, 0)
        return True

    def _loop_body(self) -> bool:
        if self._loop_type.has_name_list():
            self.code_gen.add_instruction(OpCode.POP, self._iter_var_name)
        return self.parser.command_seq()

    def _loop_post(self) -> bool:
        if self._loop_type is LoopType.ARRAY:
            self.code_gen.plus_equals(self._iter_var_name, 1)
        elif self._loop_type not in (LoopType.INFINITE, LoopType.WHILE):
            self.code_gen.minus_equals(LoopVar.COUNTER, 1)

        if self._index_var is not None:
            self.code_gen.plus_equals(self._index_var, LoopVar.INCREMENT)

        return True

    @property
    def _current_operand_token(self) -> Operand | None:
        return {
            TokenTypes.GROUP: Operand.GROUP,
            TokenTypes.LOCATION: Operand.LOCATION
        }.get(self.current_token.token_type)
