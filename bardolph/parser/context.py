from collections import deque

from bardolph.controller.routine import Routine
from bardolph.lib.symbol import Symbol, SymbolType
from bardolph.lib.symbol_table import SymbolTable
from bardolph.parser.code_gen import CodeGen
from bardolph.vm.instruction import Instruction


class _LoopContext:
    def __init__(self):
        self.break_list = []


class Context:
    def __init__(self):
        self._globals = SymbolTable()
        self._locals = SymbolTable()
        self._loop_stack = deque()
        self._loop_depth = 0
        self._in_matrix = False
        self._current_routine = None

    def __contains__(self, name) -> bool:
        return name in self._locals or name in self._globals

    _undefined = Symbol()

    def clear(self) -> None:
        # Locals don't need to be in a stack because nested routines aren't
        # allowed.
        self._current_routine = None
        self._globals.clear()
        self._locals.clear()
        self._loop_stack.clear()

    def enter_routine(self, routine: Routine) -> None:
        self._current_routine = routine

    def get_current_routine(self) -> Routine | None:
        return self._current_routine

    def in_routine(self) -> bool:
        return self._current_routine is not None

    def exit_routine(self) -> None:
        self._current_routine = None
        self._locals.clear()

    def enter_matrix(self) -> None:
        self._in_matrix = True

    def in_matrix(self) -> bool:
        return self._in_matrix

    def exit_matrix(self) -> None:
        self._in_matrix = False
        self._locals.clear()

    def enter_loop(self) -> None:
        self._loop_stack.append(_LoopContext())

    def in_loop(self) -> bool:
        return len(self._loop_stack) > 0

    def exit_loop(self) -> None:
        self._loop_stack.pop()

    def add_break(self, inst: Instruction) -> None:
        self._top_break_list().append(inst)

    def _top_break_list(self):
        return self._loop_stack[-1].break_list

    def fix_break_addrs(self, code_gen: CodeGen) -> None:
        offset = code_gen.current_offset
        for inst in self._top_break_list():
            inst.param1 = offset - inst.param1

    def add_symbol(self, name: str, symbol_type: SymbolType) -> None:
        dest = self._locals if self._current_routine else self._globals
        dest.add_symbol(name, symbol_type)

    def add_routine(self, routine: Routine) -> None:
        self._globals.add_symbol(routine.name, SymbolType.ROUTINE, routine)

    def add_variable(self, name: str) -> None:
        dest = self._locals if self._current_routine else self._globals
        dest.add_symbol(name, SymbolType.VAR)

    def add_array(self, name: str) -> None:
        dest = self._locals if self._current_routine else self._globals
        dest.add_symbol(name, SymbolType.ARRAY)

    def add_global(self, name: str, symbol_type: SymbolType, value) -> None:
        self._globals.add_symbol(name, symbol_type, value)

    def get_data(self, name: str):
        return self.get_symbol_typed(
            name, (SymbolType.CONSTANT, SymbolType.VAR))

    def get_symbol(self, name: str) -> Symbol:
        """
        Get a parameter from the top of the stack. If it's not there, check
        the globals.
        """
        symbol = self._locals.get_symbol(name)
        if symbol.undefined:
            symbol = self._globals.get_symbol(name)
        return symbol

    def get_symbol_typed(self, name: str, *symbol_types) -> Symbol:
        symbol = self.get_symbol(name)
        if symbol.undefined or symbol.symbol_type in symbol_types:
            return symbol
        return self._undefined

    def has_symbol(self, name: str) -> bool:
        return not self.get_symbol(name).undefined

    def has_symbol_typed(self, name: str, *symbol_types) -> bool:
        symbol = self.get_symbol(name)
        return not symbol.undefined and symbol.symbol_type in symbol_types

    def get_routine(self, name: str) -> Symbol:
        return self._global_of_type(name, SymbolType.ROUTINE)

    def has_routine(self, name: str) -> bool:
        return not self._global_of_type(name, SymbolType.ROUTINE).undefined

    def get_constant(self, name: str) -> Symbol:
        return self._global_of_type(name, SymbolType.CONSTANT)

    def _global_of_type(self, name: str, symbol_type: SymbolType) -> Symbol:
        symbol = self._globals.get_symbol(name)
        if symbol.undefined or symbol.symbol_type == symbol_type:
            return symbol
        return self._undefined
