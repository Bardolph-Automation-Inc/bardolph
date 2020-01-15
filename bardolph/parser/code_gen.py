from ..controller.instruction import Instruction, OpCode, Register, SeriesOp

class CodeGen:
    def __init__(self):
        self._code = []
    
    @property
    def program(self):
        return self._code
    
    def clear(self):
        self._code.clear()
    
    def add_instruction(self, op_code, param0=None, param1=None):
        inst = Instruction(op_code, param0, param1)
        self._code.append(inst)
        return inst
    
    def push_context(self, params):
        self.add_instruction(OpCode.CALL, params)
    
    def optimize(self):
        idem = (Register.NAME, Register.OPERAND, Register.SERIES, Register.TIME,
                Register.DURATION, Register.FIRST_ZONE, Register.LAST_ZONE)
        last_value = {}
        any_series = False
               
        for inst in self._code:
            if inst.op_code == OpCode.SERIES and inst.param0 == SeriesOp.INIT:
                any_series = True
            if inst.op_code == OpCode.SET_REG and inst.param0 in idem:
                reg = inst.param0
                value = inst.param1
                if reg in last_value and value == last_value[reg]:
                    inst.nop()
                else:
                    last_value[reg] = value
        if not any_series:
            for inst in self._code:
                if (inst.op_code == OpCode.SERIES
                        or inst.param0 == Register.SERIES):
                    inst.nop()
        self._code = [inst for inst in self._code if inst.op_code != OpCode.NOP]
