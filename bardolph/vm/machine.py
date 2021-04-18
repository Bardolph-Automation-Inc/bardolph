import copy
import logging

from bardolph.controller import units
from bardolph.controller.get_key import getch
from bardolph.controller.i_controller import LightSet
from bardolph.controller.units import UnitMode
from bardolph.lib.i_lib import Clock, TimePattern
from bardolph.lib.injection import inject, injected, provide
from bardolph.lib.symbol import Symbol

from .call_stack import CallStack
from .loader import Loader
from .vm_codes import JumpCondition, LoopVar, OpCode, Operand, Register, SetOp
from .vm_discover import VmDiscover
from .vm_io import VmIo
from .vm_math import VmMath


class Registers:
    def __init__(self):
        self.blue = 0.0
        self.brightness = 0.0
        self.disc_forward = False
        self.duration = 0.0
        self.first_zone = 0
        self.green = 0.0
        self.hue = 0.0
        self.kelvin = 0.0
        self.last_zone = 0
        self.name = None
        self.operand = Operand.NULL
        self.pc = 0
        self.power = False
        self.red = 0.0
        self.result = None
        self.saturation = 0.0
        self.time = 0.0  # ms.
        self.unit_mode = UnitMode.LOGICAL

    def get_color(self):
        if self.unit_mode is not UnitMode.RGB:
            return [self.hue, self.saturation, self.brightness, self.kelvin]
        return [self.red, self.green, self.blue, self.kelvin]

    def store_color(self, color) -> None:
        if self.unit_mode is not UnitMode.RGB:
            self.hue, self.saturation, self.brightness, self.kelvin = color
        else:
            self.red, self.green, self.blue, self.kelvin = color

    def get_by_enum(self, reg):
        return getattr(self, reg.name.lower())

    def set_by_enum(self, reg, value):
        setattr(self, reg.name.lower(), value)

    def reset(self):
        self.__init__()

    def get_power(self):
        return 65535 if self.power else 0


class MachineState:
    def __init__(self, reg, call_stack):
        self.reg = reg
        self.call_stack = call_stack


class Machine:
    def __init__(self):
        self._cue_time = 0
        self._clock = provide(Clock)
        self._routines = {}
        self._program = []
        self._reg = Registers()
        self._call_stack = CallStack()
        self._vm_io = VmIo(self._call_stack, self._reg)
        self._vm_math = VmMath(self._call_stack, self._reg)
        self._vm_discover = VmDiscover(self._call_stack, self._reg)
        self._enable_pause = True
        self._keep_running = True
        excluded = (OpCode.STOP, OpCode.ROUTINE)
        op_codes = [code for code in OpCode
                    if not str(code.name).startswith('_')
                    and code not in excluded]
        self._fn_table = {
            op_code: getattr(self, '_' + op_code.name.lower())
            for op_code in (op_codes)}
        self._fn_table[OpCode.STOP] = self.stop

    def reset(self) -> None:
        self._reg.reset()
        self._routines.clear()
        self._cue_time = 0
        self._call_stack.reset()
        self._vm_math.reset()
        self._keep_running = True
        self._enable_pause = True

    def run(self, program) -> None:
        loader = Loader()
        loader.load(program, self._routines)
        self._program = loader.code
        self._keep_running = True

        logging.debug('Starting to execute.')
        self._clock.start()
        program_len = len(self._program)
        try:
            while self._keep_running and self._reg.pc < program_len:
                inst = self._program[self._reg.pc]
                if inst.op_code == OpCode.STOP:
                    break
                self._fn_table[inst.op_code]()
                if inst.op_code not in (OpCode.END, OpCode.JSR, OpCode.JUMP):
                    self._reg.pc += 1
            self._clock.stop()
            logging.debug(
                'Stopped, _keep_running = {}, _pc = {}, program_len = {}'
                .format(
                    self._keep_running, self._reg.pc, program_len))
        except Exception as ex:
            logging.error("Machine stopped due to {}".format(ex))

    def stop(self) -> None:
        self._keep_running = False
        self._clock.stop()

    def get_state(self) -> MachineState:
        return MachineState(self._reg, self._call_stack)

    def color_to_reg(self, color) -> None:
        reg = self._reg
        if reg.unit_mode in (UnitMode.RAW, UnitMode.LOGICAL):
            reg.hue, reg.saturation, reg.brightness, reg.kelvin = color
        else:
            reg.red, reg.green, reg.blue, reg.kelvin = color

    def color_from_reg(self):
        return self._reg.get_color()

    def get_variable(self, name):
        return self._call_stack.get_variable(name)

    @property
    def current_inst(self):
        return self._program[self._reg.pc]

    def _color(self) -> None:
        fn_map = {operand: fn for operand, fn in (
            (Operand.ALL, self._color_all),
            (Operand.LIGHT, self._color_light),
            (Operand.GROUP, self._color_group),
            (Operand.LOCATION, self._color_location),
            (Operand.MZ_LIGHT, self._color_mz_light))}
        fn_map[self._reg.operand]()

    @inject(LightSet)
    def _color_all(self, light_set=injected) -> None:
        color = self._assure_raw_color(self._reg.get_color())
        duration = self._assure_raw_time(self._reg.duration)
        light_set.set_color(color, duration)

    @inject(LightSet)
    def _color_light(self, light_set=injected) -> None:
        light = light_set.get_light(self._reg.name)
        if light is None:
            Machine._report_missing(self._reg.name)
        else:
            light.set_color(
                self._assure_raw_color(self._reg.get_color()),
                self._assure_raw_time(self._reg.duration))

    @inject(LightSet)
    def _color_mz_light(self, light_set=injected) -> None:
        light = light_set.get_light(self._reg.name)
        if light is None:
            Machine._report_missing(self._reg.name)
        elif self._zone_check(light):
            # Unknown why this happens.
            if not hasattr(light, 'set_zone_color'):
                logging.error(
                    'No set_zone_color for light of type', type(light))
            else:
                start_index = self._reg.first_zone
                end_index = self._reg.last_zone
                if end_index is None:
                    end_index = start_index
                light.set_zone_color(
                    start_index, end_index + 1,
                    self._assure_raw_color(self._reg.get_color()),
                    self._assure_raw_time(self._reg.duration))

    @inject(LightSet)
    def _color_group(self, light_set=injected) -> None:
        light_names = light_set.get_group(self._reg.name)
        if light_names is None:
            logging.warning("Unknown group: {}".format(self._reg.name))
        else:
            self._color_multiple(
                [light_set.get_light(name) for name in light_names])

    @inject(LightSet)
    def _color_location(self, light_set=injected) -> None:
        light_names = light_set.get_location(self._reg.name)
        if light_names is None:
            logging.warning("Unknown location: {}".format(self._reg.name))
        else:
            self._color_multiple(
                [light_set.get_light(name) for name in light_names])

    def _color_multiple(self, lights) -> None:
        color = self._assure_raw_color(self._reg.get_color())
        duration = self._assure_raw_time(self._reg.duration)
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
        duration = self._assure_raw_time(self._reg.duration)
        light_set.set_power(self._reg.get_power(), duration)

    @inject(LightSet)
    def _power_light(self, light_set=injected) -> None:
        light = light_set.get_light(self._reg.name)
        if light is None:
            Machine._report_missing(self._reg.name)
        else:
            duration = self._assure_raw_time(self._reg.duration)
            light.set_power(self._reg.get_power(), duration)

    @inject(LightSet)
    def _power_group(self, light_set=injected) -> None:
        light_names = light_set.get_group(self._reg.name)
        if light_names is None:
            logging.warning(
                'Power invoked for unknown group "{}"'.format(self._reg.name))
        else:
            self._power_multiple(
                [light_set.get_light(name) for name in light_names])

    @inject(LightSet)
    def _power_location(self, light_set=injected) -> None:
        light_names = light_set.get_location(self._reg.name)
        if light_names is None:
            logging.warning(
                "Power invoked for unknown location: {}".format(self._reg.name))
        else:
            self._power_multiple(
                [light_set.get_light(name) for name in light_names])

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
            if self._reg.operand is Operand.MZ_LIGHT:
                if self._zone_check(light):
                    zone = self._reg.first_zone
                    color = light.get_color_zones(zone, zone + 1)[0]
                    self.color_to_reg(self._maybe_converted_color(color))
            else:
                color = light.get_color()
                self.color_to_reg(self._maybe_converted_color(color))

    def _param(self) -> None:
        """
        param instruction: the name of the parameter is in param0, and its
        value is in param1. If the value is a Symbol or Register, it needs to
        be dereferenced.
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
        self._call_stack.set_return(self._reg.pc + 1)
        self._call_stack.push_current()
        routine_name = inst.param0
        rtn = self._routines.get(routine_name, None)
        self._reg.pc = rtn.get_address()

    def _end(self) -> None:
        self._call_stack.unwind_loops()
        ret_addr = self._call_stack.get_return()
        self._call_stack.pop_current()
        self._reg.pc = ret_addr

    def _jump(self) -> None:
        # In the current instruction, param0 contains the condition, and
        # param1 contains the offset.
        inst = self.current_inst
        if inst.param0 is JumpCondition.INDIRECT:
            address = self._call_stack.get_variable(inst.param1)
            self._reg.pc = address
        else:
            jump_if = {
                JumpCondition.ALWAYS: {True: True, False: True},
                JumpCondition.IF_FALSE: {True: False, False: True},
                JumpCondition.IF_TRUE: {True: True, False: False}
            }
            if jump_if[inst.param0][bool(self._reg.result)]:
                self._reg.pc += inst.param1
            else:
                self._reg.pc += 1

    def _loop(self) -> None:
        self._call_stack.enter_loop()

    def _end_loop(self) -> None:
        self._call_stack.exit_loop()

    def _nop(self) -> None: pass

    def _push(self) -> None:
        self._vm_math.push(self.current_inst.param0)

    def _pushq(self) -> None:
        self._vm_math.pushq(self.current_inst.param0)

    def _pop(self) -> None:
        self._vm_math.pop(self.current_inst.param0)

    def _op(self) -> None:
        self._vm_math.op(self.current_inst.param0)

    def _bin_op(self, operator) -> None:
        try:
            self._vm_math.bin_op(operator)
        except ZeroDivisionError:
            self._trigger_error("Division by zero. Halting execution.")
            self.stop()

    def _unary_op(self, operator) -> None:
        self._vm_math.unary_op(operator)

    def _disc(self) -> None:
        self._vm_discover.disc()

    def _discm(self) -> None:
            self._vm_discover.discm(self.current_inst.param0)

    def _dnext(self) -> None:
        self._vm_discover.dnext(self.current_inst.param0)

    def _dnextm(self) -> None:
        self._vm_discover.dnextm(
            self.current_inst.param0, self.current_inst.param1)

    def _out(self) -> None:
        self._vm_io.out(self.current_inst)

    def _pause(self) -> None:
        if self._enable_pause:
            print("Press any key to continue, q to quit, "
                  + "! to run without stopping again.")
            char = getch()
            if char == 'q':
                self.stop()
            else:
                print("Running...")
                if char == '!':
                    self._enable_pause = False

    def _constant(self) -> None:
        name = self.current_inst.param0
        value = self.current_inst.param1
        self._call_stack.put_constant(name, value)

    def _wait(self) -> None:
        time = self._reg.time
        if isinstance(time, TimePattern):
            self._clock.wait_until(time)
        elif time > 0:
            if self._reg.unit_mode is UnitMode.RAW:
                time /= 1000.0
            self._clock.pause_for(time)

    def _assure_raw_time(self, value) -> int:
        if self._reg.unit_mode in (UnitMode.LOGICAL, UnitMode.RGB):
            return units.time_raw(value)
        return value

    def _assure_raw_color(self, color):
        if self._reg.unit_mode is UnitMode.RAW:
            return color
        if self._reg.unit_mode is UnitMode.RGB:
            return units.rgb_to_raw(color)
        return units.logical_to_raw(color)

    def _maybe_converted_color(self, color):
        """
        The incoming color always consists of raw values.
        """
        if self._reg.unit_mode is UnitMode.RAW:
            return color
        if self._reg.unit_mode is UnitMode.LOGICAL:
            return units.raw_to_logical(color)
        return units.raw_to_rgb(color)

    def _move(self) -> None:
        """
        Move from variable/register to variable/register.
        """
        inst = self.current_inst
        value = inst.param0
        dest = inst.param1
        if isinstance(value, Register):
            value = self._reg.get_by_enum(value)
        elif isinstance(value, (str, LoopVar)):
            value = self._call_stack.get_variable(value)
        self._do_put_value(dest, value)

    def _moveq(self) -> None:
        """
        Move a value from the instruction itself into a register or variable.
        """
        value = self.current_inst.param0
        dest = self.current_inst.param1
        if dest is Register.UNIT_MODE:
            self._switch_unit_mode(value)
        else:
            self._do_put_value(dest, value)

    @staticmethod
    def _convert_units_fn(from_mode, to_mode):
        def key(mode0, mode1): return str(mode0) + str(mode1)
        converters = (
            (UnitMode.LOGICAL, UnitMode.RAW, units.logical_to_raw),
            (UnitMode.LOGICAL, UnitMode.RGB, units.logical_to_rgb),
            (UnitMode.RGB, UnitMode.RAW, units.rgb_to_raw),
            (UnitMode.RGB, UnitMode.LOGICAL, units.rgb_to_logical),
            (UnitMode.RAW, UnitMode.RGB, units.raw_to_rgb),
            (UnitMode.RAW, UnitMode.LOGICAL, units.raw_to_logical))
        convert_dict = {key(from_mode, to_mode): fn
                        for from_mode, to_mode, fn in converters}
        return convert_dict[key(from_mode, to_mode)]

    def _switch_unit_mode(self, to_mode) -> None:
        from_mode = self._reg.unit_mode
        if from_mode is to_mode:
            return

        original_color = self._reg.get_color()
        self._reg.unit_mode = to_mode
        converter = self._convert_units_fn(from_mode, to_mode)
        self._reg.store_color(converter(original_color))

        if to_mode is UnitMode.RAW:
            self._reg.duration = units.time_raw(self._reg.duration)
            self._reg.time = units.time_raw(self._reg.time)
        elif from_mode is UnitMode.RAW:
            self._reg.duration = units.time_logical(self._reg.duration)
            self._reg.time = units.time_logical(self._reg.time)

    def _do_put_value(self, dest, value) -> None:
        if isinstance(dest, Register):
            self._reg.set_by_enum(dest, value)
        else:
            self._call_stack.put_variable(dest, value)

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

    @staticmethod
    def _report_missing(name) -> None:
        logging.warning('Light "{}" not found.'.format(name))

    def _power_param(self):
        return 65535 if self._reg.power else 0

    def _breakpoint(self) -> None:
        print("At breakpoint.")

    def _trigger_error(self, message) -> bool:
        logging.error(message)
        return False
