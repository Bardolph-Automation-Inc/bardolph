from bardolph.vm.instruction import Instruction
from bardolph.vm.vm_codes import JumpCondition, OpCode, Operator, Register

class _JumpMarker:
    def __init__(self, inst, offset):
        self.jump = inst
        self.offset = offset
        self.has_else = False

class CodeGen:
    def __init__(self):
        self._code = []

    @property
    def program(self):
        return self._code

    @property
    def current_offset(self):
        return len(self._code)

    def clear(self):
        self._code.clear()

    def push(self, operand):
        self.add_instruction(CodeGen._push_op(operand), operand)

    def pop(self, operand):
        self.add_instruction(OpCode.POP, operand)

    def add_instruction(self, op_code, param0=None, param1=None):
        inst = Instruction(op_code, param0, param1)
        self._code.append(inst)
        return inst

    def add_list(self, inst_list):
        for code in inst_list:
            op_code = code[0]
            param0 = code[1] if len(code) > 1 else None
            param1 = code[2] if len(code) > 2 else None
            self.add_instruction(op_code, param0, param1)

    def addition(self, addend0, addend1) -> None:
        push0 = CodeGen._push_op(addend0)
        push1 = CodeGen._push_op(addend1)
        self.add_list([
            (push0, addend0),
            (push1, addend1),
            (OpCode.OP, Operator.ADD)
        ])

    def subtraction(self, minuend, subtrahend) -> None:
        # minuend - subtrahend
        # Leaves the difference on top of the stack.
        push = OpCode.PUSHQ if isinstance(
            subtrahend, (int, float)) else OpCode.PUSH
        self.add_list([
            (OpCode.PUSH, minuend),
            (push, subtrahend),
            (OpCode.OP, Operator.SUB)
        ])

    def decrement(self, dest) -> None:
        self.add_list([
            (OpCode.PUSH, dest),
            (OpCode.PUSHQ, 1),
            (OpCode.OP, Operator.SUB),
            (OpCode.POP, dest)
        ])

    def push_context(self, params):
        self.add_instruction(OpCode.JSR, params)

    def test_op(self, operator, op0, op1):
        """
        Generate code to perform a boolean operation on two operands. The
        generated code will set the RESULT register accordingly.

        If literal is True, then the second operand is a literal value and
        should be embedded verbatim in the instruction.
        """
        push = OpCode.PUSHQ if isinstance(op1, (int, float)) else OpCode.PUSH
        self.add_list([
            (OpCode.PUSH, op0),
            (push, op1),
            (OpCode.OP, operator),
            (OpCode.POP, Register.RESULT)
        ])

    def mark(self):
        return _JumpMarker(None, self.current_offset)

    def jump_back(self, marker):
        offset = marker.offset - self.current_offset
        self.add_instruction(OpCode.JUMP, JumpCondition.ALWAYS, offset)

    def if_start(self):
        inst = self.add_instruction(OpCode.JUMP, JumpCondition.IF_FALSE)
        return _JumpMarker(inst, self.current_offset)

    def if_else(self, marker):
        marker.has_else = True
        marker.jump.param1 = self.current_offset - marker.offset + 2
        inst = self.add_instruction(OpCode.JUMP, JumpCondition.ALWAYS)
        marker.jump = inst
        marker.offset = self.current_offset

    def if_end(self, marker):
        marker.jump.param1 = self.current_offset - marker.offset + 1

    def optimize(self):
        idem = (Register.NAME, Register.OPERAND, Register.TIME,
                Register.DURATION, Register.FIRST_ZONE, Register.LAST_ZONE)
        last_value = {}
        for inst in self._code:
            reg = inst.param1
            if inst.op_code == OpCode.MOVE:
                if reg in idem and reg in last_value:
                    del last_value[reg]
            elif inst.op_code == OpCode.MOVEQ and reg in idem:
                value = inst.param0
                if reg in last_value and value == last_value[reg]:
                    inst.nop()
                else:
                    last_value[reg] = value
            elif inst.op_code == OpCode.ROUTINE:
                last_value.clear()
        self._code = [inst for inst in self._code if inst.op_code != OpCode.NOP]

    @classmethod
    def _push_op(cls, oper):
        return OpCode.PUSHQ if isinstance(oper, (int, float)) else OpCode.PUSH
