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
from bardolph.vm.vm_codes import IoOp, JumpCondition, LoopVar, Operand, Operator
from bardolph.vm.vm_codes import Register, SetOp

_assembly = [
    #instructions

]

def build_instructions():
    program = []
    it = iter(_assembly)
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
    settings_init.add_overrides(overrides).apply_env().configure()
    light_module.configure()
    machine.Machine().run(build_instructions())


if __name__ == '__main__':
    main()
