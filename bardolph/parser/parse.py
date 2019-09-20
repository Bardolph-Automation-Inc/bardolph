#!/usr/bin/env python

import argparse
import logging
import re

from ..controller.instruction import Instruction, OpCode, Operand
from . import lex
from .token_types import TokenTypes


token_regex = re.compile(r'"(.*?)"|\s+|\w+|#.*\n?')
word_regex = re.compile(r"\w+")


class Parser:
    def __init__(self):
        self.lexer = None
        self.error_output = ''
        self.light_state = {}
        self.name = None
        self.current_token_type = None
        self.current_token = None
        self.op_code = OpCode.nop
        self.symbol_table = {}
        self.code = []
        
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
        while succeeded and self.current_token_type != TokenTypes.eof:
            succeeded = self.command()
        return succeeded

    def eof(self):
        if self.current_token_type != TokenTypes.eof:
            return self.trigger_error("Didn't get to end of file.")
        return True

    def command(self):
        fn = {
            TokenTypes.brightness: self.set_reg,
            TokenTypes.define: self.definition,
            TokenTypes.duration: self.set_reg,
            TokenTypes.get: self.get,
            TokenTypes.hue: self.set_reg,
            TokenTypes.kelvin: self.set_reg,
            TokenTypes.off: self.power_off,
            TokenTypes.on: self.power_on,
            TokenTypes.pause: self.pause,
            TokenTypes.saturation: self.set_reg,
            TokenTypes.set: self.set,
            TokenTypes.time: self.set_reg
        }.get(self.current_token_type, self.syntax_error)
        return fn() if fn != None else True
        
    def set_reg(self):
        self.name = self.current_token
        self.next_token()

        if self.current_token_type == TokenTypes.integer:
            value = int(self.current_token)
        elif self.current_token_type == TokenTypes.literal:
            value = self.current_token
        elif self.current_token in self.symbol_table:
            value = self.symbol_table[self.current_token]
        else:
            return self.token_error('Unknown parameter value: "{}"')

        self.add_instruction(OpCode.set_reg, self.name, value)
        return self.next_token()

    def set(self):
        return self.action(OpCode.color)
    
    def get(self):
        return self.action(OpCode.get_color)
    
    def power_on(self):
        self.add_instruction(OpCode.set_reg, 'power', True)
        return self.action(OpCode.power)
        
    def power_off(self):
        self.add_instruction(OpCode.set_reg, 'power', False)
        return self.action(OpCode.power)
    
    def pause(self):
        self.add_instruction(OpCode.pause)
        self.next_token()
        return True
        
    def action(self, op_code):
        self.op_code = op_code
        self.next_token()

        if self.current_token_type == TokenTypes.group:
            self.add_instruction(OpCode.set_reg, 'operand', Operand.group)
            self.next_token()
        elif self.current_token_type == TokenTypes.location:
            self.add_instruction(OpCode.set_reg, 'operand', Operand.location)
            self.next_token()
        else:
            self.add_instruction(OpCode.set_reg, 'operand', Operand.light)
        
        return self.operand_list()
    
    def operand_list(self):
        if self.current_token_type == TokenTypes.all:
            self.add_instruction(OpCode.set_reg, 'name', None)
            if self.op_code != OpCode.get_color:
                self.add_instruction(OpCode.time_wait)
            self.add_instruction(self.op_code) 
            return self.next_token()
        
        if not self.operand_name():
            return False
        
        self.add_instruction(OpCode.set_reg, 'name', self.name)
        if self.op_code != OpCode.get_color:
            self.add_instruction(OpCode.time_wait)
        self.add_instruction(self.op_code)
        while self.current_token_type == TokenTypes.and_operand:
            if not self.and_operand():
                return False
        return True
    
    def operand_name(self):
        if self.current_token_type == TokenTypes.literal:
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
        self.add_instruction(OpCode.set_reg, 'name', self.name)
        self.add_instruction(self.op_code)
        return True
           
    def definition(self):
        self.next_token()
        if self.current_token_type in [
                TokenTypes.literal, TokenTypes.integer]:
            return self.token_error('Unexpected literal: {}')
        
        var_name = self.current_token
        self.next_token()
        if self.current_token_type == TokenTypes.integer:
            value = int(self.current_token)
        elif self.current_token_type == TokenTypes.literal:
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
        opt = []
        prev_value = {}
        for inst in self.code:
            if inst.op_code != OpCode.set_reg:
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
        | "time" <set_reg>
    <set_reg> ::= <name> <integer> | <name> <literal> | <name> <symbol>
    <set> ::= <action>
    <get> ::= <action>
    <power_off> ::= <action>
    <power_on> ::= <action>
    <action> ::= <op_code> <operand_list>
    <operand_list> ::= "all" | <operand_name> | <operand_name> <and_operand> *
    <operand_name> ::= <token>
    <and_operand> ::= "and" <operand_name>
    <definition> ::= <token> <integer> | <token> <literal>
    <literal> ::= "\"" <token> "\""
"""
