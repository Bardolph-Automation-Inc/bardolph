#!/usr/bin/env python

import argparse
import logging

from ..controller.instruction import Instruction, OpCode, Operand
from ..controller.instruction import Register, SetOp
from ..controller.units import UnitMode, Units
from . import lex
from ..lib.time_pattern import TimePattern
from .token_types import TokenTypes


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
            TokenTypes.DEFINE: self._definition,
            TokenTypes.GET: self._get,
            TokenTypes.OFF: self._power_off,
            TokenTypes.ON: self._power_on,
            TokenTypes.PAUSE: self._pause,
            TokenTypes.REGISTER: self._set_reg,
            TokenTypes.SET: self._set,
            TokenTypes.UNITS: self._set_units,
        }.get(self._current_token_type, self._syntax_error)()

    def _set_reg(self):
        self._name = self._current_token
        register = Register[self._name.upper()]
        if register == Register.TIME:
            return self._time()
        if register == Register.DURATION:
            return self._duration()
                
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
        
        self._add_reg_instruction(register, value)
        return self._next_token()

    def _add_reg_instruction(self, reg, value):
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
        self._add_instruction(OpCode.SET_REG, reg, value)

    def _set_units(self):
        self._next_token()
        mode = {
            TokenTypes.RAW: UnitMode.RAW,
            TokenTypes.LOGICAL: UnitMode.LOGICAL
        }.get(self._current_token_type, None)

        if mode is None:
            return self._trigger_error(
                'Invalid parameter "{}" for units.'.format(self._current_token))

        self._unit_mode = mode
        return self._next_token()

    def _set(self):
        return self._action(OpCode.COLOR)

    def _get(self):
        self._next_token()
        if self._current_token_type == TokenTypes.LITERAL:
            self._name = self._current_token
        elif self._current_token in self._symbol_table:
            self._name = self._symbol_table[self._current_token]
        else:
            return self._token_error('Needed light or zone for "get", got {}.')
        
        self._next_token()
        if self._current_token_type == TokenTypes.ZONE:
            operand = Operand.MZ_LIGHT
            self._next_token()
            if self._current_token_type != TokenTypes.NUMBER:
                return self._token_error('Expected zone number, got "{}"')
            self._add_instruction(
                OpCode.SET_REG, Register.ZONES, (self._current_int(), None))
            self._next_token()
        else:
            operand = Operand.LIGHT

        self._add_instruction(OpCode.SET_REG, Register.NAME, self._name)
        self._add_instruction(OpCode.SET_REG, Register.OPERAND, operand)
        self._add_instruction(OpCode.GET_COLOR)
        return True

    def _power_on(self):
        self._add_instruction(OpCode.SET_REG, Register.POWER, True)
        return self._action(OpCode.POWER)

    def _power_off(self):
        self._add_instruction(OpCode.SET_REG, Register.POWER, False)
        return self._action(OpCode.POWER)

    def _pause(self):
        self._add_instruction(OpCode.PAUSE)
        self._next_token()
        return True
    
    def _time(self):
        self._next_token()
        if self._current_token_type == TokenTypes.AT:
            return self._process_time_patterns()

        if self._current_token_type == TokenTypes.NUMBER:
            value = self._normalized_time()
        elif self._current_token in self._symbol_table:
            value = self._normalized_time(
                self._symbol_table[self._current_token])
        else:
            return self._time_spec_error()
        self._add_reg_instruction(Register.TIME, value)
        return self._next_token()
        
    def _duration(self):
        self._next_token()
        if self._current_token_type == TokenTypes.NUMBER:
            value = self._normalized_time()
        elif self._current_token in self._symbol_table:
            value = self._normalized_time(
                self._symbol_table[self._current_token])
        else:
            return self._token_error("Expected number for duration, got {}.")
        self._add_reg_instruction(Register.DURATION, value)
        return self._next_token()
        
    def _process_time_patterns(self):
        time_pattern = self._next_time_pattern()
        if time_pattern is None:
            return self._time_spec_error()
        self._add_instruction(
            OpCode.TIME_PATTERN, SetOp.INIT, time_pattern)
        self._next_token()

        while self._current_token_type == TokenTypes.OR:
            time_pattern = self._next_time_pattern()
            if time_pattern is None:
                return self._time_spec_error()  
            self._add_instruction(
                OpCode.TIME_PATTERN, SetOp.UNION, time_pattern)
            self._next_token()

        return True;

    def _next_time_pattern(self):
        self._next_token()
        if self._current_token_type == TokenTypes.TIME_PATTERN:
            pattern_string = self._current_token
        else:
            pattern_string = self._symbol_table.get(self._current_token, None)
        if pattern_string is None:
            return None
        time_pattern = TimePattern.from_string(pattern_string)
        return time_pattern  
    
    def _action(self, op_code):
        """ op_code: COLOR, GET_COLOR, or POWER """
        self._op_code = op_code
        if self._op_code != OpCode.GET_COLOR:
            self._add_instruction(OpCode.TIME_WAIT)

        self._next_token()
        if self._current_token_type == TokenTypes.ALL:
            return self._all_operand()
        return self._operand_list()
    
    def _all_operand(self):
        self._add_instruction(OpCode.SET_REG, Register.NAME, None)
        self._add_instruction(OpCode.SET_REG, Register.OPERAND, Operand.ALL)
        self._add_instruction(self._op_code)
        return self._next_token()

    def _operand_list(self):
        if not self._operand():
            return self._syntax_error()

        self._add_instruction(self._op_code)
                
        while self._current_token_type == TokenTypes.AND:
            self._next_token()
            if not self._operand():
                return False
            self._add_instruction(self._op_code)
        return True
    
    def _operand(self):
        """ A group, location, or light with an optional set of zones. """
        if self._current_token_type == TokenTypes.GROUP:
            operand = Operand.GROUP
            self._next_token()
        elif self._current_token_type == TokenTypes.LOCATION:
            operand = Operand.LOCATION
            self._next_token()
        else:
            operand = Operand.LIGHT
            
        if self._current_token_type == TokenTypes.LITERAL:
            self._name = self._current_token
        elif self._current_token in self._symbol_table:
            self._name = self._symbol_table[self._current_token]
        else:
            return self._token_error('Unknown variable: {}')
        self._add_instruction(OpCode.SET_REG, Register.NAME, self._name)

        self._next_token()
        if self._current_token_type == TokenTypes.ZONE:
            if not self._zone_range():
                return False
            operand = Operand.MZ_LIGHT

        self._add_instruction(OpCode.SET_REG, Register.OPERAND, operand)
        return True

    def _zone_range(self):
        if self._op_code != OpCode.COLOR:
            return self._trigger_error('Zones not supported for {}'.format(
                self._op_code.name.tolower()))

        self._next_token()
        if self._current_token_type != TokenTypes.NUMBER:
            return self._token_error('Expected zone number, got "{}"')

        start_zone = self._current_int()
        self._next_token()

        if self._current_token_type == TokenTypes.NUMBER:
            end_zone = self._current_int()
            self._next_token()
        else:
            end_zone = start_zone + 1
            
        self._add_instruction(
            OpCode.SET_REG, Register.ZONES, (start_zone, end_zone))
        return True

    def _and(self):
        self._next_token()
        if not self._operand_name():
            return False
        self._add_instruction(OpCode.SET_REG, Register.NAME, self._name)
        self._add_instruction(self._op_code)
        return True

    def _definition(self):
        self._next_token()
        if self._current_token_type in [
                TokenTypes.LITERAL, TokenTypes.NUMBER, TokenTypes.TIME_PATTERN]:
            return self._token_error('Unexpected literal: {}')

        var_name = self._current_token
        self._next_token()
        if self._current_token_type == TokenTypes.NUMBER:
            value = int(self._current_token)
        elif self._current_token_type == TokenTypes.LITERAL:
            value = self._current_token
        elif self._current_token_type == TokenTypes.TIME_PATTERN:
            value = TimePattern.from_string(self._current_token)
            if value is None:
                return self._time_spec_error()
        elif self._current_token in self._symbol_table:
            value = self._symbol_table[self._current_token]
        else:
            return self._token_error('Unknown term: "{}"')

        self._symbol_table[var_name] = value
        self._next_token()
        return True

    def _add_instruction(self, op_code, param0=None, param1=None):
        self._code.append(Instruction(op_code, param0, param1))

    def _add_message(self, message):
        self._error_output += '{}\n'.format(message)

    def _trigger_error(self, message):
        full_message = 'Line {}: {}'.format(
            self._lexer.get_line_number(), message)
        logging.error(full_message)
        self._add_message(full_message)
        return False

    def _next_token(self):
        (self._current_token_type,
         self._current_token) = self._lexer.next_token()
        return True
    
    def _current_int(self):
        if self._current_token_type != TokenTypes.NUMBER:
            return None
        return round(float(self._current_token))

    def _token_error(self, message_format):
        return self._trigger_error(message_format.format(self._current_token))

    def _syntax_error(self):
        return self._token_error('Unexpected input "{}"')

    def _time_spec_error(self):
        return self._token_error('Invalid time specification: "{}"')  

    def _normalized_time(self, token=None):
        if token is None:
            token = self._current_token
        if self._unit_mode == UnitMode.LOGICAL:
            value = round(float(token) * 1000.0)
        else:
            value = int(token)            
        return value
    
    def _optimize(self):
        """
        Eliminate SET_REG if it has the same value as the previous SET_REG
        instruction.
        
        For this instruction, param0 is the name of the register, and param1 is
        the value to which the register is set.

        Any GET_COLOR instruction clears out the previous value cache.
        """
        opt = []
        prev_value = {}
        for inst in self._code:
            if inst.op_code == OpCode.GET_COLOR:
                prev_value = {}
                opt.append(inst)
            if inst.op_code != OpCode.SET_REG:
                opt.append(inst)
            else:
                key = str(inst.param0)
                if key not in prev_value or prev_value[key] != inst.param1:
                    opt.append(inst)
                    prev_value[key] = inst.param1
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
        | "time" <time_spec>
    <set_reg> ::= <name> <number> | <name> <literal> | <name> <symbol>
    <set> ::= <action>
    <set_units> ::= "logical" | "raw"
    <get> ::= <action>
    <power_off> ::= <action>
    <power_on> ::= <action>
    <time_spec> ::= <number> | <time_pattern_set>
    <time_pattern_set> ::= <time_pattern> | <time_pattern> "or" <time_pattern>
    <time_pattern> ::= <hour_pattern> ":" <minute_pattern>
    <hour_pattern> ::= <digit> | <digit><digit> | "*" <digit> |
                        <digit> "*" | "*"
    <minute_pattern> ::= <digit><digit> | <digit> "*" | "*" <digit> | "*"
    <action> ::= <op_code> <operand_list> | <op_code> "all"
    <operand_list> ::= <operand> | <operand> <and> *
    <operand> ::= <name> | "group" <name> | "location" <name>
    <name> ::= <literal> | <token>
    <and> ::= "and" <operand_name>
    <definition> ::= <token> <number> | <token> <literal>
    <literal> ::= "\"" <token> "\""
"""
