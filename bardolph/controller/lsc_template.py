#!/usr/bin/env python

import argparse
import logging

from bardolph.lib import injection
from bardolph.lib import settings
from bardolph.lib.time_pattern import TimePattern

from bardolph.controller import arg_helper
from bardolph.controller import config_values
from bardolph.controller.instruction import Instruction, OpCode
from bardolph.controller.instruction import Operand, Register, SetOp
from bardolph.controller import light_module
from bardolph.controller import machine

instructions = [
    #instructions

]

current_instruction = 0

def next_instruction():
    global current_instruction
    if current_instruction < len(instructions):
        value = instructions[current_instruction]
        current_instruction += 1
        return value
    return None

def build_instructions():
    program = []
    op_code = next_instruction()
    while op_code != None:
        if op_code in (OpCode.SET_REG, OpCode.TIME_PATTERN):
            param0 = next_instruction()
            param1 = next_instruction()
            program.append(Instruction(op_code, param0, param1))
        else:
            program.append(Instruction(op_code))
        op_code = next_instruction()
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
