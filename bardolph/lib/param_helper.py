import functools


def param_8(param) -> int:
    # Make sure a param can be represented as an 8-bit unsigned integer.
    return round(max(0, min(param, 0xff)))


def param_16(param) -> int:
    # Make sure a param can be represented as a 16-bit unsigned integer.
    return round(max(0, min(param, 0xffff)))


def param_32(param) -> int:
    # Make sure a param can be represented a 32-bit unsigned integer.
    return round(max(0, min(param, 0xffffffff)))


def param_bool(param) -> int:
    return 1 if param else 0


def param_color(color):
    return [param_16(x) for x in color]
