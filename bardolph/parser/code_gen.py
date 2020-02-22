from ..controller.instruction import Instruction, OpCode, Register

class CodeGen:
    def __init__(self):
        self._code = []
        self._a_record = []

    @property
    def program(self):
        return self._code

    def clear(self):
        self._code.clear()
        self._a_record.clear()

    def add_instruction(self, op_code, param0=None, param1=None):
        inst = Instruction(op_code, param0, param1)
        self._code.append(inst)
        return inst

    def push_context(self, params):
        self.add_instruction(OpCode.CALL, params)

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
