import logging
import string

from .vm_codes import IoOp, Register

class VmIo:
    def __init__(self, call_stack, reg):
        self._call_stack = call_stack
        self._reg = reg
        self._unnamed = []

    def out(self, inst):
        io_op = inst.param0
        if io_op is IoOp.REGISTER:
            self._unnamed.append(self._reg.get_by_enum(inst.param1))
        elif io_op is IoOp.PRINT:
            print(self._unnamed[0], end=inst.param1)
            self._unnamed.clear()
        elif io_op is IoOp.PRINTF:
            self._printf(inst)
        else:
            logging.error("Unrecognized output: {}".format(io_op))

    def reset(self):
        self._unnamed.clear()

    def _printf(self, inst):
        format_str = inst.param1
        params = {}
        for field in string.Formatter().parse(format_str):
            name = field[1] or ''
            if len(name) > 0 and not name.isdecimal():
                reg = Register.from_string(name)
                if reg is not None:
                    params[name] = self._reg.get_by_enum(reg)
                else:
                    params[name] = self._call_stack.get_variable(name)
        print(format_str.format(*self._unnamed, **params))
        self._unnamed.clear()
