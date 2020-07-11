#!/usr/bin/env python

import argparse
import logging

from bardolph.lib import injection
from bardolph.lib import settings
from bardolph.controller import arg_helper
from bardolph.controller import config_values
from bardolph.controller import light_module
from bardolph.controller.units import UnitMode
from bardolph.vm import machine
from bardolph.vm.instruction import Instruction, OpCode
from bardolph.vm.vm_codes import JumpCondition, LoopVar, Operand, Operator
from bardolph.vm.vm_codes import Register, SetOp

_assembly = [
    #instructions

]

_param_counts = {
    OpCode.BREAKPOINT : 0, OpCode.COLOR : 0, OpCode.CONSTANT: 2,
    OpCode.DISC : 0, OpCode.DISCM : 1, OpCode.DNEXT : 1, OpCode.DNEXTM : 2,
    OpCode.END : 1, OpCode.END_LOOP : 0, OpCode.GET_COLOR : 0, OpCode.JSR : 1,
    OpCode.JUMP: 2, OpCode.LOOP : 0, OpCode.MOVE: 2, OpCode.MOVEQ: 2,
    OpCode.NOP : 0, OpCode.OP : 1, OpCode.PARAM: 2, OpCode.PAUSE : 0,
    OpCode.POP : 1, OpCode.POWER : 0, OpCode.PUSH : 1, OpCode.PUSHQ : 1,
    OpCode.ROUTINE : 1, OpCode.STOP : 0, OpCode.TIME_PATTERN: 2, OpCode.WAIT: 0
}

def get_assembly():
    current_instruction = 0
    while current_instruction < len(_assembly):
        value = _assembly[current_instruction]
        current_instruction += 1
        yield value

def build_instructions():
    program = []
    it = iter(get_assembly())
    op_code = next(it, None)
    while op_code is not None:
        param_count = _param_counts[OpCode(op_code)]
        param0 = None if param_count < 1 else next(it)
        param1 = None if param_count < 2 else next(it)
        program.append(Instruction(op_code, param0, param1))
        op_code = next(it, None)
    return program

def main():
    injection.configure()

    ap = argparse.ArgumentParser()
    ap.add_argument(
        '-v', '--verbose', help='do debug-level logging', action='store_true')
    ap.add_argument(
        '-f', '--fakes', help='use fake lights', action='store_true')
    arg_helper.add_n_argument(ap)
    args = ap.parse_args()

    overrides = {
        'sleep_time': 0.1
    }
    if args.verbose:
        overrides['log_level'] = logging.DEBUG
        overrides['log_to_console'] = True
    if args.fakes:
        overrides['use_fakes'] = True
    n_arg = arg_helper.get_overrides(args)
    if n_arg is not None and not args.fakes:
        overrides.update(n_arg)

    settings_init = settings.using(config_values.functional)
    settings_init.add_overrides(overrides).configure()
    light_module.configure()
    machine.Machine().run(build_instructions())


if __name__ == '__main__':
    main()
