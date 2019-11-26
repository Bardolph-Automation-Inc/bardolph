import logging

from lifxlan.errors import WorkflowException

from ..lib.i_lib import Clock, TimePattern
from ..lib.injection import inject, provide

from .get_key import getch
from .i_controller import LightSet
from .instruction import OpCode, Operand, SetOp

class Registers:
    def __init__(self):
        self.hue = 0
        self.saturation = 0
        self.brightness = 0
        self.kelvin = 0
        self.duration = 0
        self.power = False
        self.name = None
        self.operand = None
        self.zones = None
        self.time = 0 # ms.

    def get_color(self):
        return [self.hue, self.saturation, self.brightness, self.kelvin]

    def get_power(self):
        return 65535 if self.power else 0


class Machine:
    def __init__(self):
        self._pc = 0
        self._cue_time = 0
        self._clock = provide(Clock)
        self._variables = {}
        self._program = []
        self._reg = Registers()
        self._enable_pause = True
        self._fn_table = {
            OpCode.COLOR: self._color,
            OpCode.END: self._end,
            OpCode.GET_COLOR: self._get_color,
            OpCode.NOP: self._nop,
            OpCode.PAUSE: self._pause,
            OpCode.POWER: self._power,
            OpCode.SET_REG: self._set_reg,
            OpCode.STOP: self.stop,
            OpCode.TIME_PATTERN: self._time_pattern,
            OpCode.TIME_WAIT: self._time_wait
        }

    def run(self, program):
        self._program = program
        self._pc = 0
        self._cue_time = 0
        self._clock.start()
        while self._pc < len(self._program):
            inst = self._program[self._pc]
            if inst.op_code == OpCode.STOP:
                break
            self._fn_table[inst.op_code]()
            self._pc += 1
        self._clock.stop()

    def stop(self):
        self._pc = len(self._program)

    def color_from_reg(self):
        return [self._reg.hue, self._reg.saturation, self._reg.brightness,
                self._reg.kelvin]

    def color_to_reg(self, color):
        if color is not None:
            reg = self._reg
            reg.hue, reg.saturation, reg.brightness, reg.kelvin = color

    def _color(self): {
        Operand.ALL: self._color_all,
        Operand.LIGHT: self._color_light,
        Operand.GROUP: self._color_group,
        Operand.LOCATION: self._color_location,
        Operand.MZ_LIGHT: self._color_mz_light
    }[self._reg.operand]()

    @inject(LightSet)
    def _color_all(self, light_set):
        light_set.set_color(self._reg.get_color(), self._reg.duration)

    @inject(LightSet)
    def _color_light(self, light_set):
        light = light_set.get_light(self._reg.name)
        if light is None:
            Machine._report_missing(self._reg.name)
        else:
            light.set_color(self._reg.get_color(), self._reg.duration, True)
            
    @inject(LightSet)
    def _color_mz_light(self, light_set):
        light = light_set.get_light(self._reg.name)
        if light is None:
            Machine._report_missing(self._reg.name)
        elif self._zone_check(light):
            start_index, end_index = self._reg.zones
            light.set_zone_color(
                start_index, end_index, 
                self._reg.get_color(), self._reg.duration, True)

    @inject(LightSet)
    def _color_group(self, light_set):
        self._color_multiple(light_set.get_group(self._reg.name))

    @inject(LightSet)
    def _color_location(self, light_set):
        self._color_multiple(light_set.get_location(self._reg.name))

    def _color_multiple(self, lights):
        color = self._reg.get_color()
        for light in lights:
            light.set_color(color, self._reg.duration, True)

    def _power(self): {
        Operand.ALL: self._power_all,
        Operand.LIGHT: self._power_light,
        Operand.GROUP: self._power_group,
        Operand.LOCATION: self._power_location
    }[self._reg.operand]()

    @inject(LightSet)
    def _power_all(self, light_set):
        light_set.set_power(self._reg.get_power(), self._reg.duration)

    @inject(LightSet)
    def _power_light(self, light_set):
        light = light_set.get_light(self._reg.name)
        if light is None:
            Machine._report_missing(self._reg.name)
        else:
            light.set_power(self._reg.get_power(), self._reg.duration, True)

    @inject(LightSet)
    def _power_group(self, light_set):
        self._power_multiple(light_set.get_group(self._reg.name))

    @inject(LightSet)
    def _power_location(self, light_set):
        self._power_multiple(light_set.get_location(self._reg.name))

    def _power_multiple(self, lights):
        power = self._reg.get_power()
        for light in lights:
            light.set_power(power, self._reg.duration)

    @inject(LightSet)
    def _get_color(self, light_set):
        light = light_set.get_light(self._reg.name)
        if light is None:
            Machine._report_missing(self._reg.name)
        else:
            if self._reg.operand == Operand.MZ_LIGHT:
                if self._zone_check(light):
                    zone = self._reg.zones[0]
                    self.color_to_reg(light.get_color_zones(zone, zone + 1))[0]
            else:
                self.color_to_reg(light.get_color())
            
    def _nop(self): pass

    def _pause(self):
        if self._enable_pause:
            print("Press any to continue, q to quit, ! to run.")
            char = getch()
            if char == 'q':
                self.stop()
            else:
                print("Running...")
                if char == '!':
                    self._enable_pause = False

    def _check_wait(self):
        time = self._reg.time
        if isinstance(time, TimePattern):
            self._clock.wait_until(self._reg.time)
        elif time > 0:
            self._clock.pause_for(time / 1000.0)

    def _end(self):
        self.stop()

    def _set_reg(self):
        # param0 is the name of the register, param1 is its value.
        inst = self._program[self._pc]
        setattr(self._reg, inst.param0.name.lower(), inst.param1)

    def _time_pattern(self):
        inst = self._program[self._pc]
        if inst._param0 == SetOp.INIT:
            self._reg.time = inst._param1
        else:
            self._reg.time.union(inst._param1)

    def _time_wait(self):
        self._check_wait()

    def _zone_check(self, light):
        try:
            if not light.supports_multizone():
                logging.warning(
                    'Light "{}" is not multi-zone.'.format(light.get_label()))
                return False
        except WorkflowException:
            name = light.get_label()
            logging.warning(
                'Exception checking capability of "{}"'.format(name))
        return True

    @classmethod
    def _report_missing(cls, name):
        logging.warning("Light \"{}\" not found.".format(name))

    def _power_param(self):
        return 65535 if self._reg.power else 0
