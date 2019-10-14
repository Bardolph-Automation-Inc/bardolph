from enum import auto, Enum


class OpCode(Enum):
    COLOR = auto()
    END = auto()
    GET_COLOR = auto()
    NOP = auto()
    PAUSE = auto()
    POWER = auto()
    SET_REG = auto()
    STOP = auto()
    TIME_WAIT = auto()


class Operand(Enum):
    ALL = auto()
    LIGHT = auto()
    GROUP = auto()
    LOCATION = auto()


class Instruction:
    def __init__(self, op_code=OpCode.NOP, name=None, param=None):
        self._op_code = op_code
        self._name = name
        self._param = param

    def __repr__(self):
        if self._param is None:
            if self._name is None:
                return 'Instruction(OpCode.{}, None, None)'.format(
                    self._op_code._name)
            return 'Instruction(OpCode.{}, "{}", None)'.format(
                self._op_code._name, self._name)

        if type(self._param).__name__ == 'str':
            param_str = '"{}"'.format(self._param)
        else:
            param_str = str(self._param)

        return 'Instruction(OpCode.{}, "{}", {})'.format(
            self._op_code._name_, self._name, param_str)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError
        return (self._op_code == other._op_code
                and self._name == other._name and self._param == other._param)

    @property
    def op_code(self):
        return self._op_code
    
    @property
    def name(self):
        return self._name
    
    @property
    def param(self):
        return self._param
    
    def as_list_text(self):
        if self._op_code != OpCode.SET_REG:
            return 'OpCode.{}'.format(self._op_code._name)

        if type(self._param).__name__ == 'str':
            param_str = '"{}"'.format(self._param)
        else:
            param_str = str(self._param)

        return 'OpCode.set_reg, "{}", {}'.format(self._name, param_str)
