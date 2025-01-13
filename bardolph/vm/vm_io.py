import logging
import string

from bardolph.lib.i_lib import Output
from bardolph.lib.injection import inject
from bardolph.vm.vm_codes import IoOp, Register

class VmIo:
    def __init__(self, call_stack, reg):
        self._call_stack = call_stack
        self._reg = reg
        self._unnamed = []

    @inject(Output)
    def out(self, inst, output):
        match inst.param0:
            case IoOp.LITERAL:
                self._unnamed.append(inst.param1)
            case IoOp.REGISTER:
                self._unnamed.append(self._reg.get_by_enum(inst.param1))
            case IoOp.PRINT:
                if len(self._unnamed) > 0:
                    output.out(self._unnamed[0])
                    self._unnamed.clear()
            case IoOp.PRINT_END:
                output.newline()
            case IoOp.PRINTF:
                self._printf(inst)
            case _:
                logging.error(
                    "print command internal error: {}".format(inst.param0))

    def reset(self):
        self._unnamed.clear()

    @inject(Output)
    def flush(self, output):
        for remaining in self._unnamed:
            output.out(remaining)
        output.flush()
        self.reset()

    @inject(Output)
    def _printf(self, inst, output):
        format_str = inst.param1.replace('\\n', '\n')
        named = {}
        for field in string.Formatter().parse(format_str):
            name = field[1]
            if name is not None and len(name) > 0 and not name.isdecimal():
                reg = Register.from_string(name)
                if reg is not None:
                    named[name] = self._reg.get_by_enum(reg)
                else:
                    named[name] = self._call_stack.get_variable(name)
        output.out(format_str.format(*self._unnamed, **named))
        self._unnamed.clear()
