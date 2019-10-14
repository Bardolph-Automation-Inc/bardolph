from enum import auto, Enum

from ..parser.token_types import TokenTypes


_RAW_RANGE = (0, 65535)


class UnitMode(Enum):
    LOGICAL = auto()
    RAW = auto()


class Units:
    def has_range(self, reg):
        return reg not in (TokenTypes.DURATION, TokenTypes.TIME)

    def requires_conversion(self, reg):
        return reg not in (
            TokenTypes.DURATION, TokenTypes.KELVIN, TokenTypes.TIME)

    def get_range(self, reg):
        """
        Return the allowable range, in raw units, for a parameter.

        Reg:
            token_type.TokenType designating the register to be set.

        Returns:
            A tuple containing (minimum, maximum), or None if the parameter
            does not have a limited range of values.
        """
        return None if reg in (
            TokenTypes.DURATION, TokenTypes.TIME) else _RAW_RANGE

    def as_raw(self, reg, logical_value):
        """If necessary, converts to integer value that can be passed into the
        light API.

        Args:
            reg: TokenType corresponding to the register being set.
            logical_value: the number to be converted.

        Returns:
            If no conversion is done, returns the incoming value untouched.
            Otherwise, an integer that corresponds to the logical value.
        """
        value = logical_value
        if self.requires_conversion(reg):
            if reg == TokenTypes.HUE:
                if logical_value in (0.0, 360.0):
                    value = 0
                else:
                    value = round((logical_value % 360.0) / 360.0 * 65535.0)
            elif reg in (TokenTypes.BRIGHTNESS, TokenTypes.SATURATION):
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
            raw_value: the number to be converted.

        Returns:
            If no conversion is done, returns the incoming value untouched.
            Otherwise, a float that corresponds to the raw value.
        """
        value = raw_value
        if not self.requires_conversion(reg):
            return raw_value
        if reg == TokenTypes.HUE:
            value = float(raw_value) / 65535.0 * 360.0
        elif reg in (TokenTypes.BRIGHTNESS, TokenTypes.SATURATION):
            if raw_value == 65535:
                value = 100.0
            else:
                value = float(raw_value) / 65535.0 * 100.0
        return value
