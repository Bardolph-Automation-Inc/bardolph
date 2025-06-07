from bardolph.vm.instruction import Instruction
from bardolph.vm.vm_codes import OpCode


class _InstFrame:
    def __init__(self, inst: Instruction):
        self.inst = inst
        self.address = None
        self.target = None
        self.targeted = False

class Optimizer:
    def __init__(self):
        self._program = None
        self._frames = None

    def optimize(self, program: list) -> list:
        self._frames = [_InstFrame(inst) for inst in program]
        any_jumps = self._find_jumps()
        any_push_pop = self._fold_push_pop()
        if any_push_pop:
            if any_jumps:
                self._set_addresses()
                self._fix_jumps()
            return [frame.inst for frame in self._frames
                        if frame.inst.op_code is not OpCode.NOP]
        return program

    def _find_jumps(self) -> bool:
        # Returns True if any jumps were found, False otherwise.
        inst_pos = 0
        any_jump = False
        for frame in self._frames:
            inst = frame.inst
            if inst.op_code is OpCode.JUMP:
                target_pos = inst_pos + inst.param1
                frame.target = self._frames[target_pos]
                frame.target.targeted = True
                any_jump = True
            inst_pos += 1
        return any_jump

    def _fold_push_pop(self) -> bool:
        """
        Replace push followed by immediate pop with move.

        For example:
            OpCode.PUSHQ, 1
            OpCode.POP, Register.RESULT
        becomes:
            OpCode.MOVEQ, 1, Register.RESULT

        Returns True if any changes were make, False otherwise.
        """
        inst_pos = 0
        any_change = False
        for frame in self._frames:
            inst = frame.inst
            if inst.op_code in (OpCode.PUSH, OpCode.PUSHQ):
                if not frame.targeted:
                    next_pos = inst_pos + 1
                    next_frame = self._frames[next_pos]
                    next_inst = next_frame.inst
                    if (next_inst.op_code is OpCode.POP
                            and not next_frame.targeted):
                        any_change = True
                        if inst.op_code is OpCode.PUSH:
                            inst.op_code = OpCode.MOVE
                        else:
                            inst.op_code = OpCode.MOVEQ
                        inst.param1 = next_inst.param0
                        next_inst.op_code = OpCode.NOP
            inst_pos += 1
        return any_change

    def _set_addresses(self):
        address = 0
        for frame in self._frames:
            if frame.inst.op_code is OpCode.NOP:
                frame.address = None
            else:
                frame.address = address
                address += 1

    def _fix_jumps(self):
        for frame in self._frames:
            if frame.inst.op_code is OpCode.JUMP:
                frame.inst.param1 = frame.target.address - frame.address
