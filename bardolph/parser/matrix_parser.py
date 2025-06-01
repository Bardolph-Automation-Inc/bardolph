from bardolph.parser.sub_parser import SubParser
from bardolph.parser.token import TokenTypes
from bardolph.vm.vm_codes import OpCode, Operand, Register


class MatrixParser(SubParser):
    def matrix_spec(self) -> bool:
        """
        Entry point for general parser. At this point, the current token is
        row, column, or begin.
        """
        self.code_gen.add_instruction(OpCode.MATRIX)
        inline_matrix = not self.current_token.is_a(TokenTypes.BEGIN)
        if not self.operand_list():
            return False
        if inline_matrix:
            # Store the color in the specified section of the matrix.
            self.code_gen.add_instruction(OpCode.COLOR)
        self.code_gen.add_instruction(OpCode.END, Operand.MATRIX)
        return True

    def operand_list(self) -> bool:
        if self.current_token.is_a(TokenTypes.BEGIN):
            return self._block_operand()
        else:
            return self._inline_operand()

    def get_all(self) -> bool:
        self.code_gen.add_list(
            (OpCode.MOVEQ, None, Register.FIRST_ROW),
            (OpCode.MOVEQ, None, Register.LAST_ROW),
            (OpCode.MOVEQ, None, Register.FIRST_COLUMN),
            (OpCode.MOVEQ, None, Register.LAST_COLUMN),
            (OpCode.MOVEQ, Operand.MATRIX, Register.OPERAND),
            OpCode.GET_COLOR
        )
        return True

    def _rows(self, has_rows) -> bool:
        if has_rows:
            return self.trigger_error('"row" supplied more than once.')
        self.next_token()
        if not self.at_rvalue(False):
            return self.token_error('Expected range for rows, got {}')
        return self._range(Register.FIRST_ROW, Register.LAST_ROW)

    def _columns(self, has_columns) -> bool:
        if has_columns:
            return self.trigger_error('column supplied more than once.')
        self.next_token()
        if not self.at_rvalue(False):
            return self.token_error('Expected a range for columns, got {}')
        return self._range(Register.FIRST_COLUMN, Register.LAST_COLUMN)

    def _range(self, first, last):
        if not self.rvalue():
            return False
        self.code_gen.pop(first)
        if self.at_rvalue(False):
            if not self.rvalue():
                return False
            self.code_gen.pop(last)
            return True

        self.code_gen.add_instruction(OpCode.MOVEQ, None, last)
        return True

    def _block_operand(self) -> bool:
        if self.context.in_matrix():
            return self.token_error("Nesting not allowed here.")
        self.context.enter_matrix()
        if not self.parser.command_seq():
            return False
        self.context.exit_matrix()
        return True

    def _inline_operand(self) -> bool:
        self.code_gen.add_instruction(
            OpCode.MOVEQ, Operand.MATRIX, Register.OPERAND)

        has_rows = has_columns = False
        while self.current_token.is_any(TokenTypes.ROW, TokenTypes.COLUMN):
            if self.current_token.is_a(TokenTypes.ROW):
                if not self._rows(has_rows):
                    return False
                has_rows = True
            elif self.current_token.is_a(TokenTypes.COLUMN):
                if not self._columns(has_columns):
                    return False
                has_columns = True

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
