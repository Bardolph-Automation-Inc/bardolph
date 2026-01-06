from enum import Enum, auto


class Register(Enum):
    BLUE = auto()
    BRIGHTNESS = auto()
    DEFAULT = auto()
    DISC_FORWARD = auto()
    DURATION = auto()
    FIRST_COLUMN = auto()
    FIRST_ROW = auto()
    FIRST_ZONE = auto()
    GREEN = auto()
    HUE = auto()
    LAST_COLUMN = auto()
    LAST_ROW = auto()
    LAST_ZONE = auto()
    KELVIN = auto()
    MATRIX = auto()
    MAT_BODY = auto()
    MAT_TIP = auto()
    NAME = auto()
    OPERAND = auto()
    PC = auto()
    POWER = auto()
    RED = auto()
    RESULT = auto()
    SATURATION = auto()
    TIME = auto()
    UNIT_MODE = auto()

    @staticmethod
    def from_string(name):
        upper = name.upper()
        return getattr(Register, upper) if hasattr(Register, upper) else None


class OpCode(Enum):
    ARRAY = auto()
    BASE = auto()
    BREAKPOINT = auto()
    COLOR = auto()
    CONSTANT = auto()
    CTX = auto()
    DIM = auto()
    DISC = auto()
    DISCM = auto()
    DNEXT = auto()
    DNEXTM = auto()
    END = auto()
    END_CTX = auto()
    END_LOOP = auto()
    GET_COLOR = auto()
    INDEX = auto()
    JSR = auto()
    JUMP = auto()
    LOOP = auto()
    MATRIX = auto()
    MOVE = auto()
    MOVEQ = auto()
    NOP = auto()
    OP = auto()
    OUT = auto()
    PARAM = auto()
    PAUSE = auto()
    PEEK = auto()
    POP = auto()
    POWER = auto()
    PUSH = auto()
    PUSHQ = auto()
    RETURN = auto()
    ROUTINE = auto()
    STOP = auto()
    TIME_PATTERN = auto()
    WAIT = auto()


class JumpCondition(Enum):
    ALWAYS = auto()
    IF_FALSE = auto()
    IF_TRUE = auto()


class LoopVar(Enum):
    # These variables are internal and invisible to the script code.
    COUNTER = auto()
    COUNT_LAST = auto()
    CURRENT = auto()
    EXIT_JMP = auto()
    INCREMENT = auto()
    NAME_FIRST = auto()
    RANGE_FIRST = auto()
    RANGE_LAST = auto()


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
    SET = auto()
    SIZE = auto()
    SUB = auto()
    UADD = auto()
    USUB = auto()


class Operand(Enum):
    ALL = auto()
    LIGHT = auto()
    GROUP = auto()      # Device-configured group or location
    LOCATION = auto()
    MATRIX = auto()
    DEFAULT = auto()
    MATRIX_LIGHT = auto()
    MZ_LIGHT = auto()
    NULL = auto()


class IoOp(Enum):
    LITERAL = auto()
    PRINT = auto()
    PRINT_END = auto()
    PRINTF = auto()
    REGISTER = auto()


class SetOp(Enum):
    """ Used with TimePattern """
    INIT = auto()
    UNION = auto()
