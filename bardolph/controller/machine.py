import logging

from ..lib.i_lib import Clock, TimePattern
from ..lib.injection import inject, provide
from ..lib.symbol import Symbol, SymbolType

from . import units
from .call_stack import CallStack
from .get_key import getch
from .i_controller import LightSet
from .instruction import OpCode, Operand, SetOp
from .loader import Loader
from .units import UnitMode

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
        self.time = 0  # ms.
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
        self._call_stack = CallStack()
        self._enable_pause = True
        self._fn_table = {
            OpCode.CALL: self._call,
            OpCode.COLOR: self._color,
            OpCode.END: self._end,
            OpCode.GET_COLOR: self._get_color,
            OpCode.JUMP: self._jump,
            OpCode.MOVE: self._move,
            OpCode.MOVEQ: self._moveq,
            OpCode.NOP: self._nop,
            OpCode.PARAM: self._param,
            OpCode.PAUSE: self._pause,
            OpCode.POWER: self._power,
            OpCode.STOP: self.stop,
            OpCode.TIME_PATTERN: self._time_pattern,
            OpCode.WAIT: self._wait
        }

    def run(self, program) -> None:
        self._variables.clear()
        loader = Loader()
        loader.load(program, self._variables)
        self._program = loader.code
        self._pc = 0
        self._cue_time = 0
        self._call_stack.clear()
        self._clock.start()
        while self._pc < len(self._program):
            inst = self._program[self._pc]
            if inst.op_code == OpCode.STOP:
                break
            self._fn_table[inst.op_code]()
            if inst.op_code not in (OpCode.CALL, OpCode.END, OpCode.JUMP):
                self._pc += 1
        self._clock.stop()

    def stop(self) -> None:
        self._pc = len(self._program)

    def color_from_reg(self) -> [int]:
        return self._reg.get_color()

    def color_to_reg(self, color) -> None:
        if color is not None:
            reg = self._reg
            reg.hue, reg.saturation, reg.brightness, reg.kelvin = color
            self._reg_series.clear()

    def _color(self) -> None: {
        Operand.ALL: self._color_all,
        Operand.LIGHT: self._color_light,
        Operand.GROUP: self._color_group,
        Operand.LOCATION: self._color_location,
        Operand.MZ_LIGHT: self._color_mz_light
    }[self._reg.operand]()

    @inject(LightSet)
    def _color_all(self, light_set) -> None:
        light_set.set_color(self._reg.get_color(), self._reg.duration)

    @inject(LightSet)
    def _color_light(self, light_set) -> None:
        light = light_set.get_light(self._reg.name)
        if light is None:
            Machine._report_missing(self._reg.name)
        else:
            light.set_color(self.color_from_reg(), self._reg.duration)

    @inject(LightSet)
    def _color_mz_light(self, light_set) -> None:
        light = light_set.get_light(self._reg.name)
        if light is None:
            Machine._report_missing(self._reg.name)
        elif self._zone_check(light):
            start_index = self._reg.first_zone
            end_index = self._reg.last_zone
            if end_index is None:
                end_index = start_index
            light.set_zone_color(
                start_index, end_index + 1,
                self._reg.get_color(), self._reg.duration)

    @inject(LightSet)
    def _color_group(self, light_set) -> None:
        lights = light_set.get_group(self._reg.name)
        if lights is None:
            logging.warning("Unknown group: {}".format(self._reg.name))
        else:
            self._color_multiple(lights)

    @inject(LightSet)
    def _color_location(self, light_set) -> None:
        lights = light_set.get_location(self._reg.name)
        if lights is None:
            logging.warning("Unknown location: {}".format(self._reg.name))
        else:
            self._color_multiple(lights)

    def _color_multiple(self, lights) -> None:
        color = self._reg.get_color()
        for light in lights:
            light.set_color(color, self._reg.duration)

    def _power(self) -> None: {
        Operand.ALL: self._power_all,
        Operand.LIGHT: self._power_light,
        Operand.GROUP: self._power_group,
        Operand.LOCATION: self._power_location
    }[self._reg.operand]()

    @inject(LightSet)
    def _power_all(self, light_set) -> None:
        light_set.set_power(self._reg.get_power(), self._reg.duration)

    @inject(LightSet)
    def _power_light(self, light_set) -> None:
        light = light_set.get_light(self._reg.name)
        if light is None:
            Machine._report_missing(self._reg.name)
        else:
            light.set_power(self._reg.get_power(), self._reg.duration)

    @inject(LightSet)
    def _power_group(self, light_set) -> None:
        lights = light_set.get_group(self._reg.name)
        if lights is None:
            logging.warning(
                'Power invoked for unknown group "{}"'.format(self._reg.name))
        else:
            self._power_multiple(light_set.get_group(self._reg.name))

    @inject(LightSet)
    def _power_location(self, light_set) -> None:
        lights = light_set.get_location(self._reg.name)
        if lights is None:
            logging.warning(
                "Power invoked for unknown location: {}".format(self._reg.name))
        else:
            self._power_multiple(lights)

    def _power_multiple(self, lights) -> None:
        power = self._reg.get_power()
        for light in lights:
            light.set_power(power, self._reg.duration)

    @inject(LightSet)
    def _get_color(self, light_set) -> None:
        light = light_set.get_light(self._reg.name)
        if light is None:
            Machine._report_missing(self._reg.name)
        else:
            if self._reg.operand == Operand.MZ_LIGHT:
                if self._zone_check(light):
                    zone = self._reg.first_zone
                    self.color_to_reg(light.get_color_zones(zone, zone + 1)[0])
            else:
                self.color_to_reg(light.get_color())

    def _param(self) -> None:
        """
        param instruction: the name of the routine's parameter is in param0.
        If the parameter is itself an incoming parameter, it needs to be
        resolved to a real value before being put on the stack.
        """
        inst = self._program[self._pc]
        value = inst.param1
        if isinstance(value, Symbol) and value.symbol_type == SymbolType.VAR:
            value = self._call_stack.get_variable(value.name)
        self._call_stack.add_param(inst.param0, value)

    def _call(self) -> None:
        inst = self._program[self._pc]
        self._call_stack.set_return(self._pc + 1)
        self._call_stack.push_current()
        routine_name = inst.param0
        rtn = self._variables.get(routine_name, None)
        self._pc = rtn.get_address()

    def _end(self) -> None:
        ret_addr = self._call_stack.get_return()
        self._call_stack.pop_current()
        self._pc = ret_addr

    def _nop(self): pass

    def _jump(self) -> None:
        self._pc = self._program[self._pc].param0

    def _pause(self) -> None:
        if self._enable_pause:
            print("Press any to continue, q to quit, ! to run.")
            char = getch()
            if char == 'q':
                self.stop()
            else:
                print("Running...")
                if char == '!':
                    self._enable_pause = False

    def _wait(self) -> None:
        time = self._reg.time
        if isinstance(time, TimePattern):
            self._clock.wait_until(time)
        elif time > 0:
            self._clock.pause_for(time / 1000.0)

    def _unit_check(self, reg, value) -> int:
        """
        If necessary, convert from logical to raw units. Check the range of
        the value if appropriate.
        """
        if (self._reg.unit_mode == UnitMode.LOGICAL
                and units.requires_conversion(reg)):
            value = units.as_raw(reg, value)
        if units.has_range(reg):
            min_val, max_val = units.get_range(reg)
            if not min_val <= value <= max_val:
                self._trigger_error('{} out of range'.format(reg.name.lower()))
                return None
        return value

    def _move(self) -> bool:
        """
        Inside a routine, move a value from a parameter into a register.

        Within the instruction, param0 is the name of a parameter, while param1
        is the destination register.
        """
        inst = self._program[self._pc]
        name = inst.param0
        value = self._call_stack.get_variable(name)
        if value is None:
            return self._trigger_error('Unknown: "{}"'.format(name))

        reg = inst.param1
        value = self._unit_check(reg, value)
        if value is None:
            return False
        setattr(self._reg, reg.name.lower(), value)
        return True

    def _moveq(self) -> bool:
        """
        Move a value from the instruction itself into a register.

        Within the instruction, param0 is the source literal value, while param1
        is the destination register.
        """
        inst = self._program[self._pc]
        reg = inst.param1
        if inst.param0 is None:
            value = None
        else:
            value = self._unit_check(reg, inst.param0)
            if value is None:
                return False
        setattr(self._reg, reg.name.lower(), value)
        return True

    def _time_pattern(self) -> None:
        inst = self._program[self._pc]
        if inst.param0 == SetOp.INIT:
            self._reg.time = inst.param1
        else:
            self._reg.time.union(inst.param1)

    def _zone_check(self, light) -> bool:
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

    def _trigger_error(self, message) -> bool:
        logging.error(message)
        return False
