from bardolph.lib.symbol import SymbolType
from bardolph.parser.sub_parser import SubParser
from bardolph.parser.token import Assoc, TokenTypes
from bardolph.vm.vm_codes import OpCode, Operator, Register


class ExpressionParser(SubParser):
    def expression(self, code_gen=None) -> bool:
        code_gen = code_gen or self.code_gen
        return self._atom(code_gen) and self._expression(0, code_gen)

    def routine(self, code_gen=None) -> bool:
        code_gen = code_gen or self.code_gen
        return self._routine_call(code_gen or self.code_gen)

    def rvalue(self, code_gen=None) -> bool:
        # The calculated value is left on top of the expression stack.
        return self.expression(code_gen)

    def lvalue(self, code_gen=None) -> bool:
        # The calculated value is left on top of the expression stack.
        return self.expression(code_gen)

    def _expression(self, min_prec, code_gen) -> bool:
        while (self.current_token.is_binop
                and self.current_token.prec >= min_prec):
            op = self.current_token
            self.next_token()
            if not self._atom(code_gen):
                return False
            while ((self.current_token.is_binop
                        and self.current_token.prec > op.prec)
                    or (self.current_token.assoc is Assoc.RIGHT
                        and self.current_token.prec == op.prec)):
                if not self._expression(self.current_token.prec, code_gen):
                    return False
            if not self._do_op(op, code_gen):
                return False
        return True

    def _atom(self, code_gen) -> bool:
        match self.current_token.token_type:
            case TokenTypes.REGISTER:
                return self._register(code_gen)
            case TokenTypes.NAME:
                return self._name(code_gen)
            case TokenTypes.NUMBER | TokenTypes.LITERAL_STRING:
                return self._literal(code_gen)
            case TokenTypes.MARK:
                match str(self.current_token):
                    case '(' | '{':
                        return self._paren(code_gen)
                    case '+' | '-' | '!':
                        return self._unary(code_gen)
                    case '[':
                        self.next_token()
                        return self._fn_call(code_gen)
        return self.token_error('Incomplete expression at "{}"')

    def _register(self, code_gen) -> bool:
        code_gen.push(self.current_reg)
        return self.next_token()

    def _name(self, code_gen) -> bool:
        name = str(self.current_token)
        if self.context.has_symbol_typed(name, SymbolType.ARRAY):
            return self.next_token() and self._array(name, code_gen)
        if self.context.has_symbol_typed(
                name, SymbolType.VAR, SymbolType.CONSTANT):
            code_gen.push(str(self.current_token))
            return self.next_token()
        return self.trigger_error('Unknown name: {}'.format(name))

    def _array(self, name, code_gen) -> bool:
        if self.current_token != '[':
            return self.token_error('Array reference expected "[", got {}')
        while self.current_token == '[':
            if not self.expression(code_gen):
                return False
            if self.current_token != ']':
                return self.token_error('Expected closing "]", got {}')
            code_gen.pop(Register.RESULT)
            code_gen.add_add_list(OpCode.INDEX, name, Register.RESULT)
            self.next_token()
        return True

    def _literal(self, code_gen) -> bool:
        code_gen.pushq(self.current_literal)
        return self.next_token()

    def _paren(self, code_gen) -> bool:
        closer = ')' if self.current_token == '(' else '}'
        self.next_token()
        if not self.expression(code_gen):
            return False
        if self.current_token != closer:
            return self.trigger_error('Missing closing {}'.format(closer))
        return self.next_token()

    def _unary(self, code_gen) -> bool:
        uminus = self.current_token == '-'
        unot = self.current_token == '!'
        self.next_token()
        if not self._atom(code_gen):
            return False
        if uminus:
            code_gen.add_list(
                (OpCode.PUSHQ, -1),
                (OpCode.OP, Operator.MUL)
            )
        elif unot:
            code_gen.add_instruction(OpCode.OP, Operator.NOT)
        return True

    def _fn_call(self, code_gen) -> bool:
        # Routine call enclosed in brackets.
        if not self._routine_call(code_gen):
            return False
        if str(self.current_token) != ']':
            return self.trigger_error('No closing bracket for function call.')
        return self.next_token()

    def _routine_call(self, code_gen) -> bool:
        routine = self.context.get_routine(str(self.current_token))
        if routine.undefined:
            return self.token_error('Unknown name: "{}"')

        code_gen.add_instruction(OpCode.CTX)
        self.next_token()
        for param_name in routine.value.params:
            if self.current_token == ']':
                return self.trigger_error(
                    'Missing parameter "{}"'.format(param_name))
            if not self.rvalue():
                return False
            code_gen.add_instruction(OpCode.POP, Register.RESULT)
            code_gen.add_instruction(OpCode.PARAM, param_name, Register.RESULT)
        code_gen.add_instruction(OpCode.JSR, routine.name)
        code_gen.add_instruction(OpCode.END_CTX)

        return True

    def _do_op(self, op, code_gen) -> bool:
        # Each of these will pop two arguments off the stack, perform the
        # calculation, and push the result.
        operator = {
            '+': Operator.ADD,
            '-': Operator.SUB,
            '*': Operator.MUL,
            '/': Operator.DIV,
            '%': Operator.MOD,
            '^': Operator.POW,
            '&&': Operator.AND,
            '||': Operator.OR,
            '<': Operator.LT,
            '<=': Operator.LTE,
            '>': Operator.GT,
            '>=': Operator.GTE,
            '==': Operator.EQ,
            '!=': Operator.NOTEQ}.get(op.content)
        if operator is None:
            return self.token_error('Invalid operand {} in expression.')
        code_gen.add_instruction(OpCode.OP, operator)
        return True
