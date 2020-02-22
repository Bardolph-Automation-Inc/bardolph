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

    def get_symbol(self, name) -> Symbol:
        # Return (type, value)
        return self._dict.get(name, None)

    def get_type(self, name):
        pair = self.get_symbol(name)
        if pair is None:
            return None
        symbol_type, _ = pair
        return symbol_type

    def get_value(self, name):
        pair = self.get_symbol(name)
        if pair is None:
            return None
        _, symbol_name = pair
        return symbol_name

    def get_routine(self, name):
        pair = self.get_symbol(name)
        if pair is None:
            return None
        symbol_type, value = self.get_symbol(name)
        return value if symbol_type == SymbolType.ROUTINE else None
