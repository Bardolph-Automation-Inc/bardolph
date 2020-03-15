from bardolph.controller import units

from .eval_stack import EvalStack
from .vm_codes import Operator, Register

class VmMath:
    # a was the top of the stack, and b was the element below it.
    _fn_table = {
        Operator.ADD: lambda a, b: b + a,
        Operator.AND: lambda a, b: b and a,
        Operator.DIV: lambda a, b: b / a,
        Operator.EQ: lambda a, b: b == a,
        Operator.GT: lambda a, b: b > a,
        Operator.GTE: lambda a, b: b >= a,
        Operator.LT: lambda a, b: b < a,
        Operator.LTE: lambda a, b: b <= a,
        Operator.MUL: lambda a, b: b * a,
        Operator.NOTEQ: lambda a, b: b != a,
        Operator.OR: lambda a, b: b or a,
        Operator.SUB: lambda a, b: b - a
    }

    def __init__(self, call_stack, reg):
        self._call_stack = call_stack
        self._reg = reg
        self._eval_stack = EvalStack()

    def reset(self) -> None:
        self._eval_stack.clear()

    def push(self, srce) -> None:
        if isinstance(srce, Register):
            value = self._reg.get_by_enum(srce)
            if self._reg.unit_mode == units.UnitMode.LOGICAL:
                value = units.as_logical(srce, value)
        elif isinstance(srce, (int, float)):
            value = srce
        elif isinstance(srce, str):
            value = self._call_stack.get_variable(srce)
            assert value is not None, "missing value: %r" % srce
        self._eval_stack.push(value)

    def pushq(self, srce) -> None:
        self._eval_stack.push(srce)

    def pop(self, dest) -> None:
        value = self._eval_stack.pop()
        if isinstance(dest, Register):
            if self._reg.unit_mode == units.UnitMode.LOGICAL:
                value = units.as_raw(dest, value)
            self._reg.set_by_enum(dest, value)
        elif isinstance(dest, str):
            self._call_stack.put_variable(dest, value)

    def op(self, operator) -> None:
        if operator in (Operator.UADD, Operator.USUB, Operator.NOT):
            self.unary_op(operator)
        else:
            self.bin_op(operator)

    def unary_op(self, operator) -> None:
        if operator == Operator.USUB:
            self._eval_stack.replace_top(-self._eval_stack.top)
        elif operator == Operator.NOT:
            self._eval_stack.replace_top(not self._eval_stack.top)

    def bin_op(self, operator) -> None:
        op1 = self._eval_stack.pop()
        op2 = self._eval_stack.pop()
        self._eval_stack.push(VmMath._fn_table[operator](op1, op2))
