from collections import deque
from typing import Generator
from bardolph.parser.code_gen import CodeGen
from bardolph.parser.sub_parser import SubParser
from bardolph.parser.token import TokenTypes
from bardolph.vm.vm_codes import LoopVar, OpCode, Operand, Operator, Register


class _CodeStack:
    def __init__(self):
        self._stack = deque()

    def push(self, code_gen: CodeGen) -> None:
        self._stack.append(code_gen)

    def flush(self) -> Generator[CodeGen, None, None]:
        while len(self._stack) > 0:
            yield self._stack.pop()


class LightListParser(SubParser):
    """
    Examples:

    repeat all

    repeat location

    repeat group

    repeat in
        group group_name and
        location location_name and
        light_name and light_name

        All of these are optional and repeatable, and the order is
        insignificant.

    repeat all, repeat location, and repeat group are mutually exclusive and may
    not be combined with repeat in.

    The generated code pushes individual light names onto the stack. Groups and
    locations are expanded at runtime and the name of each member is pushed onto
    the stack. The expansion occurs before the loop starts. No effort is made to
    eliminate duplicate names.

    When the generated code finishes running, all of the light names will be on
    the stack and the number of lights will have been added to LoopVar.COUNT.
    """
    def __init__(self, parser):
        super().__init__(parser)

    def all_lights(self) -> bool:
        """
        Generate code to push all lights onto the stack in reverse order. Each
        time a light is pushed, increment LoopVar.COUNTER by 1.
        """
        code_gen = self.code_gen
        code_gen.add_list(
            (OpCode.MOVEQ, Operand.LIGHT, Register.OPERAND),
            OpCode.DISC
        )
        loop_marker = code_gen.mark()
        code_gen.pop(LoopVar.CURRENT)
        code_gen.test_op(Operator.NOTEQ, LoopVar.CURRENT, Operand.NULL)
        if_marker = code_gen.start_if_true()
        code_gen.push(LoopVar.CURRENT)
        code_gen.plus_equals(LoopVar.COUNTER)
        code_gen.add_list(
            (OpCode.MOVEQ, Operand.LIGHT, Register.OPERAND),
            (OpCode.DNEXT, LoopVar.CURRENT)
        )
        code_gen.jump_back(loop_marker)
        code_gen.end_if(if_marker)

        return self.next_token()

    def all_groups(self) -> bool:
        self._push_set_names(Operand.GROUP, self.code_gen)
        return self.next_token()

    def all_locations(self) -> bool:
        self._push_set_names(Operand.LOCATION, self.code_gen)
        return self.next_token()

    def light_list(
            self, code_stack: _CodeStack = None, top_call: bool = True) -> bool:
        if code_stack is None:
            code_stack = _CodeStack()
        code_gen = CodeGen()
        match self.current_token.token_type:
            case TokenTypes.GROUP:
                self.next_token()
                if not self.rvalue_str(code_gen):
                    return self.token_error('Needed a group, got "{}"')
                self._push_member_names(Operand.GROUP, code_gen)
                code_stack.push(code_gen)
            case TokenTypes.LOCATION:
                self.next_token()
                if not self.rvalue_str(code_gen):
                    return self.token_error('Needed a location, got "{}"')
                self._push_member_names(Operand.LOCATION, code_gen)
                code_stack.push(code_gen)
            case TokenTypes.LITERAL_STRING:
                code_gen.pushq(self.current_token.content)
                code_gen.plus_equals(LoopVar.COUNTER)
                code_stack.push(code_gen)
                self.next_token()
            case TokenTypes.NAME:
                if not self.rvalue_str(code_gen):
                    return False
                code_gen.plus_equals(LoopVar.COUNTER)
                code_stack.push(code_gen)
            case _:
                return self.token_error('"{}" is not allowed in this list.')

        # Limit to one level of recursion.
        if top_call:
            while self.current_token.is_a(TokenTypes.AND):
                self.next_token()
                if not self.light_list(code_stack, False):
                    return False
            for code_gen in code_stack.flush():
                self.code_gen.merge(code_gen)

        return True

    def _push_member_names(self, operand, code_gen: CodeGen) -> None:
        """
        Generate code to push all members of a group or location onto the
        stack. They are pushed in reverse order so that they will be in the
        correct order when popped off. Each time a name is pushed, increment
        LoopVar.COUNTER by 1.
        """
        code_gen.pop(LoopVar.NAME_FIRST)
        code_gen.add_list(
            (OpCode.MOVEQ, operand, Register.OPERAND),
            (OpCode.DISCM, LoopVar.NAME_FIRST)
        )
        loop_marker = code_gen.mark()
        code_gen.pop(LoopVar.CURRENT)
        code_gen.test_op(Operator.NOTEQ, LoopVar.CURRENT, Operand.NULL)
        if_marker = code_gen.start_if_true()
        code_gen.push(LoopVar.CURRENT)
        code_gen.plus_equals(LoopVar.COUNTER)
        code_gen.add_list(
            (OpCode.MOVEQ, operand, Register.OPERAND),
            (OpCode.DNEXTM, LoopVar.NAME_FIRST, LoopVar.CURRENT)
        )
        code_gen.jump_back(loop_marker)
        code_gen.end_if(if_marker)

    def _push_set_names(self, operand, code_gen: CodeGen) -> None:
        """
        Generate code to push all group or location names onto the stack. They
        are pushed in reverse alphabetical order so that they will be in the
        correct order when popped off. Each time a name is pushed, increment
        LoopVar.COUNTER by 1.
        """
        code_gen = self.code_gen
        code_gen.add_list(
            (OpCode.MOVEQ, operand, Register.OPERAND),
            OpCode.DISC
        )
        loop_marker = code_gen.mark()
        code_gen.pop(LoopVar.CURRENT)
        code_gen.test_op(Operator.NOTEQ, LoopVar.CURRENT, Operand.NULL)
        if_marker = code_gen.start_if_true()
        code_gen.push(LoopVar.CURRENT)
        code_gen.plus_equals(LoopVar.COUNTER)
        code_gen.add_list(
            (OpCode.MOVEQ, operand, Register.OPERAND),
            (OpCode.DNEXT, LoopVar.CURRENT)
        )
        code_gen.jump_back(loop_marker)
        code_gen.end_if(if_marker)
