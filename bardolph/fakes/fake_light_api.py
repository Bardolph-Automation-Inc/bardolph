import logging
from enum import Enum, auto

from bardolph.controller import i_controller
from bardolph.fakes import fake_light
from bardolph.fakes.activity_monitor import Action, ActivityMonitor
from bardolph.lib.injection import bind_instance
from bardolph.lib.param_helper import param_32, param_bool, param_color


class _Type(Enum):
    MATRIX = auto()
    MULTI_ZONE = auto()
    STD = auto()


class _Chroma(Enum):
    COLOR = auto()
    WHITE = auto()


class _LightBuilder:
    def __init__(self):
        self._name = self._group = self._location = ''
        self._type = _Type.STD
        self._is_color = True
        self._width = self._height = 0

    def set_name(self, name: str):
        self._name = name
        return self

    def set_group(self, group: str):
        self._group = group
        return self

    def set_location(self, location: str):
        self._location = location
        return self

    def set_type(self, the_type: _Type):
        self._type = the_type
        return self

    def set_is_color(self, is_color: bool):
        self._is_color = is_color
        return self

    def set_height(self, height: int):
        self._height = height
        return self

    def set_width(self, width: int):
        self._width = width
        return self

    def build(self):
        match self._type:
            case _Type.MATRIX:
                new_light = fake_light.MatrixLight(
                    self._name, self._group, self._location)
                new_light.set_height(self._height)
                new_light.set_width(self._width)
            case _Type.MULTI_ZONE:
                new_light = fake_light.MultizoneLight(
                    self._name, self._group, self._location)
                new_light.set_width(self._width)
            case _Type.STD:
                new_light = fake_light.Light(
                    self._name, self._group, self._location)
        new_light.set_is_color(self._is_color)
        return new_light

    @staticmethod
    def new_from_spec(spec):
        it = iter(spec)
        builder = _LightBuilder()

        numbers = []
        strings = []
        keep_going = True
        while keep_going:
            try:
                desc = next(it)
                if isinstance(desc, str):
                    strings.append(desc)
                elif isinstance(desc, int):
                    numbers.append(desc)
                elif isinstance(desc, _Chroma):
                    builder.set_is_color(desc is _Chroma.COLOR)
                elif isinstance(desc, _Type):
                    builder.set_type(desc)
            except StopIteration:
                keep_going = False

        while len(strings) < 3:
            strings.append('')

        builder.set_name(strings[0])
        builder.set_group(strings[1])
        builder.set_location(strings[2])

        match len(numbers):
            case 1:
                builder.set_width(numbers[0])
            case 2:
                builder.set_height(numbers[0])
                builder.set_width(numbers[1])

        return builder.build()


class FakeLightApi(i_controller.LightApi):
    def __init__(self, specs):
        self._monitor = ActivityMonitor()
        self._lights = [_LightBuilder().new_from_spec(spec) for spec in specs]

    def get_lights(self):
        return self._lights

    def set_color_all_lights(self, color, duration):
        color = param_color(color)
        duration = param_32(duration)
        self._monitor.log_call(Action.SET_COLOR, color, duration)
        logging.info("Color (all) {}, {}".format(color, duration))
        for light in self.get_lights():
            light.quietly().set_color(color, duration)

    def set_power_all_lights(self, power_level, duration):
        power_level = param_bool(power_level)
        duration = param_32(duration)
        self._monitor.log_call(Action.SET_POWER, power_level, duration)
        logging.info("Power (all) {} {}".format(power_level, duration))
        for light in self.get_lights():
            light.quietly().set_power(power_level, duration)

    def get_call_list(self):
        return self._monitor.get_call_list()


class _Reinit:
    def __init__(self, specs):
        self._specs = specs

    def configure(self):
        bind_instance(FakeLightApi(self._specs)).to(i_controller.LightApi)


def using_large_set():
    specs = (
        ('Top', 'Pole', 'Home'),
        ('Middle', 'Pole', 'Home'),
        ('Bottom', 'Pole', 'Home'),

        ('Strip', 'Furniture', 'Home', _Type.MULTI_ZONE, 16),
        ('Balcony', 'Windows', 'Home', _Type.MULTI_ZONE, 32),
        ('Candle', 'Furniture', 'Home', _Type.MATRIX, 6, 5),
        ('White Candle', 'Furniture', 'Home',
            _Type.MATRIX, _Chroma.WHITE, 6, 5),
        ('Tube', 'Furniture', 'Home', _Type.MATRIX, 11, 5),

        ('Lamp', 'Furniture', 'Living Room', _Chroma.WHITE),
        ('table-0', 'Table', 'Living Room'),
        ('table-1', 'Table', 'Living Room'),
        ('table-2', 'Table', 'Living Room'),
        ('table-3', 'Table', 'Living Room'),
        ('table-4', 'Table', 'Living Room'),
        ('table-5', 'Table', 'Living Room'),
        ('table-6', 'Table', 'Living Room'),
        ('table-7', 'Table', 'Living Room')
    )
    return _Reinit(specs)


def using_small_set():
    specs = (
        ('light_1', 'a', 'b'),
        ('light_2', 'group', 'loc'),
        ('light_0', 'group', 'loc')
    )
    return _Reinit(specs)


def configure():
    using_large_set().configure()


def using(specs):
    return _Reinit(specs)
