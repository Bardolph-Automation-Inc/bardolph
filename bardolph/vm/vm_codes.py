from enum import Enum

from bardolph.lib.auto_repl import auto

class Register(Enum):
    BRIGHTNESS = auto()
    DURATION = auto()
    FIRST_ZONE = auto()
    HUE = auto()
    LAST_ZONE = auto()
    KELVIN = auto()
    NAME = auto()
    OPERAND = auto()
    POWER = auto()
    RESULT = auto()
    SATURATION = auto()
    TIME = auto()
    UNIT_MODE = auto()

    @classmethod
    def from_string(cls, name):
        upper = name.upper()
        return getattr(Register, upper) if hasattr(Register, upper) else None

class OpCode(Enum):
    BREAKPOINT = auto()
    COLOR = auto()
    CONSTANT = auto()
    END = auto()
    END_LOOP = auto()
    GET_COLOR = auto()
    JSR = auto()
    JUMP = auto()
    LOOP = auto()
    MOVE = auto()
    MOVEQ = auto()
    NOP = auto()
    OP = auto()
    PARAM = auto()
    PAUSE = auto()
    POWER = auto()
    POP = auto()
    PUSH = auto()
    PUSHQ = auto()
    ROUTINE = auto()
    STOP = auto()
    TIME_PATTERN = auto()
    WAIT = auto()

class JumpCondition(Enum):
    ALWAYS = auto()
    IF_FALSE = auto()
    IF_TRUE = auto()

class LoopVar(Enum):
    COUNTER = auto()
    FIRST = auto()
    INCR = auto()
    LAST = auto()

class Operator(Enum):
    ADD = auto()
    DIV = auto()
    MUL = auto()
    SUB = auto()

    UADD = auto()
    USUB = auto()
    NOT = auto()

    AND = auto()
    OR = auto()

    EQ = auto()
    NOTEQ = auto()
    LT = auto()
    LTE = auto()
    GT = auto()
    GTE = auto()

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
