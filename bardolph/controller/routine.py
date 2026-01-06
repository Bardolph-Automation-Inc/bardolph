from bardolph.lib.symbol import SymbolType


class Routine:
    def __init__(self, name: str,
                 return_type: SymbolType = SymbolType.VAR,
                 address: int = 0):
        self._name = name
        self._return_type = return_type
        self._address = address
        self._return_address = address
        self._params = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def return_type(self) -> SymbolType:
        return self._return_type

    @property
    def params(self) -> list:
        return self._params

    @params.setter
    def params(self, params: list):
        self._params = params

    def add_param(self, name) -> None:
        self._params.append(name)

    def has_param(self, name) -> bool:
        return name in self._params

    def set_address(self, address: int) -> None:
        self._address = address

    def get_address(self) -> int:
        return self._address

    def set_return_address(self, address: int) -> None:
        self._return_address = address

    def get_return_address(self) -> int:
        return self._return_address


class RuntimeRoutine(Routine):
    def __init__(self, name: str, fn):
        super().__init__(name)
        self._fn = fn

    def invoke(self, stack_frame):
        return self._fn(stack_frame)
