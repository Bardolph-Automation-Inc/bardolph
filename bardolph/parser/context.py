from collections import deque

from bardolph.lib.symbol import Symbol, SymbolType
from bardolph.lib.symbol_table import Symbol, SymbolTable


class _LoopContext:
    def __init__(self):
        self.break_list = []


class Context:
    def __init__(self):
        self._globals = SymbolTable()
        self._locals = SymbolTable()
        self._loop_stack = deque()
        self._loop_depth = 0
        self._in_routine = False
        self._return_list = []

    def __contains__(self, name) -> bool:
        return name in self._locals or name in self._globals

    def clear(self) -> None:
        self._in_routine = False
        self._globals.clear()
        self._locals.clear()
        self._loop_stack.clear()
        self._return_list.clear()

    def enter_routine(self) -> None:
        self._in_routine = True

    def in_routine(self) -> bool:
        return self._in_routine

    def exit_routine(self) -> None:
        self._in_routine = False
        self._locals.clear()
        self._return_list.clear()

    def enter_loop(self) -> None:
        self._loop_stack.append(_LoopContext())

    def in_loop(self) -> bool:
        return len(self._loop_stack) > 0

    def exit_loop(self) -> None:
        self._loop_stack.pop()

    def add_break(self, inst) -> None:
        self._top_break_list().append(inst)

    def _top_break_list(self):
        return self._loop_stack[-1].break_list

    def fix_break_addrs(self, code_gen) -> None:
        offset = code_gen.current_offset
        for inst in self._top_break_list():
            inst.param1 = offset - inst.param1

    def add_return(self, inst) -> None:
        self._return_list.append(inst)

    def fix_return_addrs(self, code_gen) -> None:
        offset = code_gen.current_offset
        for inst in self._return_list:
            inst.param1 = offset - inst.param1

    def add_routine(self, routine) -> None:
        self._globals.add_symbol(routine.name, SymbolType.ROUTINE, routine)

    def add_variable(self, name, value=None) -> None:
        dest = self._locals if self._in_routine else self._globals
        dest.add_symbol(name, SymbolType.VAR, value)

    def add_global(self, name, symbol_type, value) -> None:
        self._globals.add_symbol(name, symbol_type, value)

    def get_data(self, name):
        return self.get_symbol_typed(name, (SymbolType.MACRO, SymbolType.VAR))

    def get_symbol(self, name) -> Symbol:
        """
        Get a parameter from the top of the stack. If it's not there, check
        the globals.
        """
        symbol = self._locals.get_symbol(name)
        if symbol.undefined:
            symbol = self._globals.get_symbol(name)
        return symbol

    def get_symbol_typed(self, name, symbol_types):
        symbol = self.get_symbol(name)
        if symbol.undefined or symbol.symbol_type in symbol_types:
            return symbol
        return Symbol()

    def has_symbol(self, name) -> bool:
        return not self.get_symbol(name).undefined

    def has_symbol_typed(self, name, * symbol_types) -> bool:
        symbol = self.get_symbol(name)
        return not symbol.undefined and symbol.symbol_type in symbol_types

    def get_routine(self, name):
        return self._global_of_type(name, SymbolType.ROUTINE)

    def has_routine(self, name):
        return not self._global_of_type(name, SymbolType.ROUTINE).undefined

    def get_macro(self, name) -> Symbol:
        return self._global_of_type(name, SymbolType.MACRO)

    def _global_of_type(self, name, symbol_type) -> Symbol:
        symbol = self._globals.get_symbol(name)
        if symbol.undefined or symbol.symbol_type == symbol_type:
            return symbol
        return Symbol()
