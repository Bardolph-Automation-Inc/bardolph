#!/usr/bin/env python

import argparse
from enum import auto, Enum
import logging
import re

from ..controller.instruction import Instruction, OpCode, Operand
from . import lex
from .token_types import TokenTypes


word_regex = re.compile(r"\w+")
HSB_RANGE = (0.0, 65536.0)
KELVIN_RANGE = (2500.0, 9000.0)
RAW_RANGE = (0, 65536)


class UnitMode(Enum):
    LOGICAL = auto()
    RAW = auto()


class Parser:
    def __init__(self):
        self.lexer = None
        self.error_output = ''
        self.light_state = {}
        self.name = None
        self.current_token_type = None
        self.current_token = None
        self.op_code = OpCode.NOP
        self.symbol_table = {}
        self.code = []
        self.unit_mode = UnitMode.LOGICAL
        
    def parse(self, input_string):
        self.code.clear()
        self.error_output = ''
        self.lexer = lex.Lex(input_string)
        self.next_token()
        success = self.script()
        self.lexer = None
        if not success:
            return None
        self.optimize()
        return self.code

    def load(self, file_name):
        logging.debug('File name: {}'.format(file_name))
        try:
            f = open(file_name, 'r')
            input_string = f.read()
            f.close()
            return self.parse(input_string)
        except FileNotFoundError:
            logging.error('Error: file {} not found.'.format(file_name))
        except:
            logging.error('Error accessing file {}'.format(file_name))

    def script(self):
        return self.body() and self.eof()
        
    def body(self):
        succeeded = True
        while succeeded and self.current_token_type != TokenTypes.EOF:
            succeeded = self.command()
        return succeeded

    def eof(self):
        if self.current_token_type != TokenTypes.EOF:
            return self.trigger_error("Didn't get to end of file.")
        return True

    def command(self):
        fn = {
            TokenTypes.BRIGHTNESS: self.set_reg,
            TokenTypes.DEFINE: self.definition,
            TokenTypes.DURATION: self.set_reg,
            TokenTypes.GET: self.get,
            TokenTypes.HUE: self.set_reg,
            TokenTypes.KELVIN: self.set_reg,
            TokenTypes.OFF: self.power_off,
            TokenTypes.ON: self.power_on,
            TokenTypes.PAUSE: self.pause,
            TokenTypes.SATURATION: self.set_reg,
            TokenTypes.SET: self.set,
            TokenTypes.TIME: self.set_reg,
            TokenTypes.UNITS: self.set_units,
        }.get(self.current_token_type, self.syntax_error)
        return fn() if fn != None else True
        
    def set_reg(self):
        self.name = self.current_token
        reg = self.current_token_type
        self.next_token()

        if self.current_token_type == TokenTypes.NUMBER:
            try:
                value = round(float(self.current_token))
            except ValueError:
                return self.token_error('Invalid number: "{}"')
        elif self.current_token_type == TokenTypes.LITERAL:
            value = self.current_token
        elif self.current_token in self.symbol_table:
            value = self.symbol_table[self.current_token]
        else:
            return self.token_error('Unknown parameter value: "{}"')

        value = self.convert_units(reg, value)
        if value is None:
            return False
        
        self.add_instruction(OpCode.SET_REG, self.name, value)
        return self.next_token()
    
    def convert_units(self, reg, code_value):
        """If necessary, converts units to integer values that can be passed
        into the light API.
        
        With UnitMode.RAW, all parameters are passed through unmodified to the
        API.
        
        With UnitMode.LOGICAL, hue is an angle measured in degrees, while
        saturation and brightness are percentages. 
        
        In either case, kelvin is passed through unmodified.
        
        Args:
            reg: TokenType corresponding to the register being set.
            code_value: the numerical parameter as it appears in the script.
                Should be floating point, but int's should work.
            
        Returns:
            An integer containing the value that corresponds to the incoming
            value from the script, or None if the value is out of range.
        """
        value = code_value
        if self.unit_mode == UnitMode.RAW:
            (min_val, max_val) = RAW_RANGE
        else:
            if reg == TokenTypes.HUE:
                (min_val, max_val) = HSB_RANGE
                if code_value == 360.0 or code_value == 0:
                    value = 0.0;
                else:
                    value = round((code_value % 360.0) / 360.0 * 65535.0)
            elif reg in (TokenTypes.BRIGHTNESS, TokenTypes.SATURATION):
                (min_val, max_val) = HSB_RANGE
                if code_value == 100.0:
                    value = 65535.0
                else:
                    value = code_value / 100.0 * 65535.0
            elif reg in (TokenTypes.DURATION, TokenTypes.TIME):
                (min_val, max_val) = RAW_RANGE
            else:
                (min_val, max_val) = KELVIN_RANGE
        if value < min_val or value > max_val:
            self.trigger_error(
                "Invalid value {} for {}".format(code_value, self.name))
            return None
        return round(value)
    
    def set_units(self):
        self.next_token()
        mode = {
            TokenTypes.RAW: UnitMode.RAW,
            TokenTypes.LOGICAL:UnitMode.LOGICAL
        }.get(self.current_token_type, None)
    
        if mode is None:
            return self.trigger_error(
                'Invalid parameter "{}" for units.'.format(self.current_token))

        self.unit_mode = mode
        return self.next_token()

    def set(self):
        return self.action(OpCode.COLOR)
    
    def get(self):
        return self.action(OpCode.GET_COLOR)
    
    def power_on(self):
        self.add_instruction(OpCode.SET_REG, 'power', True)
        return self.action(OpCode.POWER)
        
    def power_off(self):
        self.add_instruction(OpCode.SET_REG, 'power', False)
        return self.action(OpCode.POWER)
    
    def pause(self):
        self.add_instruction(OpCode.PAUSE)
        self.next_token()
        return True
        
    def action(self, op_code):
        self.op_code = op_code
        self.next_token()

        if self.current_token_type == TokenTypes.GROUP:
            self.add_instruction(OpCode.SET_REG, 'operand', Operand.GROUP)
            self.next_token()
        elif self.current_token_type == TokenTypes.LOCATION:
            self.add_instruction(OpCode.SET_REG, 'operand', Operand.LOCATION)
            self.next_token()
        else:
            self.add_instruction(OpCode.SET_REG, 'operand', Operand.LIGHT)
        
        return self.operand_list()
    
    def operand_list(self):
        if self.current_token_type == TokenTypes.ALL:
            self.add_instruction(OpCode.SET_REG, 'name', None)
            if self.op_code != OpCode.GET_COLOR:
                self.add_instruction(OpCode.TIME_WAIT)
            self.add_instruction(self.op_code) 
            return self.next_token()
        
        if not self.operand_name():
            return False
        
        self.add_instruction(OpCode.SET_REG, 'name', self.name)
        if self.op_code != OpCode.GET_COLOR:
            self.add_instruction(OpCode.TIME_WAIT)
        self.add_instruction(self.op_code)
        while self.current_token_type == TokenTypes.AND:
            if not self.and_operand():
                return False
        return True
    
    def operand_name(self):
        if self.current_token_type == TokenTypes.LITERAL:
            self.name = self.current_token
        elif self.current_token in self.symbol_table:
            self.name = self.symbol_table[self.current_token]
        else:
            return self.token_error('Unknown variable: {}')
        return self.next_token()

    def and_operand(self):
        self.next_token()
        if not self.operand_name():
            return False
        self.add_instruction(OpCode.SET_REG, 'name', self.name)
        self.add_instruction(self.op_code)
        return True
           
    def definition(self):
        self.next_token()
        if self.current_token_type in [
                TokenTypes.LITERAL, TokenTypes.NUMBER]:
            return self.token_error('Unexpected literal: {}')
        
        var_name = self.current_token
        self.next_token()
        if self.current_token_type == TokenTypes.NUMBER:
            value = int(self.current_token)
        elif self.current_token_type == TokenTypes.LITERAL:
            value = self.current_token
        elif self.current_token in self.symbol_table:
            value = self.symbol_table[self.current_token]
        else:
            return self.token_error('Unknown term: "{}"')

        self.symbol_table[var_name] = value
        self.next_token()
        return True

    def add_instruction(self, op_code, name = None, param = None):
        self.code.append(Instruction(op_code, name, param))

    def get_errors(self):
        return self.error_output;
    
    def add_message(self, message):
        self.error_output += '{}\n'.format(message)
        
    def trigger_error(self, message):
        full_message = 'Line {}: {}'.format(self.lexer.line_num, message)
        logging.error(full_message)
        self.add_message(full_message)
        return False
    
    def token_error(self, message_format):
        return self.trigger_error(message_format.format(self.current_token))

    def next_token(self):
        (self.current_token_type, self.current_token) = self.lexer.next_token()
        return True
        
    def syntax_error(self):
        return self.token_error('Unexpected input "{}"')

    def optimize(self):
        """
        Eliminate an instruction if it would set a register to the same value
        that was assigned to it in the previous SET_REG instruction.
        
        Any GET_COLOR instruction clears out the previous value cache. 
        """
        opt = []
        prev_value = {}
        for inst in self.code:
            if inst.op_code == OpCode.GET_COLOR:
                prev_value = {}
            if inst.op_code != OpCode.SET_REG:
                opt.append(inst)
            else:
                if inst.name not in prev_value or (
                        prev_value[inst.name] != inst.param):
                    opt.append(inst)
                    prev_value[inst.name] = inst.param
        self.code = opt
                
                
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file', help='name of the script file')
    args = ap.parse_args()
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(filename)s(%(lineno)d) %(funcName)s(): %(message)s')
    parser = Parser()
    output_code = parser.load(args.file)
    if output_code:
        for inst in output_code:
            print(inst)
    else:
        print(parser.error_output)

    
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
        | "pause" <pause>
        | "saturation" <set_reg>
        | "set" <set>
        | "units" <set_units>
        | "time" <set_reg>
    <set_reg> ::= <name> <number> | <name> <literal> | <name> <symbol>
    <set> ::= <action>
    <get> ::= <action>
    <power_off> ::= <action>
    <power_on> ::= <action>
    <action> ::= <op_code> <operand_list>
    <operand_list> ::= "all" | <operand_name> | <operand_name> <and_operand> *
    <operand_name> ::= <token>
    <and_operand> ::= "and" <operand_name>
    <definition> ::= <token> <number> | <token> <literal>
    <literal> ::= "\"" <token> "\""
"""
