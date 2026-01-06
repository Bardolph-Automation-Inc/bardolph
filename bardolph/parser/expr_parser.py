from bardolph.lib.symbol import SymbolType
from bardolph.parser.sub_parser import SubParser
from bardolph.parser.token import Assoc, TokenTypes
from bardolph.vm.vm_codes import OpCode, Operator, Register


class ExpressionParser(SubParser):
    def expression(self) -> bool:
        return self._atom() and self._expression(0)

    def routine(self, has_brackets: bool = False) -> bool:
        return self._routine_call(has_brackets)

    def rvalue(self) -> bool:
        return self.expression()

    def lvalue(self) -> bool:
        if self.current_token == '[':
            return self._fn_lvalue()
        if not self.current_token.is_a(TokenTypes.NAME):
            return self.token_error('Expected name for assignment, got "{}"')
        name = self.current_token.content
        symbol_type = self.context.get_symbol(name).symbol_type
        match symbol_type:
            case SymbolType.UNDEFINED:
                self.context.add_variable(name)
                self.code_gen.pushq(name)
                return self.next_token()
            case SymbolType.VAR:
                self.code_gen.pushq(name)
                return self.next_token()
            case SymbolType.ARRAY:
                self.code_gen.push(name)
                self.next_token()
                return self._array_lvalue()
            case SymbolType.CONSTANT:
                return self.token_error('attempt to assign to constant "{}"')
        return self.trigger_error('error in assignment')

    def resolve_array(self) -> bool:
        if self.current_token == '[]':
            return self.next_token()

        self.code_gen.add_instruction(OpCode.BASE)
        self.next_token()
        while self.current_token != ']':
            if not self.rvalue():
                return False
            self.code_gen.add_instruction(OpCode.INDEX)
        return self.next_token()

    def _fn_lvalue(self) -> bool:
        self.next_token()
        if not self.current_token.is_a(TokenTypes.NAME):
            return self.token_error('expected rourtine name, got "{}"')
        name = self.current_token.content
        symbol = self.context.get_routine(name)
        if symbol.undefined or symbol.routine is None:
            return self.token_error('unknown routine: "{}')
        if symbol.routine.return_type is not SymbolType.ARRAY:
            return self.token_error('cannot assign to result of calling "{}"')
        if not self.self._routine_call(True):
            return False
        return self.resolve_array() if self.current_token == '[' else True

    def _array_lvalue(self) -> bool:
        if self.current_token == '[' or self.current_token == '[]':
            return self.resolve_array()
        name = self.current_token.content
        routine = self.context.get_routine(name)
        if not routine.undefined and routine.return_type is SymbolType.ARRAY:
            return self.resolve_array()

        return self.token_error(
                'cannot assign to an array variable without square '
                'brackets. Consider adding "[]"')


    def _atom(self) -> bool:
        match self.current_token.token_type:
            case TokenTypes.REGISTER:
                return self._register()
            case TokenTypes.NAME:
                return self._name_rvalue()
            case TokenTypes.NUMBER | TokenTypes.LITERAL_STRING:
                return self._literal()
            case TokenTypes.MARK:
                match self.current_token.content:
                    case '(' | '{':
                        return self._paren()
                    case '+' | '-' | '!':
                        return self._unary()
                    case '[':
                        self.next_token()
                        return self._routine_call(True)
        return self.token_error('Incomplete expression at "{}"')

    def _expression(self, min_prec) -> bool:
        while (self.current_token.is_binop
                and self.current_token.prec >= min_prec):
            op = self.current_token
            self.next_token()
            result = self._atom()
            if not result:
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

    def _register(self) -> bool:
        self.code_gen.push(self.current_reg)
        return self.next_token()

    def _name_rvalue(self) -> bool:
        name = self.current_token.content
        if self.context.has_symbol_typed(name, SymbolType.CONSTANT):
            self.code_gen.push(self.current_token.content)
            return self.next_token()
        symbol = self.context.get_symbol_typed(
            name, SymbolType.VAR, SymbolType.ARRAY)
        if symbol.undefined:
            return self.token_error('unknown name: {}')
        self.next_token()
        if symbol.symbol_type is SymbolType.ARRAY:
            if self.current_token.is_a(TokenTypes.BRACKET_PAIR):
                self.next_token()
            elif self.current_token != '[':
                return self.token_error(
                    'a reference to an array requires square brackets')
            else:
                self.code_gen.push(name)
                return self.resolve_array()
        self.code_gen.push(name)
        return True

    def _literal(self) -> bool:
        self.code_gen.pushq(self.current_literal)
        return self.next_token()

    def _paren(self) -> bool:
        closer = ')' if self.current_token == '(' else '}'
        self.next_token()
        result = self.expression()
        if not result:
            return result
        if self.current_token != closer:
            return self.trigger_error('Missing closing {}'.format(closer))
        self.next_token()
        return result

    def _unary(self) -> bool:
        is_uminus = self.current_token == '-'
        is_unot = self.current_token == '!'
        self.next_token()
        if not self._atom():
            return False
        if is_uminus:
            self.code_gen.add_list(
                (OpCode.PUSHQ, -1),
                (OpCode.OP, Operator.MUL)
            )
        elif is_unot:
            self.code_gen.add_instruction(OpCode.OP, Operator.NOT)
        return True

    def _routine_call(self, in_brackets: bool = False) -> bool:
        routine_symbol = self.context.get_routine(self.current_token.content)
        if routine_symbol.undefined:
            return self.token_error(
                'unknown routine name: "{}". Did you forget to declare a '
                'variable or routine as an array?')

        self.code_gen.add_instruction(OpCode.CTX)
        self.next_token()
        for param_name in routine_symbol.routine.params:
            if self.current_token == ']':
                return self.trigger_error(
                    'Missing parameter "{}"'.format(param_name))
            if not self.rvalue():
                return False
            self.code_gen.add_list(
                (OpCode.POP, Register.RESULT),
                (OpCode.PARAM, param_name, Register.RESULT)
            )
        self.code_gen.add_list(
            (OpCode.JSR, routine_symbol.name),
            OpCode.END_CTX
        )
        if in_brackets:
            if self.current_token != ']':
                return self.token_error('Missing right "]": {}')
            self.next_token()
            if routine_symbol.routine.return_type is SymbolType.ARRAY:
                if self.current_token.is_a(TokenTypes.BRACKET_PAIR):
                    return self.next_token()
                if self.current_token == '[':
                    return self.resolve_array()
                return self.trigger_error(
                    'routine "{}" returns an array and therefore calling it '
                    'requires square brackets, optionally containing an index'
                    .format(routine_symbol.name))
        return True

    def _do_op(self, op) -> bool:
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
        self.code_gen.add_instruction(OpCode.OP, operator)
        return True
