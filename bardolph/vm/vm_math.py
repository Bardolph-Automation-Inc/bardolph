from .eval_stack import EvalStack
from .vm_codes import LoopVar, Operator, Register

class VmMath:
    # a was the top of the stack, and b was the element below it.
    _fn_table = {
        Operator.ADD: lambda a, b: a + b,
        Operator.AND: lambda a, b: a and b,
        Operator.DIV: lambda a, b: a / b,
        Operator.EQ: lambda a, b: a == b,
        Operator.GT: lambda a, b: a > b,
        Operator.GTE: lambda a, b: a >= b,
        Operator.LT: lambda a, b: a < b,
        Operator.LTE: lambda a, b: a <= b,
        Operator.NOTEQ: lambda a, b: a != b,
        Operator.OR: lambda a, b: a or b,
        Operator.MUL: lambda a, b: a * b,
        Operator.SUB: lambda a, b: a - b
    }

    def __init__(self, call_stack, reg):
        self._call_stack = call_stack
        self._reg = reg
        self._eval_stack = EvalStack()

    def reset(self) -> None:
        self._eval_stack.clear()

    def push(self, srce) -> None:
        value = None
        if isinstance(srce, Register):
            value = self._reg.get_by_enum(srce)
        elif isinstance(srce, (int, float)):
            value = srce
        elif isinstance(srce, (str, LoopVar)):
            value = self._call_stack.get_variable(srce)
        assert value is not None
        self._eval_stack.push(value)

    def pushq(self, srce) -> None:
        self._eval_stack.push(srce)

    def pop(self, dest) -> None:
        value = self._eval_stack.pop()
        if isinstance(dest, Register):
            self._reg.set_by_enum(dest, value)
        elif isinstance(dest, (str, LoopVar)):
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
        op2 = self._eval_stack.pop()
        op1 = self._eval_stack.pop()
        self._eval_stack.push(VmMath._fn_table[operator](op1, op2))
