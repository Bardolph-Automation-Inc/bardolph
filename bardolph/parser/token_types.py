from enum import IntEnum

next_int_value = 0

def auto():
    global next_int_value
    next_int_value += 1
    return next_int_value

class TokenTypes(IntEnum):
    all = auto()
    and_operand = auto()
    brightness = auto()
    define = auto()
    duration = auto()
    eof = auto()
    get = auto()
    group = auto()
    hue = auto()
    integer = auto()
    literal = auto()
    location = auto()
    off = auto()
    on = auto()
    pause = auto()
    kelvin = auto()
    saturation = auto()
    set = auto()
    space = auto()
    syntax_error = auto()
    time = auto()
    unknown = auto()
