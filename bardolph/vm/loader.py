#!/usr/bin/env python

import argparse
import logging

from bardolph.controller.routine import Routine
if __name__ == '__main__':
    from bardolph.parser.parse import Parser

from .instruction import Instruction
from .vm_codes import JumpCondition, OpCode

class Loader:
    def __init__(self):
        self._main_segment = []
        self._routine_segment = []
        self._iter = None

    def _next_inst(self):
        if self._iter is None:
            return None
        try:
            return next(self._iter)
        except StopIteration:
            self._iter = None
            return None

    def load(self, instructions, routines):
        """ Upon completion routines will be populated as a dictionary
        of Routine objects, keyed on routine name. """
        self._main_segment.clear()
        self._routine_segment.clear()
        if instructions is not None:
            self._iter = iter(instructions)
            inst = self._next_inst()
            while inst is not None:
                if inst.op_code is OpCode.ROUTINE:
                    rtn = self._load_routine(inst)
                    routines[rtn.name] = rtn
                else:
                    self._main_segment.append(inst)
                inst = self._next_inst()

    def _load_routine(self, current_inst):
        self._routine_segment.append(current_inst)
        rtn = Routine(current_inst.param0)
        rtn.set_address(len(self._routine_segment) + 1)

        inst = self._next_inst()
        while inst is not None and inst.op_code is not OpCode.END:
            self._routine_segment.append(inst)
            inst = self._next_inst()
        if inst is not None:
            self._routine_segment.append(inst)
        return rtn

    @property
    def code(self):
        if len(self._routine_segment) == 0:
            return self._main_segment
        ret_value = [Instruction(
            OpCode.JUMP, JumpCondition.ALWAYS, len(self._routine_segment) + 1)]
        ret_value.extend(self._routine_segment)
        ret_value.extend(self._main_segment)
        return ret_value

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('file', help='name of the script file')
    args = arg_parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(filename)s(%(lineno)d) %(funcName)s(): %(message)s')

    parser = Parser()
    parser_code = parser.load(args.file)

    loader = Loader()
    routines = {}
    loader.load(parser_code, routines)
    if loader.code is not None:
        inst_num = 0
        for inst in loader.code:
            print('{:5d}: {}'.format(inst_num, inst))
            inst_num += 1
    else:
        print("Error parsing: {}".format(parser.get_errors()))


if __name__ == '__main__':
    main()
