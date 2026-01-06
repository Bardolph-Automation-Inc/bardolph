import operator
from numbers import Number

from bardolph.vm.array import ArrayBase, ArrayCursor, array_set, assure_rvalue
from bardolph.vm.call_stack import CallStack
from bardolph.vm.eval_stack import EvalStack
from bardolph.vm.vm_codes import LoopVar, Operand, Operator, Register


class VmMath:
    def __init__(self, call_stack: CallStack, reg):
        self._call_stack = call_stack
        self._reg = reg
        self._eval_stack = EvalStack()

    @property
    def eval_stack(self) -> EvalStack:
        return self._eval_stack

    @property
    def call_stack(self) -> CallStack:
        return self._call_stack

    def reset(self) -> None:
        self.eval_stack.clear()

    def push(self, srce) -> None:
        value = None
        if (isinstance(srce, Number) or
                srce in (Register.UNIT_MODE, Operand.NULL)):
            value = srce
        elif isinstance(srce, Register):
            value = self._reg.get_by_enum(srce)
        elif isinstance(srce, (str, LoopVar)):
             value = self._call_stack.get_variable(srce)

        assert value is not None, "pushing None onto eval stack"
        self._eval_stack.push(value)

    def pushq(self, srce) -> None:
        self._eval_stack.push(srce)

    def pop(self, dest) -> None:
        self._top_to_dest(self.eval_stack.pop(), dest)

    def peek(self, dest) -> None:
        self._top_to_dest(self.eval_stack.top(), dest)

    def _top_to_dest(self, value, dest) -> None:
        if isinstance(value, ArrayCursor) and value.is_at_leaf():
            value = value.get_value()
        if dest is None:
            return
        if isinstance(dest, Register):
            self._reg.set_by_enum(dest, value)
        elif isinstance(dest, (str, LoopVar)):
            self.call_stack.put_variable(dest, value)

    def op(self, operator: Operator) -> None:
        match operator:
            case Operator.UADD:
                return
            case Operator.USUB:
                self.eval_stack.replace_top(-self.eval_stack.top())
            case Operator.NOT:
                self.eval_stack.replace_top(not self.eval_stack.top())
            case Operator.AND | Operator.OR:
                self.logical_op(operator)
            case Operator.SET:
                self._set()
            case Operator.SIZE:
                self.eval_stack.replace_top(len(self.eval_stack.top()))
            case _:
                self.bin_op(operator)

    _bin_op_dict = {
        Operator.ADD: operator.add,
        Operator.DIV: operator.truediv,
        Operator.EQ: operator.__eq__,
        Operator.GT: operator.gt,
        Operator.GTE: operator.ge,
        Operator.LT: operator.lt,
        Operator.LTE: operator.le,
        Operator.NOTEQ: operator.ne,
        Operator.MOD: operator.mod,
        Operator.MUL: operator.mul,
        Operator.POW: operator.pow,
        Operator.SUB: operator.sub
    }

    def bin_op(self, operator: Operator) -> None:
        op2 = assure_rvalue(self.eval_stack.pop())
        op1 = assure_rvalue(self.eval_stack.pop())
        self.eval_stack.push(self._bin_op_dict[operator](op1, op2))

    def _set(self) -> None:
        rvalue = self.eval_stack.pop()
        lvalue = self.eval_stack.pop()
        if isinstance(lvalue, ArrayBase):
            array_set(lvalue, rvalue)
        elif isinstance(lvalue, Register):
            self._reg.set_by_enum(lvalue, rvalue)
        elif isinstance(rvalue, ArrayCursor):
            self.call_stack.put_variable(lvalue, rvalue.get_value())
        else:
            self.call_stack.put_variable(lvalue, rvalue)

    def logical_op(self, operator: Operator) -> None:
        op2 = bool(self.eval_stack.pop())
        op1 = bool(self.eval_stack.pop())
        result = op1 and op2 if operator == Operator.AND else op1 or op2
        self.eval_stack.push(result)
