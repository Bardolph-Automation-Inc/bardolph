from collections import deque

from bardolph.lib.symbol import Symbol, SymbolType
from bardolph.lib.symbol_table import Symbol, SymbolTable

class CallContext:
    _empty_table = SymbolTable()

    def __init__(self):
        self._stack = deque()
        self._in_routine = False
        self._globals = SymbolTable()
        self._stack.append(self._globals)

    def __contains__(self, name) -> bool:
        """
        Return True if the name exists as any type in the current context.
        """
        return name in self.peek() or name in self._globals

    def clear(self) -> None:
        self._in_routine = False
        self._globals.clear()
        self._stack.clear()
        self._stack.append(self._globals)

    def enter_routine(self) -> None:
        self._in_routine = True

    def in_routine(self) -> bool:
        return self._in_routine

    def exit_routine(self) -> None:
        self._in_routine = False

    def push(self, symbol_table=None) -> None:
        self._stack.append(symbol_table or SymbolTable())

    def pop(self) -> SymbolTable:
        assert len(self._stack) > 1
        return self._stack.pop()

    def peek(self) -> SymbolTable:
        assert len(self._stack) > 0
        return self._stack[-1]

    def add_routine(self, routine) -> None:
        self._globals.add_symbol(routine.name, SymbolType.ROUTINE, routine)

    def add_variable(self, name, value=None) -> None:
        self.peek().add_symbol(name, SymbolType.VAR, value)

    def add_global(self, name, symbol_type, value) -> None:
        self._globals.add_symbol(name, symbol_type, value)

    def get_data(self, name):
        return self.get_symbol_typed(name, (SymbolType.MACRO, SymbolType.VAR))

    def get_symbol(self, name) -> Symbol:
        """
        Get a parameter from the top of the stack. If it's not there, check
        the globals.
        """
        symbol = self.peek().get_symbol(name)
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

    def get_macro(self, name):
        return self._global_of_type(name, SymbolType.MACRO)

    def _global_of_type(self, name, symbol_type):
        symbol = self._globals.get_symbol(name)
        if symbol.undefined or symbol.symbol_type == symbol_type:
            return symbol
        return Symbol()
