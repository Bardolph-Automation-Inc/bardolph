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
    DISC = auto()
    DISCM = auto()
    DNEXT = auto()
    DNEXTM = auto()
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
    OUT = auto()
    OUTQ = auto()
    PARAM = auto()
    PAUSE = auto()
    POP = auto()
    POWER = auto()
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
    CURRENT = auto()
    FIRST = auto()
    INCR = auto()
    LAST = auto()

class Operator(Enum):
    ADD = auto()
    AND = auto()
    DIV = auto()
    EQ = auto()
    LT = auto()
    LTE = auto()
    GT = auto()
    GTE = auto()
    MOD = auto()
    MUL = auto()
    NOT = auto()
    NOTEQ = auto()
    OR = auto()
    POW = auto()
    SUB = auto()
    UADD = auto()
    USUB = auto()

class Operand(Enum):
    ALL = auto()
    LIGHT = auto()
    GROUP = auto()
    LOCATION = auto()
    MZ_LIGHT = auto()
    NULL = auto()

class SetOp(Enum):
    """ Used with TimePattern """
    INIT = auto()
    UNION = auto()
