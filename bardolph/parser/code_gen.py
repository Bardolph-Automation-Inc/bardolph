from bardolph.controller.units import UnitMode
from bardolph.vm.instruction import Instruction
from bardolph.vm.vm_codes import JumpCondition, LoopVar, OpCode, Operand
from bardolph.vm.vm_codes import Operator, Register

class _JumpMarker:
    def __init__(self, inst, offset):
        self.jump = inst
        self.offset = offset


class CodeGen:
    def __init__(self):
        self._code = []

    @property
    def program(self):
        return self._code

    @property
    def current_offset(self) -> int:
        return len(self._code)

    def clear(self) -> None:
        self._code.clear()

    def push(self, operand) -> None:
        self.add_instruction(self._push_op(operand), operand)

    def pop(self, operand) -> None:
        self.add_instruction(OpCode.POP, operand)

    def add_instruction(self, op_code, param0=None, param1=None) -> Instruction:
        inst = Instruction(op_code, param0, param1)
        self._code.append(inst)
        return inst

    def add_list(self, *inst_list) -> None:
        # Convert a list of tuples to Instructions.
        for code in inst_list:
            if isinstance(code, OpCode):
                self.add_instruction(code)
            else:
                op_code, param0, param1, *_ = (*code, None, None)
                self.add_instruction(op_code, param0, param1)

    def add_instructions(self, inst_list) -> None:
        self._code.extend(inst_list)

    def add(self, addend0, addend1) -> None:
        self.binop(Operator.ADD, addend0, addend1)

    def subtract(self, minuend, subtrahend) -> None:
        """
        minuend - subtrahend
        Leaves the difference on top of the stack.
        """
        self.binop(Operator.SUB, minuend, subtrahend)

    def test_op(self, operator, op0, op1) -> None:
        """
        Generate code to perform a binary operation and put the results into
        the result register.
        """
        self.binop(operator, op0, op1)
        self.add_instruction(OpCode.POP, Register.RESULT)

    def binop(self, operator, param0, param1) -> None:
        push0 = self._push_op(param0)
        push1 = self._push_op(param1)
        self.add_list(
            (push0, param0),
            (push1, param1),
            (OpCode.OP, operator)
        )

    def plus_equals(self, dest, delta=1) -> None:
        self._op_equals(Operator.ADD, dest, delta)

    def minus_equals(self, dest, delta=1) -> None:
        self._op_equals(Operator.SUB, dest, delta)

    def times_equals(self, dest, pi) -> None:
        self._op_equals(Operator.MUL, dest, pi)

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

    def if_true_start(self) -> _JumpMarker:
        inst = self.add_instruction(OpCode.JUMP, JumpCondition.IF_FALSE)
        return _JumpMarker(inst, self.current_offset)

    def if_else(self, marker) -> None:
        marker.jump.param1 = self.current_offset - marker.offset + 2
        inst = self.add_instruction(OpCode.JUMP, JumpCondition.ALWAYS)
        marker.jump = inst
        marker.offset = self.current_offset

    def if_end(self, marker) -> None:
        marker.jump.param1 = self.current_offset - marker.offset + 1

    def iter_lights(self, code) -> None:
        """ Generate code to iterate over all of the lights.
            moveq  operand.light   register.operand
            disc
        mark marker
            move register.result loopvar.current
            test operator.noteq loopvar.current operand.null
            if start
               ...insert code...
               moveq operand.light register.operand
               dnext loopvar.current
               jump mark
            if end
        """
        self.add_list(
            (OpCode.MOVEQ, Operand.LIGHT, Register.OPERAND),
            OpCode.DISC
        )
        loop_marker = self.mark()
        self.add_instruction(OpCode.MOVE, Register.RESULT, LoopVar.CURRENT)
        self.test_op(Operator.NOTEQ, LoopVar.CURRENT, Operand.NULL)
        if_marker = self.if_true_start()
        self._code.extend(list(code))
        self.add_list(
            (OpCode.MOVEQ, Operand.LIGHT, Register.OPERAND),
            (OpCode.DNEXT, LoopVar.CURRENT)
        )
        self.jump_back(loop_marker)
        self.if_end(if_marker)

    def iter_sets(self, operand, code) -> None:
        """ Iterate over all groups or locations. """
        self.add_instruction(OpCode.MOVEQ, operand, Register.OPERAND)
        self.add_instruction(OpCode.DISC)
        loop_marker = self.mark()
        self.add_instruction(OpCode.MOVE, Register.RESULT, LoopVar.CURRENT)
        self.test_op(Operator.NOTEQ, Register.RESULT, Operand.NULL)
        if_marker = self.if_true_start()
        self._code.extend(list(code))
        self.add_list(
            (OpCode.MOVEQ, operand, Register.OPERAND),
            (OpCode.DNEXT, LoopVar.CURRENT)
        )
        self.jump_back(loop_marker)
        self.if_end(if_marker)

    def iter_members(self, operand, code):
        """
        Generate code to iterate over all members of a group or location. The
        name must be in LoopVar.FIRST.
        """
        self.add_list(
            (OpCode.MOVEQ, operand, Register.OPERAND),
            (OpCode.DISCM, LoopVar.FIRST)
        )
        loop_marker = self.mark()
        self.add_instruction(OpCode.MOVE, Register.RESULT, LoopVar.CURRENT)
        self.test_op(Operator.NOTEQ, LoopVar.CURRENT, Operand.NULL)
        if_marker = self.if_true_start()
        self._code.extend(list(code))
        self.add_list(
            (OpCode.MOVEQ, operand, Register.OPERAND),
            (OpCode.DNEXTM, LoopVar.FIRST, LoopVar.CURRENT)
        )
        self.jump_back(loop_marker)
        self.if_end(if_marker)

    @staticmethod
    def _push_op(oper) -> OpCode:
        if isinstance(oper, (int, float, UnitMode)):
            return OpCode.PUSHQ
        return OpCode.PUSH
