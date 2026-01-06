from enum import Enum, auto
from typing import Any


class SymbolType(Enum):
    ARRAY = auto()
    CONSTANT = auto()
    EXTERN = auto()
    ROUTINE = auto()
    UNDEFINED = auto()
    VAR = auto()


class Symbol:
    def __init__(self,
                 name: str = '',
                 symbol_type: SymbolType = SymbolType.UNDEFINED,
                 static_value: Any = None):
        self._name = name
        self._symbol_type = symbol_type
        self._static_value = static_value

    def __repr__(self):
        return 'Symbol("{}", {}, {})'.format(
            self.name, self.symbol_type, self.static_value)

    @property
    def undefined(self) -> bool:
        return self._symbol_type == SymbolType.UNDEFINED

    @property
    def name(self) -> str:
        return self._name

    @property
    def symbol_type(self) -> SymbolType:
        return self._symbol_type

    @property
    def static_value(self) -> Any:
        return self._static_value

    @property
    def routine(self):
        if self._symbol_type is SymbolType.ROUTINE:
            return self._static_value
        return None
