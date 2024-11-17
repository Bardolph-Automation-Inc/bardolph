from bardolph.vm.vm_codes import OpCode, Operand, Register
from bardolph.parser.token import TokenTypes
from bardolph.parser.sub_parser import SubParser


class MatrixParser(SubParser):
    def matrix_spec(self) -> bool:
        self.code_gen.add_instruction(OpCode.MATRIX)
        inline_matrix = not self.current_token.is_a(TokenTypes.BEGIN)
        if inline_matrix and not self.get_all():
            return False
        if not self.operand():
            return False
        if inline_matrix:
            self.code_gen.add_instruction(OpCode.COLOR)
        self.code_gen.add_instruction(OpCode.END, OpCode.MATRIX)
        return True

    def operand(self) -> bool:
        if self.current_token.is_a(TokenTypes.BEGIN):
            return self._complex_operand()
        else:
            return self._simple_operand()

    def get_all(self) -> bool:
        self.code_gen.add_list(
            (OpCode.MOVEQ, None, Register.FIRST_ROW),
            (OpCode.MOVEQ, None, Register.LAST_ROW),
            (OpCode.MOVEQ, None, Register.FIRST_COLUMN),
            (OpCode.MOVEQ, None, Register.LAST_COLUMN),
            (OpCode.MOVEQ, True, Register.MAT_BODY),
            (OpCode.MOVEQ, True, Register.MAT_TOP),
            (OpCode.MOVEQ, Operand.MATRIX, Register.OPERAND),
            OpCode.GET_COLOR
        )
        return True

    def _top(self, has_top) -> bool:
        if has_top:
            return self.trigger_error('"top" supplied more than once.')
        return self.next_token()

    def _rows(self, has_rows) -> bool:
        if has_rows:
            return self.trigger_error('"row" supplied more than once.')
        self.next_token()
        if not self.at_rvalue():
            return self.token_error('Expected range for rows, got {}')
        return self._range(Register.FIRST_ROW, Register.LAST_ROW)

    def _columns(self, has_columns) -> bool:
        if has_columns:
            return self.trigger_error('column supplied more than once.')
        self.next_token()
        if not self.at_rvalue():
            return self.token_error('Expected range for columnss, got {}')
        return self._range(Register.FIRST_COLUMN, Register.LAST_COLUMN)

    def _range(self, first, last, only_one=False):
        if not self.rvalue(first):
            return False
        if not only_one and self.at_rvalue():
            return self.rvalue(last)

        self.code_gen.add_instruction(OpCode.MOVEQ, None, last)
        return True

    def _complex_operand(self) -> bool:
        if self.context.in_matrix():
            return self.token_error("Nested set not allowed.")
        self.context.enter_matrix()
        if not self.parser.command_seq():
            return False
        self.context.fix_return_addrs(self.code_gen)
        self.context.exit_matrix()
        return True

    def _simple_operand(self) -> bool:
        self.code_gen.add_instruction(
            OpCode.MOVEQ, Operand.MATRIX, Register.OPERAND)

        has_top = has_rows = has_columns = False
        while self.current_token.is_any(
                TokenTypes.TOP, TokenTypes.ROW, TokenTypes.COLUMN):
            if self.current_token.is_a(TokenTypes.TOP):
                if not self._top(has_top):
                    return False
                has_top = True
            elif self.current_token.is_a(TokenTypes.ROW):
                if not self._rows(has_rows):
                    return False
                has_rows = True
            elif self.current_token.is_a(TokenTypes.COLUMN):
                if not self._columns(has_columns):
                    return False
                has_columns = True

        self.code_gen.add_instruction(OpCode.MOVEQ, has_top, Register.MAT_TOP)
        if not (has_rows or has_columns):
            self.code_gen.add_instruction(
                OpCode.MOVEQ, False, Register.MAT_BODY)
        else:
            self.code_gen.add_instruction(
                OpCode.MOVEQ, True, Register.MAT_BODY)
            if not has_rows:
                self.code_gen.add_list(
                    (OpCode.MOVEQ, None, Register.FIRST_ROW),
                    (OpCode.MOVEQ, None, Register.LAST_ROW)
                )
            if not has_columns:
                self.code_gen.add_list(
                    (OpCode.MOVEQ, None, Register.FIRST_COLUMN),
                    (OpCode.MOVEQ, None, Register.LAST_COLUMN)
                )
        return True
