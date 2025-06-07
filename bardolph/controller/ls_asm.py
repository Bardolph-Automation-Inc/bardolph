from bardolph.vm.instruction import Instruction, OpCode

def assemble(assembly) -> list:
    program = []
    it = iter(assembly)
    token = next(it, None)

    while token is not None:
        op_code = token
        token = next(it, None)
        if isinstance(token, OpCode):
            program.append(Instruction(op_code))
        else:
            param0 = token
            token = next(it, None)
            if isinstance(token, OpCode):
                program.append(Instruction(op_code, param0))
            else:
                param1 = token
                program.append(Instruction(op_code, param0, param1))
                token = next(it, None)

    return program
