    #!/usr/bin/env python

import argparse
import logging

from ..controller.instruction import OpCode, Operand
from ..controller.instruction import Register, SeriesOp, SetOp
from ..controller.units import UnitMode
from .code_gen import CodeGen
from . import lex
from ..lib.trace import trace_call, trace_call_enable
from ..lib.time_pattern import TimePattern
from .symbol_table import SymbolTable, SymbolType
from .token_types import TokenTypes


class Parser:
    _token_trace = False
    trace_call_enable(_token_trace)

    def __init__(self):
        self._lexer = None
        self._error_output = ''
        self._name = None
        self._current_token_type = None
        self._current_token = None
        self._op_code = OpCode.NOP
        self._symbol_table = SymbolTable()
        self._code_gen = CodeGen()

    def parse(self, input_string, skip_optimize=False):
        self._code_gen.clear()
        self._symbol_table.clear()
        self._error_output = ''
        self._lexer = lex.Lex(input_string)
        self._next_token()
        success = self._script()
        self._lexer = None
        if success:
            if not skip_optimize:
                self._code_gen.optimize()
            return self._code_gen.program
        else:
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

    def get_errors(self):
        return self._error_output

    def _script(self):
        return self._body() and self._eof()

    def _body(self):
        while self._current_token_type != TokenTypes.EOF:
            if not self._command():
                return False
        return True

    def _eof(self):
        if self._current_token_type != TokenTypes.EOF:
            return self._trigger_error("Didn't get to end of file.")
        return True

    @trace_call
    def _command(self):
        routine = self._symbol_table.get_routine(self._current_token)
        if routine is not None:
            return self._call_routine()
        return {
            TokenTypes.DEFINE: self._definition,
            TokenTypes.GET: self._get,
            TokenTypes.OFF: self._power_off,
            TokenTypes.ON: self._power_on,
            TokenTypes.PAUSE: self._pause,
            TokenTypes.REGISTER: self._set_reg,
            TokenTypes.SET: self._set,
            TokenTypes.UNITS: self._set_units,
            TokenTypes.WAIT: self._wait
        }.get(self._current_token_type, self._syntax_error)()

    @trace_call
    def _set_reg(self):
        self._name = self._current_token
        reg = Register[self._name.upper()]
        if reg == Register.TIME:
            return self._time()
                
        self._add_instruction(OpCode.SET_REG, Register.SERIES, reg)
        self._add_instruction(OpCode.SERIES, SeriesOp.REMOVE)
        
        self._next_token()
        if self._current_token_type == TokenTypes.NUMBER:
            return self._store_number(reg) and self._next_token()
        elif self._current_token_type == TokenTypes.LITERAL:
            return self._store_literal(reg) and self._next_token()
        elif self._current_token_type == TokenTypes.SERIES:
            self._next_token()
            return self._series(reg)
        elif self._current_token_type == TokenTypes.RANGE:
            self._next_token()
            return self._range(reg)            
        elif self._current_token in self._symbol_table:
            return self._symbol_reference(reg) and self._next_token()
        else:
            return self._token_error('Unknown parameter value: "{}"')
        
    @trace_call
    def _store_number(self, reg):
        if not reg in (Register.BRIGHTNESS, Register.DURATION,
                Register.FIRST_ZONE, Register.LAST_ZONE,
                Register.HUE, Register.KELVIN,
                Register.SATURATION, Register.TIME):
            return self._token_error('Numeric value {} not allowed here.')
        try:
            value = float(self._current_token)
            if reg in (Register.FIRST_ZONE, Register.LAST_ZONE):
                value = int(round(value))
            self._add_instruction(OpCode.SET_REG, reg, value)
            return True    
        except ValueError:
            return self._token_error('Invalid number: "{}"')
        
    @trace_call
    def _store_literal(self, reg):
        if reg != Register.NAME:
            return self._trigger_error('Quoted value not allowed here.')
        self._add_instruction(OpCode.SET_REG, reg, self._current_token)
        return True

    @trace_call
    def _symbol_reference(self, reg):
        # If the symbol is an alias for a value, put that value directly into a
        # SET_REG instruction. Otherwise, put the name of the parameter into
        # a GET_PARAM instruction. 
        s_type, s_value = self._symbol_table.get_symbol(self._current_token)
        if s_type == SymbolType.PARAM:
            param_name = self._current_token
            self._add_instruction(OpCode.GET_PARAM, reg, param_name)
        elif s_type == SymbolType.VAR:
            value = s_value
            if reg in (Register.FIRST_ZONE, Register.LAST_ZONE):
                value = int(round(value))
            self._add_instruction(OpCode.SET_REG, reg, value)
        else:
            return self._token_error('Passing routine as parameter: {}')
        return True

    @trace_call
    def _series(self, reg):     
        start = self._current_float()
        if start is None:
            return self._token_error("Expected start for series, got: {}")
        self._next_token()
        delta = self._current_float()
        if delta is None:
            return self._token_error("Expected step for series, got: {}")
        return self._init_series(reg, start, delta)
        
    @trace_call
    def _range(self, reg):
        start = self._current_float()
        if start is None:
            return self._token_error("Expected start for range, got: {}")    
        self._next_token()
        last = self._current_float()
        if last is None:
            return self._token_error("Expected end of range, got: {}")
        self._next_token()
        count = self._current_float()
        if count is None:
            return self._token_error("Expected count for range, got: {}")
        if count == 0:
            return self._trigger_error("Count must not be zero.")
        
        if count == 1:
            start = (start + last) / 2.0
            delta = 0.0
        else:
            delta = (last - start) / (count - 1)
        return self._init_series(reg, start, delta)

    def _init_series(self, reg, start, delta):
        self._add_instruction(OpCode.SET_REG, Register.SERIES, reg)
        self._add_instruction(OpCode.SERIES, SeriesOp.INIT, (start, delta))

        return self._next_token()
    
    @trace_call
    def _set(self):
        return self._action(OpCode.COLOR)

    @trace_call
    def _power_on(self):
        self._add_instruction(OpCode.SET_REG, Register.POWER, True)
        return self._action(OpCode.POWER)

    @trace_call
    def _power_off(self):
        self._add_instruction(OpCode.SET_REG, Register.POWER, False)
        return self._action(OpCode.POWER)

    @trace_call
    def _action(self, op_code):
        """ op_code: COLOR or POWER """
        self._op_code = op_code
        self._add_instruction(OpCode.WAIT)
        if self._op_code == OpCode.COLOR:
            self._add_instruction(OpCode.SERIES, SeriesOp.NEXT)

        self._next_token()
        if self._current_token_type == TokenTypes.ALL:
            return self._all_operand()
        return self._operand_list()
    
    @trace_call
    def _all_operand(self):
        self._add_instruction(OpCode.SET_REG, Register.NAME, None)
        self._add_instruction(OpCode.SET_REG, Register.OPERAND, Operand.ALL)
        self._add_instruction(self._op_code)
        return self._next_token()

    @trace_call
    def _operand_list(self):
        # For every operand in the list, issue the instruction in self._op_code.
        #
        if not self._operand():
            return False

        self._add_instruction(self._op_code)
                
        while self._current_token_type == TokenTypes.AND:
            self._next_token()
            if not self._operand():
                return False
            self._add_instruction(self._op_code)
        return True
    
    @trace_call
    def _operand(self):
        # Process a group, location, or light with an optional set of zones.
        # Do this by populating the NAME and OPERAND registers.
        #
        if self._current_token_type == TokenTypes.GROUP:
            operand = Operand.GROUP
            self._next_token()
        elif self._current_token_type == TokenTypes.LOCATION:
            operand = Operand.LOCATION
            self._next_token()
        else:
            operand = Operand.LIGHT
         
        # Puts literals verbatim into the code. Treat symbol references similar
        # to when they're in a "set" or "power" instruction.
        #   
        if self._current_token_type == TokenTypes.LITERAL:
            self._add_instruction(
                OpCode.SET_REG, Register.NAME, self._current_token)
        elif self._current_token in self._symbol_table:
            self._symbol_reference(Register.NAME)
        else:
            return self._token_error('Needed a light, got "{}".')

        self._next_token()
        
        if self._current_token_type == TokenTypes.ZONE:
            if not self._zone_range():
                return False
            operand = Operand.MZ_LIGHT

        self._add_instruction(OpCode.SET_REG, Register.OPERAND, operand)
        return True

    @trace_call
    def _and(self):
        self._next_token()
        if not self._operand_name():
            return False
        self._add_instruction(OpCode.SET_REG, Register.NAME, self._name)
        self._add_instruction(self._op_code)
        return True

    @trace_call
    def _zone_range(self):
        if self._op_code != OpCode.COLOR:
            return self._trigger_error('Zones not supported for {}'.format(
                self._op_code.name.tolower()))
        self._next_token()
        if not self._number_to_reg(Register.FIRST_ZONE):
            return False
        if self._current_token_type in (TokenTypes.NUMBER, TokenTypes.UNKNOWN):
            if not self._number_to_reg(Register.LAST_ZONE):
                return False
        else:
            self._add_instruction(OpCode.SET_REG, Register.LAST_ZONE, None) 
        return True

    @trace_call
    def _set_units(self):
        self._next_token()
        mode = {
            TokenTypes.RAW: UnitMode.RAW,
            TokenTypes.LOGICAL: UnitMode.LOGICAL
        }.get(self._current_token_type, None)

        if mode is None:
            return self._trigger_error(
                'Invalid parameter "{}" for units.'.format(self._current_token))
        
        self._add_instruction(OpCode.SET_REG, Register.UNIT_MODE, mode)
        return self._next_token()

    @trace_call
    def _wait(self):
        self._add_instruction(OpCode.WAIT)
        return self._next_token()

    @trace_call
    def _get(self):
        self._next_token()
        if self._current_token_type == TokenTypes.LITERAL:
            if not self._store_literal(Register.NAME):
                return False
        elif self._current_token in self._symbol_table:
            if not self._symbol_reference(Register.NAME):
                return False
        else:
            return self._token_error('Needed light or zone for get, got "{}".')
        
        self._next_token()
        if self._current_token_type == TokenTypes.ZONE:
            operand = Operand.MZ_LIGHT
            self._next_token()
            if self._current_token_type != TokenTypes.NUMBER:
                return self._token_error('Expected zone number, got "{}"')
            self._add_instruction(
                OpCode.SET_REG, Register.FIRST_ZONE, self._current_int())
            self._add_instruction(OpCode.SET_REG, Register.LAST_ZONE, None)            
            self._next_token()
        else:
            operand = Operand.LIGHT

        self._add_instruction(OpCode.SERIES, SeriesOp.CLEAR)
        self._add_instruction(OpCode.SET_REG, Register.OPERAND, operand)
        self._add_instruction(OpCode.GET_COLOR)
        
        return True

    @trace_call
    def _pause(self):
        self._add_instruction(OpCode.PAUSE)
        self._next_token()
        return True
    
    @trace_call
    def _time(self):
        self._next_token()
        if self._current_token_type == TokenTypes.AT:
            return self._process_time_patterns()
        return self._number_to_reg(Register.TIME)
        
    @trace_call
    def _number_to_reg(self, reg):
        if self._current_token_type == TokenTypes.NUMBER:
            return self._store_number(reg) and self._next_token()
        elif self._current_token in self._symbol_table:
            return self._symbol_reference(reg) and self._next_token()
        return self._token_error('Invalid numeric value: "{}"')
    
    @trace_call
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

    @trace_call
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
    
    @trace_call
    def _definition(self):
        self._next_token()
        if self._current_token_type in (
                TokenTypes.LITERAL, TokenTypes.NUMBER, TokenTypes.TIME_PATTERN):
            return self._token_error('Expected name for definition, got: {}')
        
        name = self._current_token
        if name in self._symbol_table:
            return self._token_error('Already defined: {}')

        self._next_token()
        if self._detect_routine_start():
            self._symbol_table.set_symbol(name, SymbolType.ROUTINE)
            self._add_instruction(OpCode.ROUTINE, name)
            if not self._routine_definition():
                return False
            self._add_instruction(OpCode.END, name)
            return True
        else:
            return self._value_definition(name)
    
    def _detect_routine_start(self):
        #
        # If a definition is followed by "with", "begin", a keyword
        # corresponding to a command, or the name of an existing routine, it's 
        # defining a routine and not a variable.
        #
        if self._current_token_type in (TokenTypes.BEGIN, TokenTypes.WITH,
                    TokenTypes.REGISTER, TokenTypes.SET): 
            return True
        if self._symbol_table.get_type(
                self._current_token) == SymbolType.ROUTINE:
            return True
        return False
    
    @trace_call
    def _routine_definition(self):
        context = None 

        if self._current_token_type == TokenTypes.WITH:
            context = SymbolTable()
            params = self._param_decl(context)
            if params is None:
                return False
            self._symbol_table.add_context(context)

        if self._current_token_type == TokenTypes.BEGIN:
            self._next_token()
            result = self._compound_proc()
        else:
            result = self._simple_proc()        
        if context is not None:
            self._symbol_table.remove_context()
        return result

    @trace_call
    def _param_decl(self, context):
        while self._current_token_type in (TokenTypes.AND, TokenTypes.WITH):
            self._next_token()
            if self._current_token_type != TokenTypes.UNKNOWN:
                self._token_error(
                    "Using keyword {} as a parameter name.")
                return None
            name = self._current_token    
            context.set_symbol(name, SymbolType.PARAM)
            self._add_instruction(OpCode.PARAM, name)
            self._next_token()
        return True
    
    @trace_call
    def _simple_proc(self):
        return self._command()
    
    @trace_call
    def _compound_proc(self):
        while self._current_token_type != TokenTypes.END:
            if self._current_token_type == TokenTypes.EOF:
                return self._trigger_error('End of file before "end".')
            if not self._command():
                return False
        return self._next_token()

    @trace_call
    def _value_definition(self, var_name):
        if self._current_token_type == TokenTypes.NUMBER:
            value = float(self._current_token)
        elif self._current_token_type == TokenTypes.LITERAL:
            value = self._current_token
        elif self._current_token_type == TokenTypes.TIME_PATTERN:
            value = TimePattern.from_string(self._current_token)
            if value is None:
                return self._time_spec_error()
        elif self._current_token in self._symbol_table:
            value = self._symbol_table.get_value(self._current_token)
        else:
            return self._token_error('Unknown term: "{}"')

        self._symbol_table.set_symbol(var_name, SymbolType.VAR, value)
        return self._next_token()
            
    def _call_routine(self):
        routine_name = self._current_token
        routine_def = self._symbol_table.get_routine(routine_name)
        if routine_def is None:
            return self._token_error('Unknown routine: "{}"')
        
        for param in routine_def.ordered_params:
            param_name = param.name
            self._next_token()
            param_value = self._current_token
            self._add_instruction(OpCode.PARAM, param_name, param_value)
            
        self._add_instruction(OpCode.CALL, routine_def.name)
        return True

    def _add_instruction(self, op_code, param0=None, param1=None):
        return self._code_gen.add_instruction(op_code, param0, param1)

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
        if self._token_trace:
            logging.info(
                'Next token: "{}" ({})'.format(
                    self._current_token, self._current_token_type))
        return True
    
    def _trace(self, grammar_name):
        if self._parse_trace:
            logging.info("Parse: ".format(grammar_name))
    
    def _current_int(self):
        if self._current_token_type != TokenTypes.NUMBER:
            return None
        return round(float(self._current_token))
    
    def _current_float(self):
        if self._current_token_type != TokenTypes.NUMBER:
            return None
        return float(self._current_token)

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
    <number_param> ::= <number> | "series" <number> <number>
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
