import colorsys
from enum import Enum, auto

from bardolph.lib.noneable import noneable
from bardolph.vm.vm_codes import Register

_EPSILON = 1.0 / 65536.0 / 2.0

class UnitMode(Enum):
    LOGICAL = auto()
    RAW = auto()
    RGB = auto()

@noneable
def time_raw(logical_time):
    return logical_time * 1000.0

@noneable
def time_logical(raw_time):
    raw_time = float(raw_time)
    return 0.0 if -_EPSILON < raw_time < _EPSILON else raw_time / 1000.0

@noneable
def _pct_to_raw(pct):
    return 0.0 if -_EPSILON < pct < _EPSILON else pct / 100.0 * 65535.0

@noneable
def logical_to_raw(logical_color):
    if logical_color is None:
        return None
    logical_value = logical_color[0]
    if (-_EPSILON < logical_value < _EPSILON or
            360 - _EPSILON < logical_value < 360 + _EPSILON):
        h = 0.0
    else:
        h = (logical_value % 360.0) / 360.0 * 65535.0
    s = _pct_to_raw(logical_color[1])
    b = _pct_to_raw(logical_color[2])
    return [h, s, b, logical_color[3]]

@noneable
def raw_to_logical(raw_color):
    raw_value = raw_color[0]
    h = float(raw_value) / 65535.0 * 360.0
    raw_value = raw_color[1]
    s = 100.0 if raw_value >= 65535.0 else float(raw_value) / 65535.0 * 100.0
    raw_value = raw_color[2]
    b = 100.0 if raw_value >= 65535.0 else float(raw_value) / 65535.0 * 100.0
    return [max(h, 0.0), max(s, 0.0), max(b, 0.0), max(raw_color[3], 0.0)]

@noneable
def rgb_to_raw(rgb_color):
    r, g, b = [rgb_color[i] / 100.0 for i in range(0, 3)]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    make_raw = lambda x: round(max(0, min((x * 65535.0), 65535)))
    return [make_raw(h), make_raw(s), make_raw(v), round(rgb_color[3])]

@noneable
def rgb_to_logical(rgb_color):
    r, g, b = [rgb_color[i] / 100.0 for i in range(0, 3)]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return [h * 360.0, s * 100.0, v * 100.0, rgb_color[3]]

@noneable
def raw_to_rgb(raw_color):
    h, s, v = [raw_color[i] / 65535.0 for i in range(0, 3)]
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return [r * 100.0, g * 100.0, b * 100.0, raw_color[3]]

@noneable
def logical_to_rgb(logical_color):
    h = logical_color[0] / 360.0
    s = logical_color[1] / 100.0
    v = logical_color[2] / 100.0
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return [r * 100.0, g * 100.0, b * 100.0, logical_color[3]]

@noneable
def nop(color):
    return color

@noneable
def convert_fn(srce_type, dest_type):
    return {
        UnitMode.LOGICAL: {
            UnitMode.LOGICAL: None,
            UnitMode.RAW: logical_to_raw,
            UnitMode.RGB: logical_to_rgb },
        UnitMode.RAW: {
            UnitMode.LOGICAL: raw_to_logical,
            UnitMode.RAW: None,
            UnitMode.RGB: raw_to_rgb },
        UnitMode.RGB: {
            UnitMode.LOGICAL: rgb_to_logical,
            UnitMode.RAW: rgb_to_raw,
            UnitMode.RGB: None }
    }[srce_type][dest_type]

@noneable
def convert(srce, srce_type, dest_type):
    fn = convert_fn(srce_type, dest_type)
    return srce if fn is None else fn(srce)
