import logging

from bardolph.lib.i_lib import Clock, TimePattern
from bardolph.lib.injection import inject, injected, provide
from bardolph.lib.symbol import Symbol

from bardolph.controller import units
from bardolph.controller.get_key import getch
from bardolph.controller.i_controller import LightSet
from bardolph.controller.units import UnitMode

from .call_stack import CallStack
from .loader import Loader
from .vm_codes import JumpCondition, OpCode, Operand, Register, SetOp
from .vm_math import VmMath

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
        self.result = None
        self.name = None
        self.operand = None
        self.time = 0  # ms.
        self.unit_mode = UnitMode.LOGICAL

    def get_color(self) -> [int]:
        return [
            round(self.hue),
            round(self.saturation),
            round(self.brightness),
            round(self.kelvin)
        ]

    def get_by_enum(self, reg):
        return getattr(self, reg.name.lower())

    def set_by_enum(self, reg, value):
        setattr(self, reg.name.lower(), value)

    def reset(self):
        self.__init__()

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
        self._call_stack = CallStack()
        self._vm_math = VmMath(self._call_stack, self._reg)
        self._enable_pause = True
        self._keep_running = True
        self._fn_table = {}
        for opcode in (OpCode.COLOR,
                       OpCode.CONSTANT,
                       OpCode.END,
                       OpCode.END_LOOP,
                       OpCode.GET_COLOR,
                       OpCode.JSR,
                       OpCode.JUMP,
                       OpCode.LOOP,
                       OpCode.MOVE,
                       OpCode.MOVEQ,
                       OpCode.NOP,
                       OpCode.OP,
                       OpCode.PARAM,
                       OpCode.PAUSE,
                       OpCode.PUSH,
                       OpCode.PUSHQ,
                       OpCode.POP,
                       OpCode.POWER,
                       OpCode.TIME_PATTERN,
                       OpCode.WAIT):
            name = '_' + opcode.name.lower()
            self._fn_table[opcode] = getattr(self, name)
        self._fn_table[OpCode.STOP] = self.stop

    def reset(self) -> None:
        self._reg.reset()
        self._variables.clear()
        self._pc = 0
        self._cue_time = 0
        self._call_stack.reset()
        self._vm_math.reset()
        self._keep_running = True
        self._enable_pause = True

    def run(self, program) -> None:
        loader = Loader()
        loader.load(program, self._variables)
        self._program = loader.code
        self._keep_running = True

        self._clock.start()
        while self._keep_running and self._pc < len(self._program):
            inst = self._program[self._pc]
            if inst.op_code == OpCode.STOP:
                break
            self._fn_table[inst.op_code]()
            if inst.op_code not in (OpCode.END, OpCode.JSR, OpCode.JUMP):
                self._pc += 1
        self._clock.stop()

    def interpret(self, input_stream) -> None:
        fn_table = self._fn_table.copy()
        for op_code in (OpCode.END,
                        OpCode.END_LOOP,
                        OpCode.JSR,
                        OpCode.JUMP,
                        OpCode.LOOP,
                        OpCode.PARAM):
            fn_table[op_code] = self._nop
        self._clock.start()
        for inst in input_stream:
            if inst.op_code == OpCode.STOP:
                break
            self._fn_table[inst.op_code]()
        self._clock.stop()

    def stop(self) -> None:
        self._keep_running = False
        self._clock.stop()

    def color_to_reg(self, color) -> None:
        reg = self._reg
        reg.hue, reg.saturation, reg.brightness, reg.kelvin = color

    def color_from_reg(self) -> [int]:
        return self._reg.get_color()

    def get_variable(self, name):
        return self._call_stack.get_variable(name)

    @property
    def current_inst(self):
        return self._program[self._pc]

    def _color(self) -> None: {
        Operand.ALL: self._color_all,
        Operand.LIGHT: self._color_light,
        Operand.GROUP: self._color_group,
        Operand.LOCATION: self._color_location,
        Operand.MZ_LIGHT: self._color_mz_light
    }[self._reg.operand]()

    @inject(LightSet)
    def _color_all(self, light_set=injected) -> None:
        color = self._assure_raw_color(self._reg.get_color())
        duration = self._assure_raw(Register.DURATION, self._reg.duration)
        light_set.set_color(color, duration)

    @inject(LightSet)
    def _color_light(self, light_set=injected) -> None:
        light = light_set.get_light(self._reg.name)
        if light is None:
            Machine._report_missing(self._reg.name)
        else:
            light.set_color(
                self._assure_raw_color(self._reg.get_color()),
                self._assure_raw(Register.DURATION, self._reg.duration))

    @inject(LightSet)
    def _color_mz_light(self, light_set=injected) -> None:
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
                self._assure_raw_color(self._reg.get_color()),
                self._assure_raw(Register.DURATION, self._reg.duration))

    @inject(LightSet)
    def _color_group(self, light_set=injected) -> None:
        lights = light_set.get_group(self._reg.name)
        if lights is None:
            logging.warning("Unknown group: {}".format(self._reg.name))
        else:
            self._color_multiple(lights)

    @inject(LightSet)
    def _color_location(self, light_set=injected) -> None:
        lights = light_set.get_location(self._reg.name)
        if lights is None:
            logging.warning("Unknown location: {}".format(self._reg.name))
        else:
            self._color_multiple(lights)

    def _color_multiple(self, lights) -> None:
        color = self._assure_raw_color(self._reg.get_color())
        duration = self._assure_raw(Register.DURATION, self._reg.duration)
        for light in lights:
            light.set_color(color, duration)

    def _power(self) -> None: {
        Operand.ALL: self._power_all,
        Operand.LIGHT: self._power_light,
        Operand.GROUP: self._power_group,
        Operand.LOCATION: self._power_location
    }[self._reg.operand]()

    @inject(LightSet)
    def _power_all(self, light_set=injected) -> None:
        duration = self._assure_raw(Register.DURATION, self._reg.duration)
        light_set.set_power(self._reg.get_power(), duration)

    @inject(LightSet)
    def _power_light(self, light_set=injected) -> None:
        light = light_set.get_light(self._reg.name)
        if light is None:
            Machine._report_missing(self._reg.name)
        else:
            duration = self._assure_raw(Register.DURATION, self._reg.duration)
            light.set_power(self._reg.get_power(), duration)

    @inject(LightSet)
    def _power_group(self, light_set=injected) -> None:
        lights = light_set.get_group(self._reg.name)
        if lights is None:
            logging.warning(
                'Power invoked for unknown group "{}"'.format(self._reg.name))
        else:
            self._power_multiple(light_set.get_group(self._reg.name))

    @inject(LightSet)
    def _power_location(self, light_set=injected) -> None:
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
    def _get_color(self, light_set=injected) -> None:
        light = light_set.get_light(self._reg.name)
        if light is None:
            Machine._report_missing(self._reg.name)
        else:
            if self._reg.operand == Operand.MZ_LIGHT:
                if self._zone_check(light):
                    zone = self._reg.first_zone
                    color = light.get_color_zones(zone, zone + 1)[0]
                    self.color_to_reg(self._maybe_logical_color(color))
            else:
                self.color_to_reg(self._maybe_logical_color(light.get_color()))

    def _param(self) -> None:
        """
        param instruction: the name of the routine's parameter is in param0.
        If the parameter is itself an incoming parameter, it needs to be
        resolved to a real value before being put on the stack.
        """
        inst = self.current_inst
        value = inst.param1
        if isinstance(value, Symbol):
            value = self._call_stack.get_variable(value.name)
        elif isinstance(value, Register):
            value = self._reg.get_by_enum(value)
        self._call_stack.put_param(inst.param0, value)

    def _jsr(self) -> None:
        inst = self.current_inst
        self._call_stack.set_return(self._pc + 1)
        self._call_stack.push_current()
        routine_name = inst.param0
        rtn = self._variables.get(routine_name, None)
        self._pc = rtn.get_address()

    def _jump(self) -> None:
        # In the current instruction, param0 contains the condition, and
        # param1 contains the offset.
        inst = self.current_inst
        jump_if = {
            JumpCondition.ALWAYS: {True: True, False: True},
            JumpCondition.IF_FALSE: {True: False, False: True},
            JumpCondition.IF_TRUE: {True: True, False: False}
        }
        if jump_if[inst.param0][bool(self._reg.result)]:
            self._pc += inst.param1
        else:
            self._pc += 1

    def _loop(self) -> None:
        self._call_stack.enter_loop()

    def _end_loop(self) -> None:
        self._call_stack.exit_loop()

    def _end(self) -> None:
        ret_addr = self._call_stack.get_return()
        self._call_stack.pop_current()
        self._pc = ret_addr

    def _nop(self) -> None: pass

    def _push(self):
        return self._vm_math.push(self.current_inst.param0)

    def _pushq(self):
        return self._vm_math.pushq(self.current_inst.param0)

    def _pop(self):
        return self._vm_math.pop(self.current_inst.param0)

    def _op(self):
        return self._vm_math.op(self.current_inst.param0)

    def _bin_op(self, operator):
        return self._vm_math.bin_op(operator)

    def _unary_op(self, operator):
        return self._vm_math.unary_op(operator)

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

    def _constant(self):
        name = self.current_inst.param0
        value = self.current_inst.param1
        self._call_stack.put_constant(name, value)

    def _wait(self) -> None:
        time = self._reg.time
        if isinstance(time, TimePattern):
            self._clock.wait_until(time)
        elif time > 0:
            self._clock.pause_for(time / 1000.0)

    def _assure_raw(self, reg, value) -> int:
        """
        If in logical mode, convert incoming value to raw units. If not in
        logical mode, no conversion is necessary.
        """
        if (self._reg.unit_mode == UnitMode.LOGICAL
                and units.requires_conversion(reg)):
            return units.as_raw(reg, value)
        if (self._reg.unit_mode == UnitMode.RAW and reg == Register.HUE
                and value > 65535):
            value %= 65536
        return value

    def _assure_raw_color(self, color) -> [int]:
        if self._reg.unit_mode == UnitMode.RAW:
            return color
        result = 4 * [0]
        result[0] = units.as_raw(Register.HUE, color[0])
        result[1] = units.as_raw(Register.SATURATION, color[1])
        result[2] = units.as_raw(Register.BRIGHTNESS, color[2])
        result[3] = color[3]
        return result

    def _maybe_logical(self, reg, value) -> int:
        """
        If in logical mode, convert incoming value to logical units. If not
        in logical mode, or for some registers, no conversion is necessary.

        Typically, the incoming value comes from a register, which always
        contains a raw value.
        """
        if (self._reg.unit_mode == UnitMode.LOGICAL
                and units.requires_conversion(reg)):
            return units.as_logical(reg, value)
        if reg == Register.HUE and value > 360:
            value %= 360
        return value

    def _maybe_logical_color(self, color) -> [int]:
        if self._reg.unit_mode == UnitMode.LOGICAL:
            return color
        result = 4 * [0]
        result[0] = units.as_logical(Register.HUE, color[0])
        result[1] = units.as_logical(Register.SATURATION, color[1])
        result[2] = units.as_logical(Register.BRIGHTNESS, color[2])
        result[3] = color[3]
        return result

    def _move(self) -> bool:
        """
        Move from variable/register to variable/register.
        """
        inst = self.current_inst
        srce = inst.param0
        dest = inst.param1
        if isinstance(srce, Register):
            value = self._reg.get_by_enum(srce)
        else:
            value = self._call_stack.get_variable(srce)
            if value is None:
                return self._trigger_error('Unknown: "{}"'.format(srce))
        return self._do_put_value(dest, value)

    def _moveq(self) -> bool:
        """
        Move a value from the instruction itself into a register or variable.
        """
        value = self.current_inst.param0
        dest = self.current_inst.param1
        if dest == Register.UNIT_MODE:
            if self._reg.unit_mode != value:
                fn = (units.as_logical if value == UnitMode.LOGICAL
                      else units.as_raw)
                self._reg.hue = fn(Register.HUE, self._reg.hue)
                self._reg.saturation = fn(
                    Register.SATURATION, self._reg.saturation)
                self._reg.brightness = fn(Register.HUE, self._reg.hue)
        return self._do_put_value(dest, value)

    def _do_put_value(self, dest, value) -> bool:
        if isinstance(dest, Register):
            self._reg.set_by_enum(dest, value)
        else:
            self._call_stack.put_variable(dest, value)
        return True

    def _time_pattern(self) -> None:
        inst = self.current_inst
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

    @classmethod
    def _breakpoint(cls):
        breakpoint()

    def _trigger_error(self, message) -> bool:
        logging.error(message)
        return False
