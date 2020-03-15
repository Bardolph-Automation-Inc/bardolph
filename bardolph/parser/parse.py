#!/usr/bin/env python

import argparse
import logging

from bardolph.controller.routine import Routine
from bardolph.controller.units import UnitMode
from bardolph.lib.symbol_table import SymbolType
from bardolph.lib.time_pattern import TimePattern
from bardolph.vm.vm_codes import OpCode, Operand, Register, SetOp

from . import lex
from .call_context import CallContext
from .code_gen import CodeGen
from .lex import Lex
from .expr_parser import ExprParser
from .token_types import TokenTypes


class Parser:
    def __init__(self):
        self._lexer = None
        self._error_output = ''
        self._call_context = CallContext()
        self._current_token_type = None
        self._current_token = None
        self._op_code = OpCode.NOP
        self._code_gen = CodeGen()
        self._command_map = {
            TokenTypes.ASSIGN: self._assignment,
            TokenTypes.BREAKPOINT: self._breakpoint,
            TokenTypes.DEFINE: self._definition,
            TokenTypes.GET: self._get,
            TokenTypes.NAME: self._call_routine,
            TokenTypes.OFF: self._power_off,
            TokenTypes.ON: self._power_on,
            TokenTypes.PAUSE: self._pause,
            TokenTypes.REGISTER: self._set_reg,
            TokenTypes.REPEAT: self._repeat,
            TokenTypes.SET: self._set,
            TokenTypes.UNITS: self._set_units,
            TokenTypes.WAIT: self._wait
        }
        self._token_trace = False

    def parse(self, input_string, skip_optimize=False):
        self._call_context.clear()
        self._code_gen.clear()
        self._error_output = ''
        self._lexer = lex.Lex(input_string)
        self._next_token()
        success = self._script()
        self._lexer = None
        if success:
            if not skip_optimize:
                self._code_gen.optimize()
            return self._code_gen.program
        return None

    def load(self, file_name, skip_optimize=False):
        logging.debug('File name: {}'.format(file_name))
        try:
            srce = open(file_name, 'r')
            input_string = srce.read()
            srce.close()
            return self.parse(input_string, skip_optimize)
        except FileNotFoundError:
            logging.error('Error: file {} not found.'.format(file_name))
        except OSError:
            logging.error('Error accessing file {}'.format(file_name))

    def get_errors(self) -> str:
        return self._error_output

    def _script(self) -> bool:
        return self._body() and self._eof()

    def _body(self) -> bool:
        while self._current_token_type != TokenTypes.EOF:
            if not self._command():
                return False
        return True

    def _eof(self) -> bool:
        if self._current_token_type != TokenTypes.EOF:
            return self._trigger_error("Didn't get to end of file.")
        return True

    def _command(self) -> bool:
        return self._command_map.get(
            self._current_token_type, self._syntax_error)()

    def _set_reg(self):
        reg = Register.from_string(self._current_token)
        if reg is None:
            return self._token_error('Expected register, got "{}"')
        if reg == Register.TIME:
            return self._time()

        self._next_token()
        if self._current_token_type == TokenTypes.LITERAL_STRING:
            return self._string_to_reg(reg)
        return self._rvalue(reg)

    def _string_to_reg(self, reg) -> bool:
        if reg != Register.NAME:
            return self._trigger_error('Quoted value not allowed here.')
        self._add_instruction(OpCode.MOVEQ, self._current_token, reg)
        return self._next_token()

    def _set(self):
        return self._action(OpCode.COLOR)

    def _power_on(self):
        self._add_instruction(OpCode.MOVEQ, True, Register.POWER)
        return self._action(OpCode.POWER)

    def _power_off(self) -> bool:
        self._add_instruction(OpCode.MOVEQ, False, Register.POWER)
        return self._action(OpCode.POWER)

    def _action(self, op_code) -> bool:
        """ op_code: COLOR or POWER """
        self._op_code = op_code
        self._add_instruction(OpCode.WAIT)
        self._next_token()
        if self._current_token_type == TokenTypes.ALL:
            return self._all_operand()
        return self._operand_list()

    def _all_operand(self) -> bool:
        self._add_instruction(OpCode.MOVEQ, None, Register.NAME)
        self._add_instruction(OpCode.MOVEQ, Operand.ALL, Register.OPERAND)
        self._add_instruction(self._op_code)
        return self._next_token()

    def _operand_list(self) -> bool:
        """ For every operand in the list, issue the instruction in
        self._op_code. """
        if not self._operand():
            return False
        self._add_instruction(self._op_code)

        while self._current_token_type == TokenTypes.AND:
            self._next_token()
            if not self._operand():
                return False
            self._add_instruction(self._op_code)
        return True

    def _operand(self) -> bool:
        """
        Process a group, location, or light with an optional set of
        zones. Do this by populating the NAME and OPERAND registers.

        An operand is either a literal string, or a varible/macro containing
        a string. It gets put into the name register.
        """
        if self._current_token_type == TokenTypes.GROUP:
            operand = Operand.GROUP
            self._next_token()
        elif self._current_token_type == TokenTypes.LOCATION:
            operand = Operand.LOCATION
            self._next_token()
        else:
            operand = Operand.LIGHT

        const_str = self._current_str()
        if const_str is not None:
            self._add_instruction(OpCode.MOVEQ, const_str, Register.NAME)
            self._next_token()
        elif self._current_token_type == TokenTypes.NAME:
            if not self._var_operand():
                return False
        else:
            return self._token_error('Needed a light, got "{}".')

        if self._current_token_type == TokenTypes.ZONE:
            if not self._zone_range():
                return False
            operand = Operand.MZ_LIGHT

        self._add_instruction(OpCode.MOVEQ, operand, Register.OPERAND)
        return True

    def _var_operand(self) -> bool:
        if not self._call_context.has_symbol_typed(
                self._current_token, SymbolType.VAR):
            return self._token_error('Not a variable: "{}"')
        self._add_instruction(OpCode.MOVE, self._current_token, Register.NAME)
        return self._next_token()

    def _zone_range(self) -> bool:
        if self._op_code != OpCode.COLOR:
            return self._trigger_error('Zones not supported for {}'.format(
                self._op_code.name.tolower()))
        self._next_token()
        return self._set_zones()

    def _set_zones(self, only_one=False):
        """
        Parses out one or two zone numbers. Generates instructions
        that populate the FIRST_ZONE and LAST_ZONE registers. If only one
        parameter is present, put None into LAST_ZONE.
        """
        if not self._at_rvalue():
            return self._token_error('Expected zone, got "{}"')
        if not self._rvalue(Register.FIRST_ZONE):
            return False
        if not only_one and self._at_rvalue():
            return self._rvalue(Register.LAST_ZONE)

        self._add_instruction(OpCode.MOVEQ, None, Register.LAST_ZONE)
        return True

    def _set_units(self) -> bool:
        self._next_token()
        mode = {
            TokenTypes.RAW: UnitMode.RAW,
            TokenTypes.LOGICAL: UnitMode.LOGICAL
        }.get(self._current_token_type, None)

        if mode is None:
            return self._trigger_error(
                'Invalid parameter "{}" for units.'.format(self._current_token))

        self._add_instruction(OpCode.MOVEQ, mode, Register.UNIT_MODE)
        return self._next_token()

    def _wait(self) -> bool:
        self._add_instruction(OpCode.WAIT)
        return self._next_token()

    def _get(self) -> bool:
        self._next_token()
        if not self._at_rvalue():
            return self._token_error('Needed light for get, got "{}".')
        if not self._rvalue(Register.NAME):
            return False

        operand = Operand.LIGHT
        if self._current_token_type == TokenTypes.ZONE:
            operand = Operand.MZ_LIGHT
            self._next_token()
            if not self._set_zones(True):
                return False

        self._add_instruction(OpCode.MOVEQ, operand, Register.OPERAND)
        self._add_instruction(OpCode.GET_COLOR)
        return True

    def _pause(self):
        self._add_instruction(OpCode.PAUSE)
        self._next_token()
        return True

    def _time(self):
        self._next_token()
        if self._current_token_type == TokenTypes.AT:
            return self._process_time_patterns()
        return self._rvalue(Register.TIME)

    def _process_time_patterns(self):
        time_pattern = self._current_time_pattern()
        if time_pattern is None:
            return self._time_spec_error()
        self._add_instruction(
            OpCode.TIME_PATTERN, SetOp.INIT, time_pattern)
        self._next_token()

        while self._current_token_type == TokenTypes.OR:
            self._next_token()
            time_pattern = self._current_time_pattern()
            if time_pattern is None:
                return self._time_spec_error()
            self._add_instruction(
                OpCode.TIME_PATTERN, SetOp.UNION, time_pattern)
            self._next_token()

        return True

    def _assignment(self) -> bool:
        self._next_token()
        if self._current_token_type != TokenTypes.NAME:
            return self._token_error('Expected name for assignment, got "{}"')

        dest_name = self._current_token
        self._next_token()
        if not self._rvalue(dest_name):
            return False
        self._call_context.add_variable(dest_name)
        return True

    def _rvalue(self, dest=Register.RESULT) -> bool:
        """
        Consume an rvalue. If dest is a Register value, the generated code
        will put the results of its calculations into that register. If dest
        contains a string, the results go into a variable of that name in
        the current context.
        """
        const_value = self._current_constant()
        if const_value is not None:
            self._add_instruction(OpCode.MOVEQ, const_value, dest)
            self._call_context.add_global(dest, SymbolType.MACRO, const_value)
            return self._next_token()
        if self._current_token_type == TokenTypes.NAME:
            name = self._current_token
            if self._call_context.has_symbol_typed(name, SymbolType.VAR):
                self._add_instruction(OpCode.MOVE, name, dest)
                return self._next_token()
        if self._current_token_type == TokenTypes.EXPRESSION:
            parser = ExprParser(self._current_token)
            if not parser.generate_code(self._code_gen):
                return self._token_error('Error parsing expression "{}"')
            self._add_instruction(OpCode.POP, dest)
            return self._next_token()
        if self._current_token_type != TokenTypes.REGISTER:
            return self._token_error('Cannot use {} as a value.')
        self._add_instruction(OpCode.MOVE, self._current_reg(), dest)
        return self._next_token()

    def _at_rvalue(self) -> bool:
        return self._current_token_type in (
            TokenTypes.EXPRESSION,
            TokenTypes.LITERAL_STRING,
            TokenTypes.NAME,
            TokenTypes.NUMBER)

    def _definition(self) -> bool:
        self._next_token()
        if self._current_token_type != TokenTypes.NAME:
            return self._token_error('Expected name for definition, got: {}')
        name = self._current_token

        self._next_token()
        if self._detect_routine_start():
            if self._call_context.get_routine(name) is not None:
                return self._token_error('Already defined: "{}"')
            return self._routine_definition(name)

        return self._macro_definition(name)

    def _detect_routine_start(self) -> bool:
        """
        If a definition is followed by "with", "begin", a keyword corresponding
        to a command, or the name of an existing routine, it's defining a new
        routine and not a variable.
        """
        if self._call_context.get_routine(self._current_token) is not None:
            return True
        return self._current_token_type in (
            TokenTypes.BEGIN, TokenTypes.WITH,
            TokenTypes.REGISTER, TokenTypes.SET)

    def _macro_definition(self, name):
        """
        Process a "define" where an alias for a value is being created. This
        symbol exists at compile time. This means a define cannot refer to a
        parameter in a routine. The symbol has global scope, even if it is
        defined inside a routine.
        """
        value = self._current_literal()
        if value is None:
            value = self._call_context.get_macro(self._current_token)
        if value is None:
            return self._token_error('Macro needs constant, got "{}"')
        self._call_context.add_global(name, SymbolType.MACRO, value)
        self._add_instruction(OpCode.CONSTANT, name, value)
        return self._next_token()

    def _routine_definition(self, name):
        if self._call_context.in_routine():
            return self._trigger_error('Nested definition not allowed.')

        self._call_context.enter_routine()
        self._call_context.push()
        self._add_instruction(OpCode.ROUTINE, name)

        routine = Routine(name)
        self._call_context.add_routine(routine)
        if self._current_token_type == TokenTypes.WITH:
            self._next_token()
            if not self._param_decl(routine):
                return False
        if self._current_token_type == TokenTypes.BEGIN:
            self._next_token()
            result = self._compound_proc()
        else:
            result = self._command()

        self._call_context.pop()
        self._add_instruction(OpCode.END, name)

        self._call_context.exit_routine()
        return result

    def _param_decl(self, routine):
        """
        The parameter declarations for the routine are not included in the
        generated code. Declarations are used only at compile time.
        """
        name = self._current_token
        routine.add_param(name)
        self._call_context.add_variable(name)
        self._next_token()
        while self._current_token_type == TokenTypes.AND:
            self._next_token()
            name = self._current_token
            if routine.has_param(name):
                self._token_error('Duplicate parameter name: "{}"')
                return None
            routine.add_param(name)
            self._call_context.add_variable(name)
            self._next_token()
        return True

    def _compound_proc(self):
        while self._current_token_type != TokenTypes.END:
            if self._current_token_type == TokenTypes.EOF:
                return self._trigger_error('End of file before "end".')
            if not self._command():
                return False
        return self._next_token()

    def _call_routine(self):
        routine = self._call_context.get_routine(self._current_token)
        if routine is None:
            return self._token_error('Unknown name: "{}"')

        self._next_token()
        for param_name in routine.params:
            if not self._rvalue():
                return False
            self._add_instruction(OpCode.PARAM, param_name, Register.RESULT)

        self._add_instruction(OpCode.JSR, routine.name)
        return True

    def _repeat(self) -> bool:
        """ Unconditional, therefore infinite. """
        self._add_instruction(OpCode.LOOP)
        self._next_token()
        if self._current_token_type == TokenTypes.BEGIN:
            self._next_token()
            if not self._compound_proc():
                return False
        elif not self._command():
            return False
        self._add_instruction(OpCode.END)
        return True

    def _add_instruction(self, op_code, param0=None, param1=None):
        return self._code_gen.add_instruction(op_code, param0, param1)

    def _add_message(self, message):
        self._error_output += '{}\n'.format(message)

    def _trigger_error(self, message):
        full_message = 'Line {}: {}'.format(
            self._lexer.get_line_number(), message)
        self._add_message(full_message)
        return False

    def _current_literal(self):
        """
        Interpret the current token as a literal and return its value.
        If the current token doesn't contain a literal, return None.
        """
        value = None
        if self._current_token_type == TokenTypes.NUMBER:
            if Lex.INT_REGEX.match(self._current_token):
                value = int(self._current_token)
            else:
                value = float(self._current_token)
        elif self._current_token_type == TokenTypes.LITERAL_STRING:
            value = self._current_token
        elif self._current_token_type == TokenTypes.TIME_PATTERN:
            value = TimePattern.from_string(self._current_token)
            if value is None:
                self._time_spec_error()
        return value

    def _current_constant(self):
        """
        Interpret the current token as either a literal or macro, and return
        its value, which is known at compile time. If the token is an undefined
        name, return None.
        """
        value = self._current_literal()
        if value is not None:
            return value
        if self._current_token_type != TokenTypes.NAME:
            return None
        return self._call_context.get_macro(self._current_token)

    def _current_int(self):
        value = self._current_constant()
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return round(value)
        return None

    def _current_float(self):
        value = self._current_constant()
        if isinstance(value, float):
            return value
        if isinstance(value, int):
            return float(value)
        return None

    def _current_str(self):
        value = self._current_constant()
        return value if isinstance(value, str) else None

    def _current_time_pattern(self) -> TimePattern:
        """
        Returns the current token as a time pattern. If the current token
        isn't a time pattern or Symbol, returns None.

        Only literals or macros. Can't yet pass a time pattern as a
        parameter to a routine.
        """
        if self._current_token_type == TokenTypes.TIME_PATTERN:
            return TimePattern.from_string(self._current_token)
        if self._current_token_type == TokenTypes.NAME:
            return self._call_context.get_macro(self._current_token)
        return None

    def _current_reg(self):
        if self._current_token_type != TokenTypes.REGISTER:
            return None
        return Register.from_string(self._current_token)

    def _next_token(self):
        (self._current_token_type,
         self._current_token) = self._lexer.next_token()
        if self._token_trace:
            logging.info(
                'Next token: "{}" ({})'.format(
                    self._current_token, self._current_token_type))
        return True

    def _breakpoint(self):
        self._code_gen.add_instruction(OpCode.BREAKPOINT)

    def _token_error(self, message_format):
        return self._trigger_error(message_format.format(self._current_token))

    def _unimplementd(self):
        return self._token_error('Unimplemented at token "{}"')

    def _syntax_error(self):
        return self._token_error('Unexpected input "{}"')

    def _time_spec_error(self):
        return self._token_error('Invalid time specification: "{}"')


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('file', help='name of the script file')
    arg_parser.add_argument(
        '-u', '--unoptimized', help='disable optimization', action='store_true')
    args = arg_parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(filename)s(%(lineno)d) %(funcName)s(): %(message)s')
    parser = Parser()
    output_code = parser.load(args.file, args.unoptimized)
    if output_code:
        for inst in output_code:
            print(inst)
    else:
        print("Error parsing: {}".format(parser.get_errors()))


if __name__ == '__main__':
    main()

"""
    <script> ::= <body> <EOF>
    <body> ::= <command> *
    <command> ::=
        "brightness" <set_reg>
        | "define" <definition>
        | "duration" <set_reg>
        | "get" <name>
        | "hue" <set_reg>
        | "kelvin" <set_reg>
        | "off" <operand_list>
        | "on" <operand_list>
        | "pause" <pause>
        | "saturation" <set_reg>
        | "set" <operand_list>
        | "units" <set_units>
        | "time" <time_spec>
        | "wait"
    <set_reg> ::= <name> <number_param> | <name> <literal> | <name> <symbol>
    <number_param> ::= <number> | <name>
    <operand_list> ::= <operand> | <operand> <and> *
    <operand> ::= <light> | "group" <name> | "location" <name>
    <light> ::= <name> | <name> <zone_list>
    <zone_list> ::= "zone" <zone_range>
    <zone_range> ::= <number> | <number> <number>
    <name> ::= <literal> | <token>
    <set_units> ::= "logical" | "raw"
    <time_spec> ::= <number> | <time_pattern_set>
    <time_pattern_set> ::= <time_pattern> | <time_pattern> "or" <time_pattern>
    <time_pattern> ::= <hour_pattern> ":" <minute_pattern>
    <hour_pattern> ::= <digit> | <digit> <digit> | "*" <digit> |
                        <digit> "*" | "*"
    <minute_pattern> ::= <digit> <digit> | <digit> "*" | "*" <digit> | "*"
    <and> ::= "and" <operand_name>
    <definition> ::= <token> <number> | <token> <literal> | <code_definition>
    <code_definition> ::= "with" <parameter_decl> <code_block> | <code_block>
    <parameter_decl> ::= <formal_parameter> | <formal_parameter> <and> <parameter_decl>
    <formal_parameter> ::= <name>
    <code_block> ::= "begin" <code_sequence> "end" | <command>
    <code_sequence> ::= <command> *
    <literal> ::= "\"" (text) "\""
"""
