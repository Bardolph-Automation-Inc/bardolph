#!/usr/bin/env python

import argparse
import logging

from ..lib import injection
from ..lib import settings

from . import config_values
from .instruction import Instruction, OpCode, Operand
from . import light_module
from . import machine

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
        if op_code == OpCode.SET_REG:
            name = next_instruction()
            value = next_instruction()
            program.append(Instruction(OpCode.SET_REG, name, value))
        else:
            program.append(Instruction(op_code))
        op_code = next_instruction()
    return program

def run_script(overrides = None):
    injection.configure()
    settings.using_base(config_values.functional).configure()
    if overrides != None:
        settings.specialize(overrides)

    light_module.configure()
    machine.Machine().run(build_instructions())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        '-d', '--debug', help='do debug-level logging', action='store_true')
    ap.add_argument(
        '-f', '--fakes', help='use fake lights', action='store_true')
    args = ap.parse_args()

    overrides = {'sleep_time': 0.1}
    if args.debug:
        overrides['log_level'] = logging.DEBUG
        overrides['log_to_console'] = True
    if args.fakes:
        overrides['use_fakes'] = True
    run_script(overrides)


if __name__ == '__main__':
    main()
