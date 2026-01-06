from bardolph.controller.units import UnitMode
from bardolph.vm.instruction import Instruction
from bardolph.vm.vm_codes import JumpCondition, OpCode
from bardolph.vm.vm_codes import Operator

class _JumpMarker:
    def __init__(self, inst, offset):
        self.jump = inst
        self.offset = offset


class CodeGen:
    def __init__(self):
        self._code = []

    @property
    def program(self) -> list:
        return self._code

    @property
    def current_offset(self) -> int:
        return len(self._code)

    def clear(self) -> None:
        self._code.clear()

    def push(self, operand) -> None:
        self.add_instruction(self._push_op(operand), operand)

    def pushq(self, operand) -> None:
        self.add_instruction(OpCode.PUSHQ, operand)

    def pop(self, operand=None) -> None:
        # The operand is where to put the value. If None, throw the value away.
        self.add_instruction(OpCode.POP, operand)

    def add_instruction(self, op_code, param0=None, param1=None) -> Instruction:
        inst = Instruction(op_code, param0, param1)
        self._code.append(inst)
        return inst

    def add_list(self, *inst_list) -> None:
        #  Convert a list of tuples and/or OpCodes to Instructions.
        for code in inst_list:
            if isinstance(code, OpCode):
                self.add_instruction(code)
            else:
                op_code, param0, param1, *_ = (*code, None, None)
                self.add_instruction(op_code, param0, param1)

    def add(self, addend0, addend1) -> None:
        self.binop(Operator.ADD, addend0, addend1)

    def add_instructions(self, inst_list) -> None:
        self._code.extend(inst_list)

    def merge(self, other) -> None:
        self._code.extend(other._code)

    def wait(self) -> None:
        self.add_instruction(OpCode.WAIT)

    def subtract(self, minuend, subtrahend) -> None:
        """
        Calculate minuend - subtrahend and leave the difference on top of the
        stack. No stored values are changed.
        """
        self.binop(Operator.SUB, minuend, subtrahend)

    def test_op(self, operator, op0, op1) -> None:
        self.binop(operator, op0, op1)

    def binop(self, operator, param0, param1) -> None:
        """
        Generate code to perform a binary operation and put the results on top
        of the expression stack.
        """
        push0 = self._push_op(param0)
        push1 = self._push_op(param1)
        self.add_list(
            (push0, param0),
            (push1, param1),
            (OpCode.OP, operator)
        )

    def plus_equals(self, dest, delta=1) -> None:
        """
        Add delta to dest and save it. Nothing is left on the stack.
        """
        self._op_equals(Operator.ADD, dest, delta)

    def minus_equals(self, dest, delta=1) -> None:
        """
        Subtract delta from dest and save it. Nothing is left on the stack.
        """
        self._op_equals(Operator.SUB, dest, delta)

    def times_equals(self, dest, multiiplier) -> None:
        """
        Multiply dest by multiplier and save it. Nothing is left on the stack.
        """
        self._op_equals(Operator.MUL, dest, multiiplier)

    def _op_equals(self, operator, original, change) -> None:
        push0 = self._push_op(original)
        push1 = self._push_op(change)
        self.add_list(
            (push0, original),
            (push1, change),
            (OpCode.OP, operator),
            (OpCode.POP, original)
        )

    def push_context(self, params) -> None:
        self.add_instruction(OpCode.JSR, params)

    def mark(self) -> _JumpMarker:
        return _JumpMarker(None, self.current_offset)

    def jump_back(self, marker) -> None:
        offset = marker.offset - self.current_offset
        self.add_instruction(OpCode.JUMP, JumpCondition.ALWAYS, offset)

    def start_if_true(self) -> _JumpMarker:
        inst = self.add_instruction(OpCode.JUMP, JumpCondition.IF_FALSE)
        return _JumpMarker(inst, self.current_offset)

    def start_else(self, marker) -> None:
        marker.jump.param1 = self.current_offset - marker.offset + 2
        inst = self.add_instruction(OpCode.JUMP, JumpCondition.ALWAYS)
        marker.jump = inst
        marker.offset = self.current_offset

    def end_if(self, marker) -> None:
        marker.jump.param1 = self.current_offset - marker.offset + 1

    @staticmethod
    def _push_op(oper) -> OpCode:
        if isinstance(oper, (int, float, UnitMode)):
            return OpCode.PUSHQ
        return OpCode.PUSH
