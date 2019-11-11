from enum import Enum

from bardolph.lib.auto_repl import auto
from ..controller.instruction import Register


_RAW_RANGE = (0, 65535)


class UnitMode(Enum):
    LOGICAL = auto()
    RAW = auto()


class Units:
    def has_range(self, reg):
        return reg not in (Register.DURATION, Register.TIME)

    def requires_conversion(self, reg):
        return reg not in (
            Register.DURATION, Register.KELVIN, Register.TIME)

    def get_range(self, reg):
        """
        Return the allowable range, in raw units, for a parameter.

        Reg:
            token_type.TokenType designating the register to be set. May also
            be a string containing the name of the Enum.

        Returns:
            A tuple containing (minimum, maximum), or None if the parameter
            does not have a limited range of values.
        """
        reg = Units._string_check(reg)
        return None if reg in (
            Register.DURATION, Register.TIME) else _RAW_RANGE

    def as_raw(self, reg, logical_value):
        """If necessary, converts to integer value that can be passed into the
        light API.

        Args:
            reg: TokenType corresponding to the register being set.
            logical_value: the number to be converted. May also
            be a string containing the name of the Enum.

        Returns:
            If no conversion is done, returns the incoming value untouched.
            Otherwise, an integer that corresponds to the logical value.
        """
        value = logical_value
        reg = Units._string_check(reg)
        if self.requires_conversion(reg):
            if reg == Register.HUE:
                if logical_value in (0.0, 360.0):
                    value = 0
                else:
                    value = round((logical_value % 360.0) / 360.0 * 65535.0)
            elif reg in (Register.BRIGHTNESS, Register.SATURATION):
                if logical_value == 100.0:
                    value = 65535
                else:
                    value = round(logical_value / 100.0 * 65535.0)
        return round(value)

    def as_logical(self, reg, raw_value):
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
        value = raw_value
        reg = Units._string_check(reg)
        if not self.requires_conversion(reg):
            return raw_value
        if reg == Register.HUE:
            value = float(raw_value) / 65535.0 * 360.0
        elif reg in (Register.BRIGHTNESS, Register.SATURATION):
            if raw_value == 65535:
                value = 100.0
            else:
                value = float(raw_value) / 65535.0 * 100.0
        return value
    
    @classmethod
    def _string_check(cls, reg):
        return Register[reg.upper()] if isinstance(reg, str) else reg
