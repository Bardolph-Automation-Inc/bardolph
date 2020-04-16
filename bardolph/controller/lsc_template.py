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

assembly = [
    #instructions

]

params_0 = (OpCode.BREAKPOINT, OpCode.COLOR, OpCode.END_LOOP, OpCode.LOOP,
            OpCode.NOP, OpCode.PAUSE, OpCode.POWER, OpCode.STOP, OpCode.WAIT)

params_1 = (OpCode.END, OpCode.GET_COLOR, OpCode.JSR, OpCode.OP, OpCode.POP,
            OpCode.PUSH, OpCode.PUSHQ, OpCode.ROUTINE)

def get_assembly():
    current_instruction = 0
    while current_instruction < len(assembly):
        value = assembly[current_instruction]
        current_instruction += 1
        yield value

def build_instructions():
    program = []
    it = iter(get_assembly())
    op_code = next(it, None)
    while op_code is not None:
        if op_code in params_0:
            param_count = 0
        elif op_code in params_1:
            param_count = 1
        else:
            param_count = 2
        param0 = None if param_count < 1 else next(it)
        param1 = None if param_count < 2 else next(it)
        program.append(Instruction(op_code, param0, param1))
        op_code = next(it, None)
    return program

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        '-d', '--debug', help='do debug-level logging', action='store_true')
    ap.add_argument(
        '-f', '--fakes', help='use fake lights', action='store_true')
    arg_helper.add_n_argument(ap)
    args = ap.parse_args()

    injection.configure()
    settings_init = settings.use_base(config_values.functional)
    overrides = {
        'sleep_time': 0.1
    }
    if args.debug:
        overrides['log_level'] = logging.DEBUG
        overrides['log_to_console'] = True
    if args.fakes:
        overrides['use_fakes'] = True
    n_arg = arg_helper.get_overrides(args)
    if n_arg is not None and not args.fakes:
        overrides.update(n_arg)

    settings_init.add_overrides(overrides).configure()
    light_module.configure()
    machine.Machine().run(build_instructions())


if __name__ == '__main__':
    main()
