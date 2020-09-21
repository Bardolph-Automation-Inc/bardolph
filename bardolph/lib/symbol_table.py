from .symbol import Symbol, SymbolType

class SymbolTable:
    def __init__(self):
        self._dict = {}

    def __contains__(self, name):
        return name in self._dict

    def clear(self):
        self._dict.clear()

    def add_symbol(self, name, symbol_type=SymbolType.UNKNOWN, value=None):
        self._dict[name] = Symbol(name, symbol_type, value)

    def get_symbol(self, name):
        return self._dict.get(name, Symbol())

    def get_type(self, name):
        return self.get_symbol(name).symbol_type

    def get_value(self, name):
        symbol = self.get_symbol(name)
        return None if symbol is None else symbol.value

    def get_routine(self, name):
        s_type = self.get_type(name)
        return self.get_value(name) if s_type == SymbolType.ROUTINE else None
