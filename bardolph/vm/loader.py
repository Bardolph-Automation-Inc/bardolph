#!/usr/bin/env python

import argparse
import logging

from bardolph.controller.routine import Routine, RuntimeRoutine

if __name__ == '__main__':
    from bardolph.parser.parse import Parser

from bardolph.lib.injection import inject
from bardolph.runtime import i_runtime
from bardolph.vm.instruction import Instruction
from bardolph.vm.vm_codes import JumpCondition, OpCode


class Loader:
    def __init__(self):
        self._main_segment = []
        self._routine_segment = []
        self._routines = {}
        self._iter = None

    def _next_inst(self):
        if self._iter is None:
            return None
        try:
            return next(self._iter)
        except StopIteration:
            self._iter = None
            return None

    def load(self, instructions):
        self._main_segment.clear()
        self._routine_segment.clear()
        self._routines.clear()
        self._load_runtime()
        if instructions is not None:
            self._iter = iter(instructions)
            inst = self._next_inst()
            while inst is not None:
                if inst.op_code is OpCode.ROUTINE:
                    rtn = self._load_routine(inst)
                    self._routines[rtn.name] = rtn
                else:
                    self._main_segment.append(inst)
                inst = self._next_inst()

    @inject(i_runtime.Runtime)
    def _load_runtime(self, runtime):
        for name, fn in runtime.get_fns().items():
            self._routines[name] = RuntimeRoutine(name, fn)

    def _load_routine(self, current_inst):
        routine_name = current_inst.param0
        self._routine_segment.append(current_inst)
        new_routine = Routine(routine_name)
        new_routine.set_address(len(self._routine_segment) + 1)

        inst = self._next_inst()
        while inst is not None and not (
                inst.op_code is OpCode.END and inst.param0 == routine_name):
            self._routine_segment.append(inst)
            inst = self._next_inst()
        if inst is not None:
            self._routine_segment.append(inst)
        new_routine.set_return(len(self._routine_segment) + 1)
        return new_routine

    def get_code(self):
        if len(self._routine_segment) == 0:
            return self._main_segment
        ret_value = [Instruction(
            OpCode.JUMP, JumpCondition.ALWAYS, len(self._routine_segment) + 1)]
        ret_value.extend(self._routine_segment)
        ret_value.extend(self._main_segment)
        return ret_value

    def get_routines(self):
        return self._routines


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('file', help='name of the script file')
    args = arg_parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(filename)s(%(lineno)d) %(funcName)s(): %(message)s')

    parser = Parser()
    parser_code = parser.parse_file(args.file)

    loader = Loader()
    loader.load(parser_code)
    if loader.get_code() is not None:
        inst_num = 0
        for inst in loader.get_code():
            print('{:5d}: {}'.format(inst_num, inst))
            inst_num += 1
    else:
        print("Error parsing: {}".format(parser.get_errors()))


if __name__ == '__main__':
    main()
