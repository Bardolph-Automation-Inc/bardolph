from enum import Enum

from bardolph.lib.auto_repl import auto
from bardolph.vm.vm_codes import Register


_RAW_RANGE = (0, 65535)


class UnitMode(Enum):
    LOGICAL = auto()
    RAW = auto()

def has_range(reg):
    return reg in (
        Register.BRIGHTNESS, Register.HUE, Register.KELVIN, Register.SATURATION)

def requires_conversion(reg):
    return reg in (
        Register.BRIGHTNESS, Register.DURATION, Register.HUE,
        Register.SATURATION, Register.TIME)

def get_range(reg):
    """
    Return the allowable range, in raw units, for a parameter.

    reg:
        token_type.TokenType designating the register to be set. May also
        be a string containing the name of the Enum.

    Returns:
        A tuple containing (minimum, maximum), or None if the parameter
        does not have a limited range of values.
    """
    reg = _string_check(reg)
    return (None, None) if reg in (
        Register.DURATION, Register.TIME) else _RAW_RANGE

def as_raw(reg, logical_value, use_float=False):
    """
    If necessary, converts to integer value that can be passed into the
    light API.

    Args:
        reg: TokenType corresponding to the register being set.
        logical_value: the number to be converted. May also
        be a string containing the name of the Enum.

    Returns:
        If no conversion is done, returns the incoming value untouched.
        Otherwise, an integer that corresponds to the logical value.
    """
    reg = _string_check(reg)
    if not requires_conversion(reg):
        return logical_value

    value = logical_value
    if reg == Register.HUE:
        if logical_value in (0.0, 360.0):
            value = 0.0
        else:
            value = (logical_value % 360.0) / 360.0 * 65535.0
    elif reg in (Register.BRIGHTNESS, Register.SATURATION):
        if logical_value == 100.0:
            value = 65535.0
        else:
            value = logical_value / 100.0 * 65535.0
    elif reg in (Register.DURATION, Register.TIME):
        value = logical_value * 1000.0

    if reg == Register.HUE and value > 65535.0:
        value %= 65536.0
    return value if use_float else round(value)

def as_logical(reg, raw_value):
    """If necessary, converts to floating-point logical value that
    typically apears in a script.

    Args:
        reg: TokenType corresponding to the register being set.
        raw_value: the number to be converted. May also
        be a string containing the name of the Enum.

    Returns:
        If no conversion is done, returns the incoming value untouched.
        Otherwise, a float that corresponds to the raw value.
    """
    reg = _string_check(reg)
    if not requires_conversion(reg):
        return raw_value

    value = raw_value
    if reg == Register.HUE:
        value = float(raw_value) / 65535.0 * 360.0
    elif reg in (Register.BRIGHTNESS, Register.SATURATION):
        if raw_value == 65535:
            value = 100.0
        else:
            value = float(raw_value) / 65535.0 * 100.0
    elif reg in (Register.DURATION, Register.TIME):
        value = raw_value / 1000.0
    return value

def _string_check(reg):
    return Register[reg.upper()] if isinstance(reg, str) else reg
