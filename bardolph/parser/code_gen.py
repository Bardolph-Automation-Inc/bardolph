from bardolph.controller.units import UnitMode
from bardolph.vm.instruction import Instruction
from bardolph.vm.vm_codes import JumpCondition, LoopVar, OpCode, Operand
from bardolph.vm.vm_codes import Operator, Register

class _JumpMarker:
    def __init__(self, inst, offset):
        self.jump = inst
        self.offset = offset
        self.has_else = False

class CodeGen:
    def __init__(self):
        self._code = []

    @property
    def program(self) -> []:
        return self._code

    @property
    def current_offset(self) -> int:
        return len(self._code)

    def clear(self) -> None:
        self._code.clear()

    def push(self, operand) -> None:
        self.add_instruction(CodeGen._push_op(operand), operand)

    def pop(self, operand) -> None:
        self.add_instruction(OpCode.POP, operand)

    def add_instruction(self, op_code, param0=None, param1=None) -> Instruction:
        inst = Instruction(op_code, param0, param1)
        self._code.append(inst)
        return inst

    def add_list(self, inst_list) -> None:
        # Convert a list of tuples to Instructions.
        for code in inst_list:
            if isinstance(code, OpCode):
                self.add_instruction(code)
            else:
                op_code = code[0]
                param0 = code[1] if len(code) > 1 else None
                param1 = code[2] if len(code) > 2 else None
                self.add_instruction(op_code, param0, param1)

    def add_instructions(self, inst_list) -> None:
        self._code.extend(inst_list)

    def addition(self, addend0, addend1) -> None:
        self.binop(Operator.ADD, addend0, addend1)

    def subtraction(self, minuend, subtrahend) -> None:
        # minuend - subtrahend
        # Leaves the difference on top of the stack.
        self.binop(Operator.SUB, minuend, subtrahend)

    def test_op(self, operator, op0, op1) -> None:
        """Generate code to perform a binary operation and put the results into
        the result register."""
        self.binop(operator, op0, op1)
        self.add_instruction(OpCode.POP, Register.RESULT)

    def binop(self, operator, param0, param1) -> None:
        push0 = CodeGen._push_op(param0)
        push1 = CodeGen._push_op(param1)
        self.add_list([
            (push0, param0),
            (push1, param1),
            (OpCode.OP, operator)
        ])

    def plus_equals(self, dest, delta=1) -> None:
        self._op_equals(Operator.ADD, dest, delta)

    def minus_equals(self, dest, delta=1) -> None:
        self._op_equals(Operator.SUB, dest, delta)

    def times_equals(self, dest, pi) -> None:
        self._op_equals(Operator.MUL, dest, pi)

    def _op_equals(self, operator, original, change) -> None:
        push0 = CodeGen._push_op(original)
        push1 = CodeGen._push_op(change)
        self.add_list([
            (push0, original),
            (push1, change),
            (OpCode.OP, operator),
            (OpCode.POP, original)
        ])

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
        marker.has_else = True
        marker.jump.param1 = self.current_offset - marker.offset + 2
        inst = self.add_instruction(OpCode.JUMP, JumpCondition.ALWAYS)
        marker.jump = inst
        marker.offset = self.current_offset

    def if_end(self, marker) -> None:
        marker.jump.param1 = self.current_offset - marker.offset + 1

    def iter_lights(self, operand, code) -> None:
        # If operand is not all, when the generated code starts, the first
        # register must already contain the name of the group or location.
        if operand == Operand.ALL:
            self._traverse_all(code. OpCode.DISC, OpCode.DISCN)
        else:
            self._traverse_vertical(operand, code, OpCode.DISC, OpCode.DISCN)

    def iter_lights_reverse(self, operand, code) -> None:
        # If operand is not all, when the generated code starts, the first
        # register must already contain the name of the group or location.
        if operand == Operand.ALL:
            self._traverse_all(code, OpCode.DISCL)
        else:
            self._traverse_vertical(operand, code, OpCode.DISCL)

    def iter_sets(self, operand, code) -> None:
        self._iter_sets(operand, code, OpCode.DISC)

    def iter_sets_reverse(self, operand, code) -> None:
        self._iter_sets(operand, code, OpCode.DISCL)

    def _traverse_all(self, code, disc_op) -> None:
        """
        Gemerate code to iterate over all of the lights.

        Parameters:
            operand: Operand.GROUP or Operand.LOCATION.
            code: what to execute for each light
            disc_op: OpCode.DISC (forward) or OpCode.DISCL (reverse)
        """
        self.add_list([
            (OpCode.MOVEQ, Operand.LIGHT, Register.OPERAND),
            disc_op
        ])
        loop_marker = self.mark()
        self.add_instruction(OpCode.MOVE, Register.RESULT, LoopVar.CURRENT)
        self.test_op(Operator.NOTEQ, Register.RESULT, Operand.NULL)
        if_marker = self.if_true_start()
        self._code.extend(list(code))
        self.add_list([
            (OpCode.MOVEQ, Operand.LIGHT, Register.OPERAND),
            (CodeGen._disc_next_op(disc_op), LoopVar.CURRENT, Operand.ALL)
        ])
        self.jump_back(loop_marker)
        self.if_end(if_marker)


    def _traverse_vertical(self, operand, code, disc_op) -> None:
        """
        Gemerate code to iterate over lights within a group or location.
        The generated code assumes that the name is in the result register.

        Parameters:
            operand: Operand.GROUP or Operand.LOCATION.
            code: what to execute for each light in the group
            disc_op: OpCode.DISC (forward) or OpCode.DISCL (reverse)
        """
        self.add_list([
            (OpCode.MOVEQ, operand, Register.OPERAND),
            (disc_op, LoopVar.FIRST)
        ])
        loop_marker = self.mark()
        self.add_instruction(OpCode.MOVE, Register.RESULT, LoopVar.CURRENT)
        self.test_op(Operator.NOTEQ, LoopVar.CURRENT, Operand.NULL)
        if_marker = self.if_true_start()
        self._code.extend(list(code))
        self.add_list([
            (OpCode.MOVEQ, operand, Register.OPERAND),
            (CodeGen._disc_next_op(disc_op), LoopVar.CURRENT, LoopVar.FIRST)
        ])
        self.jump_back(loop_marker)
        self.if_end(if_marker)

    def _iter_sets(self, operand, code, disc_op) -> None:
        """
        Iterate over all groups or locations.

        Parameters:
            operand: Operand.GROUP or Operand.LOCATION.
        """
        self.add_instruction(OpCode.MOVEQ, operand, Register.OPERAND)
        self.add_instruction(disc_op, Operand.ALL)
        loop_marker = self.mark()
        self.add_instruction(OpCode.MOVE, Register.RESULT, LoopVar.CURRENT)
        self.test_op(Operator.NOTEQ, Register.RESULT, Operand.NULL)
        if_marker = self.if_true_start()
        self._code.extend(list(code))
        self.add_list([
            (OpCode.MOVEQ, operand, Register.OPERAND),
            (CodeGen._disc_next_op(disc_op), LoopVar.CURRENT, Operand.ALL)
        ])
        self.jump_back(loop_marker)
        self.if_end(if_marker)

    @classmethod
    def _disc_next_op(cls, disc_op):
        assert disc_op in (OpCode.DISC, OpCode.DISCL), str(disc_op)
        if disc_op == OpCode.DISC:
            return OpCode.DISCN
        return OpCode.DISCP

    @classmethod
    def _push_op(cls, oper) -> OpCode:
        if isinstance(oper, (int, float, UnitMode)):
            return OpCode.PUSHQ
        return OpCode.PUSH
