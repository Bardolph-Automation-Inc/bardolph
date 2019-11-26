from enum import Enum

from bardolph.lib.auto_repl import auto


class OpCode(Enum):
    COLOR = auto()
    END = auto()
    GET_COLOR = auto()
    NOP = auto()
    PAUSE = auto()
    POWER = auto()
    SET_REG = auto()
    STOP = auto()
    TIME_PATTERN = auto()
    TIME_WAIT = auto()
    ZONE = auto()


class Operand(Enum):
    ALL = auto()
    LIGHT = auto()
    GROUP = auto()
    LOCATION = auto()
    MZ_LIGHT = auto()


class SetOp(Enum):
    """ Used with TimePattern """
    INIT = auto()
    UNION = auto()
    

class Register(Enum):
    HUE = auto()
    SATURATION = auto()
    BRIGHTNESS = auto()
    KELVIN = auto()
    DURATION = auto()
    POWER = auto()
    NAME = auto()
    OPERAND = auto()
    TIME = auto()
    ZONES = auto()


class Instruction:
    def __init__(self, op_code, param0=None, param1=None):
        self._op_code = op_code
        self._param0 = param0
        self._param1 = param1

    def __repr__(self):
        if self._op_code == OpCode.TIME_PATTERN:
            return 'Instruction({}, {}, {})'.format(
                OpCode.TIME_PATTERN, self.param0, repr(self.param1))
        if self._param1 is None:
            if self._param0 is None:
                return 'Instruction({}, None, None)'.format(self._op_code)
            return 'Instruction({}, {}, None)'.format(
                self._op_code,
                Instruction.quote_if_string(self._param0))
        return 'Instruction({}, {}, {})'.format(
            self._op_code,
            Instruction.quote_if_string(self._param0),
            Instruction.quote_if_string(self._param1))
        
    def __eq__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError
        return (self._op_code == other._op_code
                and self._param0 == other._param0
                and self._param1 == other._param1)

    @property
    def op_code(self):
        return self._op_code
    
    @property
    def param0(self):
        return self._param0
    
    @property
    def param1(self):
        return self._param1
    
    def as_list_text(self):
        if self._op_code not in (OpCode.SET_REG, OpCode.TIME_PATTERN):
            return '{}'.format(self._op_code)
        return '{}, {}, {}'.format(
            self._op_code,
            Instruction.quote_if_string(self._param0),
            Instruction.quote_if_string(self._param1))

    @classmethod
    def quote_if_string(cls, obj):
        return ('"{}"' if isinstance(obj, str) else '{}').format(obj)
