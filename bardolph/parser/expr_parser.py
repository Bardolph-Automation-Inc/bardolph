import ast

from bardolph.vm.vm_codes import OpCode, Operator, Register

class Visitor:
    _class_to_op = {
        ast.Add: Operator.ADD,
        ast.And: Operator.AND,
        ast.Div: Operator.DIV,
        ast.Eq: Operator.EQ,
        ast.Lt: Operator.LT,
        ast.LtE: Operator.LTE,
        ast.Gt: Operator.GT,
        ast.GtE: Operator.GTE,
        ast.Mod: Operator.MOD,
        ast.Mult: Operator.MUL,
        ast.Not: Operator.NOT,
        ast.NotEq: Operator.NOTEQ,
        ast.Or: Operator.OR,
        ast.Pow: Operator.POW,
        ast.Sub: Operator.SUB,
        ast.UAdd: Operator.UADD,
        ast.USub: Operator.USUB,
    }

    def __init__(self, code_gen):
        self._code_gen = code_gen

    def expression(self, node):
        """ BinOp, UnaryOp, Num, Constant, or Name """
        if isinstance(node, ast.Expression):
            node = node.body
        fn_dict = {
            ast.BinOp: self._binop,
            ast.BoolOp: self._boolop,
            ast.Compare: self._compare,
            ast.Constant: self._constant,
            ast.Name: self._name,
            ast.Num: self._num,
            ast.UnaryOp: self._unaryop
        }
        fn = fn_dict.get(type(node), self._nop)
        fn(node)

    def _binop(self, node):
        self.expression(node.left)
        self.expression(node.right)
        self._op(node.op)

    def _boolop(self, node):
        self.expression(node.values[0])
        self.expression(node.values[1])
        self._op(node.op)

    def _compare(self, node):
        self.expression(node.left)
        self.expression(node.comparators[0])
        self._code_gen.add_instruction(
            OpCode.OP,
            Visitor._class_to_op.get(type(node.ops[0]), None))

    def _constant(self, node):
        self._code_gen.add_instruction(OpCode.PUSH, node.n)

    def _name(self, node):
        dest = Register.from_string(node.id) or node.id
        self._code_gen.add_instruction(OpCode.PUSH, dest)

    def _num(self, node):
        self._code_gen.add_instruction(OpCode.PUSHQ, node.n)

    def _unaryop(self, node):
        self.expression(node.operand)
        self._op(node.op)

    def _nop(self, node):
        print("parser error", node)

    def _op(self, op):
        self._code_gen.add_instruction(
            OpCode.OP, Visitor._class_to_op.get(type(op), None))


class ExprParser:
    def __init__(self, expr_string):
        try:
            self._tree = ast.parse(expr_string.strip(), mode="eval")
        except SyntaxError:
            self._tree = None

    def generate_code(self, code_gen) -> bool:
        """
        Generate the VM code to evaluate the expression. When that code is
        done, the result will be at the top of the stack.
        """
        if self._tree is None:
            return False

        visitor = Visitor(code_gen)
        visitor.expression(self._tree)
        return True
