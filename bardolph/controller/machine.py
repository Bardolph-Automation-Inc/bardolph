import logging

from ..lib.i_lib import Clock, TimePattern
from ..lib.injection import inject, provide

from ..controller import units
from ..controller.units import UnitMode
from .get_key import getch
from .i_controller import LightSet
from .instruction import OpCode, Operand, SeriesOp, SetOp
from .series import Series


class Registers:
    def __init__(self):
        self.hue = 0
        self.saturation = 0
        self.brightness = 0
        self.kelvin = 0
        self.duration = 0
        self.first_zone = None
        self.last_zone = None
        self.power = False
        self.name = None
        self.operand = None
        self.series = None
        self.time = 0 # ms.
        self.unit_mode = UnitMode.LOGICAL

    def get_color(self):
        return [
            round(self.hue),
            round(self.saturation),
            round(self.brightness), 
            round(self.kelvin)
        ]

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
        self._reg_series = {}
        self._enable_pause = True
        self._fn_table = {
            OpCode.COLOR: self._color,
            OpCode.END: self._end,
            OpCode.GET_COLOR: self._get_color,
            OpCode.NOP: self._nop,
            OpCode.PAUSE: self._pause,
            OpCode.POWER: self._power,
            OpCode.SERIES: self._series,
            OpCode.SET_REG: self._set_reg,
            OpCode.STOP: self.stop,
            OpCode.TIME_PATTERN: self._time_pattern,
            OpCode.WAIT: self._wait
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
        return self._reg.get_color()

    def color_to_reg(self, color):
        if color is not None:
            reg = self._reg
            reg.hue, reg.saturation, reg.brightness, reg.kelvin = color
            self._reg_series.clear()

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
            light.set_color(self.color_from_reg(), self._reg.duration)
            
    @inject(LightSet)
    def _color_mz_light(self, light_set):
        light = light_set.get_light(self._reg.name)
        if light is None:
            Machine._report_missing(self._reg.name)
        elif self._zone_check(light):
            start_index = self._reg.first_zone
            end_index = self._reg.last_zone
            if end_index is None:
                end_index = start_index
            light.set_zone_color(
                start_index, end_index, 
                self._reg.get_color(), self._reg.duration)

    @inject(LightSet)
    def _color_group(self, light_set):
        lights = light_set.get_group(self._reg.name)
        if lights is None:
            logging.warning("Unknown group: {}".format(self._reg.name))
        else:
            self._color_multiple(lights)

    @inject(LightSet)
    def _color_location(self, light_set):
        lights = light_set.get_location(self._reg.name)
        if lights is None:
            logging.warning("Unknown location: {}".format(self._reg.name))
        else:
            self._color_multiple(lights)

    def _color_multiple(self, lights):
        color = self._reg.get_color()
        for light in lights:
            light.set_color(color, self._reg.duration)

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
            light.set_power(self._reg.get_power(), self._reg.duration)

    @inject(LightSet)
    def _power_group(self, light_set):
        lights = light_set.get_group(self._reg.name)
        if lights is None:
            logging.warning(
                'Power invoked for unknown group "{}"'.format(self._reg.name))
        else:
            self._power_multiple(light_set.get_group(self._reg.name))

    @inject(LightSet)
    def _power_location(self, light_set):
        lights = light_set.get_location(self._reg.name)
        if lights is None:
            logging.warning(
                "Power invoked for unknown location: {}".format(self._reg.name))
        else:
            self._power_multiple(lights)

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
                    zone = self._reg.first_zone
                    self.color_to_reg(light.get_color_zones(zone, zone + 1))[0]
            else:
                self.color_to_reg(light.get_color())

    def _series(self):
        inst = self._program[self._pc]
        if inst.param0 == SeriesOp.CLEAR:
            self._reg_series.clear()
        elif inst.param0 == SeriesOp.INIT:
            (start, delta) = inst.param1
            series = Series(start, delta)
            self._reg_series[self._reg.series] = series
        elif inst.param0 == SeriesOp.REMOVE:
            if self._reg.series in self._reg_series: 
                del self._reg_series[self._reg.series]
        elif inst.param0 == SeriesOp.NEXT:
            for reg in self._reg_series.keys():
                series = self._reg_series[reg]
                setattr(self._reg, reg.name.lower(), series.next())
            
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

    def _wait(self):
        time = self._reg.time
        if isinstance(time, TimePattern):
            self._clock.wait_until(time)
        elif time > 0:
            self._clock.pause_for(time / 1000.0)

    def _end(self):
        self.stop()

    def _set_reg(self):
        # param0 is the name of the register, param1 is its value.
        inst = self._program[self._pc]        
        reg = inst.param0
        value = inst.param1
    
        if (units.requires_conversion(reg) and
                self._reg.unit_mode == UnitMode.LOGICAL):
            value = units.as_raw(reg, value)
            if units.has_range(reg):
                (min_val, max_val) = units.get_range(reg)
                if value < min_val or value > max_val:
                    if self._unit_mode == UnitMode.LOGICAL:
                        min_val = units.as_logical(reg, min_val)
                        max_val = units.as_logical(reg, max_val)
                        return self._trigger_error(
                            '{} out of range'.format(reg.name.lower()))
        
        setattr(self._reg, inst.param0.name.lower(), value)
        return True

    def _time_pattern(self):
        inst = self._program[self._pc]
        if inst._param0 == SetOp.INIT:
            self._reg.time = inst._param1
        else:
            self._reg.time.union(inst._param1)

    def _zone_check(self, light):
        if not light.multizone:
            logging.warning(
                'Light "{}" is not multi-zone.'.format(light.name))
            return False
        return True

    @classmethod
    def _report_missing(cls, name):
        logging.warning("Light \"{}\" not found.".format(name))
            
    def _power_param(self):
        return 65535 if self._reg.power else 0
