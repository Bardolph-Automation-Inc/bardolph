import logging
from enum import Enum, auto

from bardolph.controller import i_controller
from bardolph.fakes import fake_light
from bardolph.fakes.activity_monitor import Action, ActivityMonitor
from bardolph.lib import i_lib, injection
from bardolph.lib.injection import bind_instance
from bardolph.lib.param_helper import param_32, param_bool, param_color


class LightType(Enum):
    MATRIX = auto()
    MULTI_ZONE = auto()
    STD = auto()


class FakeLightApi(i_controller.LightApi):
    def __init__(self, specs):
        self._monitor = ActivityMonitor()
        self._lights = [self._build_light(spec) for spec in specs]

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

    def _build_light(self, spec):
        match spec:
            case name, group, location:
                return fake_light.Light(name, group, location, [0] * 4)
            case name, group, location, color:
                return fake_light.Light(name, group, location, color)
            case name, group, location, color, LightType.MATRIX:
                return fake_light.MatrixLight(name, group, location, color)
            case name, group, location, color, LightType.MULTI_ZONE, zones:
                return fake_light.MultizoneLight(
                    name, group, location, color, zones)

        logging.warning(
            "FakeLightApi._build_light(), no match: {}".format(spec))
        return None


class _Reinit:
    # name, group, location, optional color, optional LightType
    def __init__(self, specs):
        self._specs = specs

    def configure(self):
        bind_instance(FakeLightApi(self._specs)).to(i_controller.LightApi)


def using_large_set():
    settings = injection.provide(i_lib.Settings)
    default_color = settings.get_value('matrix_init_color', [0] * 4)

    specs = (
        ('Top', 'Pole', 'Home', [10, 20, 30, 40]),
        ('Middle', 'Pole', 'Home', [100, 200, 300, 400]),
        ('Bottom', 'Pole', 'Home', [1000, 2000, 3000, 4000]),

        ('Strip', 'Furniture', 'Home', default_color, LightType.MULTI_ZONE, 16),
        ('Balcony', 'Windows', 'Home', default_color, LightType.MULTI_ZONE, 32),
        ('Candle', 'Furniture', 'Home', [0] * 4, LightType.MATRIX),

        ('Lamp', 'Furniture', 'Living Room', [10000, 20000, 30000, 4004]),

        ('table-0', 'Table', 'Living Room', [16000, 16000, 16000, 2700]),
        ('table-1', 'Table', 'Living Room', [16000, 16000, 16000, 2700]),
        ('table-2', 'Table', 'Living Room', [16000, 16000, 16000, 2700]),
        ('table-3', 'Table', 'Living Room', [16000, 16000, 16000, 2700]),
        ('table-4', 'Table', 'Living Room', [16000, 16000, 16000, 2700]),
        ('table-5', 'Table', 'Living Room', [16000, 16000, 16000, 2700]),
        ('table-6', 'Table', 'Living Room', [16000, 16000, 16000, 2700]),
        ('table-7', 'Table', 'Living Room', [16000, 16000, 16000, 2700])
    )
    return _Reinit(specs)


def using_small_set():
    color = [1, 2, 3, 4]
    specs = (
        ('light_1', 'a', 'b', color),
        ('light_2', 'group', 'loc', color),
        ('light_0', 'group', 'loc', color)
    )
    return _Reinit(specs)


def configure():
    using_large_set().configure()


def using(specs):
    return _Reinit(specs)
