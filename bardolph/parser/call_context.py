from collections import deque

from ..lib.symbol import Symbol, SymbolType
from ..lib.symbol_table import SymbolTable

class CallContext:
    _empty_table = SymbolTable()

    def __init__(self):
        self._stack = deque()
        self._globals = SymbolTable()
        self.push()
        self._in_routine = False

    def __contains__(self, name) -> bool:
        """
        Return True if the name exists as any type in the current context.
        """
        symbol_table = self.peek()
        return ((symbol_table is not None and name in symbol_table)
                or name in self._globals)

    def clear(self) -> None:
        self._stack.clear()
        self.push()

    def enter_routine(self) -> None:
        self._in_routine = True

    def in_routine(self) -> bool:
        return self._in_routine

    def exit_routine(self) -> None:
        self._in_routine = False

    def push(self, symbol_table=None) -> None:
        if symbol_table is None:
            symbol_table = SymbolTable()
        self._stack.append(symbol_table)

    def pop(self) -> SymbolTable:
        if len(self._stack) != 0:
            self._stack.pop()
        return self.peek()

    def peek(self) -> SymbolTable:
        if len(self._stack) > 0:
            return self._stack[-1]
        return CallContext._empty_table

    def add_routine(self, routine) -> None:
        self._globals.add_symbol(routine.name, SymbolType.ROUTINE, routine)

    def add_param(self, name, value=None) -> None:
        """ Bring a parameter into scope as a variable. """
        self.peek().add_symbol(name, SymbolType.VAR, value)

    def add_global(self, name, symbol_type, value) -> None:
        self._globals.add_symbol(name, symbol_type, value)

    def resolve_variable(self, name) -> Symbol:
        return self.get_symbol_typed(name, (SymbolType.MACRO, SymbolType.VAR))

    def get_symbol(self, name) -> Symbol:
        """ Get a parameter from the top of the stack. If it's not there, check
        the globals. """
        symbol = self.peek().get_symbol(name)
        if symbol is not None:
            return symbol
        return self._globals.get_symbol(name)

    def get_symbol_typed(self, name, symbol_types) -> Symbol:
        symbol = self.get_symbol(name)
        if symbol is None or symbol.symbol_type not in symbol_types:
            return None
        return symbol

    def get_routine(self, name):
        routine = None
        symbol = self._global_of_type(name, SymbolType.ROUTINE)
        if symbol is not None:
            routine = symbol.value
        return routine

    def get_macro(self, name):
        macro = self._global_of_type(name, SymbolType.MACRO)
        return None if macro is None else macro.value

    def _global_of_type(self, name, symbol_type):
        symbol = self._globals.get_symbol(name)
        if symbol is None or symbol.symbol_type != symbol_type:
            return None
        return symbol
