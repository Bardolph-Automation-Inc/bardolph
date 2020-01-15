from enum import Enum

from bardolph.lib.auto_repl import auto

class SymbolType(Enum):
    PARAM = auto()
    ROUTINE = auto()
    VAR = auto()

class SymbolTable:
    def __init__(self):
        self._dict = {}
        self._other = None
        
    def __contains__(self, symbol):
        if self._dict.__contains__(symbol):
            return True
        return self._other is not None and self._other.__contains__(symbol)
    
    def add_context(self, other):
        self._other = other
        
    def remove_context(self):
        self._other = None
    
    def clear(self):
        self._other = None
        self._dict.clear()
    
    def set_symbol(self, name, symbol_type, value=None):
        self._dict[name] = (symbol_type, value)

    def get_symbol(self, name):
        # Return (type, value)
        pair = None
        if self._other is not None:
            pair = self._other.get_symbol(name)
        if pair is None: 
            pair = self._dict.get(name, None)
        return pair if pair is not None else (None, None)
    
    def get_type(self, name):
        symbol_type, _ = self.get_symbol(name)
        return symbol_type
    
    def get_value(self, name):
        _, symbol_name = self.get_symbol(name)
        return symbol_name
    
    def get_routine(self, name):
        symbol_type, value = self.get_symbol(name)
        return value if symbol_type == SymbolType.ROUTINE else None
