from bardolph.vm.vm_codes import OpCode, Operator, Register
from bardolph.parser.token import Assoc, TokenTypes
from bardolph.parser.sub_parser import SubParser


class ExpressionParser(SubParser):
    def expression(self):
        return self._atom() and self._expression(0)

    def _expression(self, min_prec) -> bool:
        while (self.current_token.is_binop
                and self.current_token.prec >= min_prec):
            op = self.current_token
            self.next_token()
            if not self._atom():
                return False
            while ((self.current_token.is_binop
                        and self.current_token.prec > op.prec)
                    or (self.current_token.assoc is Assoc.RIGHT
                        and self.current_token.prec == op.prec)):
                if not self._expression(self.current_token.prec):
                    return False
            if not self._do_op(op):
                return False
        return True

    def _atom(self) -> bool:
        if str(self.current_token) == '(':
            self.next_token()
            if not self.expression():
                return False
            if self.current_token != ')':
                return self.token_error('Unmatched parenthesis: {}')
            return self.next_token()

        uminus = str(self.current_token) == '-'
        if str(self.current_token) in '+-':
            self.next_token()
            if not self._atom():
                return False
            if uminus:
                self.code_gen.add_list(
                    (OpCode.PUSHQ, -1),
                    (OpCode.OP, Operator.MUL)
                )
        elif not self.rvalue(OpCode.PUSH):
            return False
        return True

    def _do_op(self, op) -> bool:
        # Each of these will pop two arguments off the stack, perform the
        # calculation, and push the result.
        operator = {
            '+': Operator.ADD,
            '-': Operator.SUB,
            '*': Operator.MUL,
            '/': Operator.DIV,
            '^': Operator.POW,
            'and': Operator.AND,
            'or': Operator.OR,
            '<': Operator.LT,
            '<=': Operator.LTE,
            '>': Operator.GT,
            '>=': Operator.GTE,
            '==': Operator.EQ,
            '!=': Operator.NOTEQ}.get(op.content)
        if operator is None:
            return self.token_error('Invalid operand {} in expression.')
        self.code_gen.add_instruction(OpCode.OP, operator)
        return True
