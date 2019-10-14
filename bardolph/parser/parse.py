#!/usr/bin/env python

import argparse
import logging
import re

from ..controller.instruction import Instruction, OpCode, Operand
from ..controller.units import UnitMode, Units
from . import lex
from .token_types import TokenTypes


WORD_REGEX = re.compile(r"\w+")


class Parser:
    def __init__(self):
        self._lexer = None
        self._error_output = ''
        self._light_state = {}
        self._name = None
        self._current_token_type = None
        self._current_token = None
        self._op_code = OpCode.NOP
        self._symbol_table = {}
        self._code = []
        self._unit_mode = UnitMode.LOGICAL

    def parse(self, input_string):
        self._code.clear()
        self._error_output = ''
        self._lexer = lex.Lex(input_string)
        self._next_token()
        success = self._script()
        self._lexer = None
        if not success:
            return None
        self._optimize()
        return self._code

    def load(self, file_name):
        logging.debug('File name: {}'.format(file_name))
        try:
            srce = open(file_name, 'r')
            input_string = srce.read()
            srce.close()
            return self.parse(input_string)
        except FileNotFoundError:
            logging.error('Error: file {} not found.'.format(file_name))
        except OSError:
            logging.error('Error accessing file {}'.format(file_name))

    def get_errors(self):
        return self._error_output

    def _script(self):
        return self._body() and self._eof()

    def _body(self):
        succeeded = True
        while succeeded and self._current_token_type != TokenTypes.EOF:
            succeeded = self._command()
        return succeeded

    def _eof(self):
        if self._current_token_type != TokenTypes.EOF:
            return self._trigger_error("Didn't get to end of file.")
        return True

    def _command(self):
        return {
            TokenTypes.BRIGHTNESS: self._set_reg,
            TokenTypes.DEFINE: self._definition,
            TokenTypes.DURATION: self._set_reg,
            TokenTypes.GET: self._get,
            TokenTypes.HUE: self._set_reg,
            TokenTypes.KELVIN: self._set_reg,
            TokenTypes.OFF: self._power_off,
            TokenTypes.ON: self._power_on,
            TokenTypes.PAUSE: self._pause,
            TokenTypes.SATURATION: self._set_reg,
            TokenTypes.SET: self._set,
            TokenTypes.TIME: self._set_reg,
            TokenTypes.UNITS: self._set_units,
        }.get(self._current_token_type, self._syntax_error)()

    def _set_reg(self):
        self._name = self._current_token
        reg = self._current_token_type
        self._next_token()

        if self._current_token_type == TokenTypes.NUMBER:
            try:
                value = round(float(self._current_token))
            except ValueError:
                return self._token_error('Invalid number: "{}"')
        elif self._current_token_type == TokenTypes.LITERAL:
            value = self._current_token
        elif self._current_token in self._symbol_table:
            value = self._symbol_table[self._current_token]
        else:
            return self._token_error('Unknown parameter value: "{}"')

        units = Units()
        if self._unit_mode == UnitMode.LOGICAL:
            value = units.as_raw(reg, value)
            if units.has_range(reg):
                (min_val, max_val) = units.get_range(reg)
                if value < min_val or value > max_val:
                    if self._unit_mode == UnitMode.LOGICAL:
                        min_val = units.as_logical(reg, min_val)
                        max_val = units.as_logical(reg, max_val)
                    return self._trigger_error(
                        '{} must be between {} and {}'.format(
                            reg.name.lower(), min_val, max_val))

        self._add_instruction(OpCode.SET_REG, self._name, value)
        return self._next_token()

    def _set_units(self):
        self._next_token()
        mode = {
            TokenTypes.RAW: UnitMode.RAW,
            TokenTypes.LOGICAL:UnitMode.LOGICAL
        }.get(self._current_token_type, None)

        if mode is None:
            return self._trigger_error(
                'Invalid parameter "{}" for units.'.format(self._current_token))

        self._unit_mode = mode
        return self._next_token()

    def _set(self):
        return self._action(OpCode.COLOR)

    def _get(self):
        return self._action(OpCode.GET_COLOR)

    def _power_on(self):
        self._add_instruction(OpCode.SET_REG, 'power', True)
        return self._action(OpCode.POWER)

    def _power_off(self):
        self._add_instruction(OpCode.SET_REG, 'power', False)
        return self._action(OpCode.POWER)

    def _pause(self):
        self._add_instruction(OpCode.PAUSE)
        self._next_token()
        return True

    def _action(self, op_code):
        self._op_code = op_code
        self._next_token()

        if self._current_token_type == TokenTypes.GROUP:
            self._add_instruction(OpCode.SET_REG, 'operand', Operand.GROUP)
            self._next_token()
        elif self._current_token_type == TokenTypes.LOCATION:
            self._add_instruction(OpCode.SET_REG, 'operand', Operand.LOCATION)
            self._next_token()
        else:
            self._add_instruction(OpCode.SET_REG, 'operand', Operand.LIGHT)

        return self._operand_list()

    def _operand_list(self):
        if self._current_token_type == TokenTypes.ALL:
            self._add_instruction(OpCode.SET_REG, 'name', None)
            self._add_instruction(OpCode.SET_REG, 'operand', Operand.ALL)
            if self._op_code != OpCode.GET_COLOR:
                self._add_instruction(OpCode.TIME_WAIT)
            self._add_instruction(self._op_code)
            return self._next_token()

        if not self._operand_name():
            return False

        self._add_instruction(OpCode.SET_REG, 'name', self._name)
        if self._op_code != OpCode.GET_COLOR:
            self._add_instruction(OpCode.TIME_WAIT)
        self._add_instruction(self._op_code)
        while self._current_token_type == TokenTypes.AND:
            if not self._and():
                return False
        return True

    def _operand_name(self):
        if self._current_token_type == TokenTypes.LITERAL:
            self._name = self._current_token
        elif self._current_token in self._symbol_table:
            self._name = self._symbol_table[self._current_token]
        else:
            return self._token_error('Unknown variable: {}')
        return self._next_token()

    def _and(self):
        self._next_token()
        if not self._operand_name():
            return False
        self._add_instruction(OpCode.SET_REG, 'name', self._name)
        self._add_instruction(self._op_code)
        return True

    def _definition(self):
        self._next_token()
        if self._current_token_type in [
                TokenTypes.LITERAL, TokenTypes.NUMBER]:
            return self._token_error('Unexpected literal: {}')

        var_name = self._current_token
        self._next_token()
        if self._current_token_type == TokenTypes.NUMBER:
            value = int(self._current_token)
        elif self._current_token_type == TokenTypes.LITERAL:
            value = self._current_token
        elif self._current_token in self._symbol_table:
            value = self._symbol_table[self._current_token]
        else:
            return self._token_error('Unknown term: "{}"')

        self._symbol_table[var_name] = value
        self._next_token()
        return True

    def _add_instruction(self, op_code, name=None, param=None):
        self._code.append(Instruction(op_code, name, param))

    def _add_message(self, message):
        self._error_output += '{}\n'.format(message)

    def _trigger_error(self, message):
        full_message = 'Line {}: {}'.format(
            self._lexer.get_line_number(), message)
        logging.error(full_message)
        self._add_message(full_message)
        return False

    def _token_error(self, message_format):
        return self._trigger_error(message_format.format(self._current_token))

    def _next_token(self):
        (self._current_token_type,
         self._current_token) = self._lexer.next_token()
        return True

    def _syntax_error(self):
        return self._token_error('Unexpected input "{}"')

    def _optimize(self):
        """
        Eliminate an instruction if it would _set a register to the same value
        that was assigned to it in the previous SET_REG instruction.

        Any GET_COLOR instruction clears out the previous value cache.
        """
        opt = []
        prev_value = {}
        for inst in self._code:
            if inst.op_code == OpCode.GET_COLOR:
                prev_value = {}
            if inst.op_code != OpCode.SET_REG:
                opt.append(inst)
            else:
                if inst.name not in prev_value or (
                        prev_value[inst.name] != inst.param):
                    opt.append(inst)
                    prev_value[inst.name] = inst.param
        self._code = opt


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('file', help='name of the script file')
    args = arg_parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(filename)s(%(lineno)d) %(funcName)s(): %(message)s')
    parser = Parser()
    output_code = parser.load(args.file)
    if output_code:
        for inst in output_code:
            print(inst)
    else:
        print(parser.get_errors())


if __name__ == '__main__':
    main()

"""
    <script> ::= <body> <EOF>
    <body> ::= <command> *
    <command> ::=
        "brightness" <set_reg>
        | "define" <definition>
        | "duration" <set_reg>
        | "hue" <set_reg>
        | "kelvin" <set_reg>
        | "off" <power_off>
        | "on" <power_on>
        | "_pause" <pause>
        | "saturation" <set_reg>
        | "_set" <set>
        | "units" <set_units>
        | "time" <set_reg>
    <set_reg> ::= <name> <number> | <name> <literal> | <name> <symbol>
    <set> ::= <action>
    <get> ::= <action>
    <power_off> ::= <action>
    <power_on> ::= <action>
    <action> ::= <op_code> <operand_list>
    <operand_list> ::= "all" | <operand_name> | <operand_name> <and> *
    <operand_name> ::= <token>
    <and> ::= "and" <operand_name>
    <definition> ::= <token> <number> | <token> <literal>
    <literal> ::= "\"" <token> "\""
"""
