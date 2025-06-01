import logging

from bardolph.controller import units
from bardolph.controller.color_matrix import ColorMatrix
from bardolph.controller.color_matrix import Rect
from bardolph.controller.get_key import getch
from bardolph.controller.i_controller import (LightSet, MatrixLight,
                                              MultizoneLight)
from bardolph.controller.routine import RuntimeRoutine
from bardolph.controller.units import UnitMode
from bardolph.lib.i_lib import Clock, TimePattern
from bardolph.lib.injection import inject, provide
from bardolph.lib.symbol import Symbol
from bardolph.vm.array import Array
from bardolph.vm.call_stack import CallStack
from bardolph.vm.loader import Loader
from bardolph.vm.vm_codes import (JumpCondition, LoopVar, OpCode, Operand,
                                  Register, SetOp)
from bardolph.vm.vm_discover import VmDiscover
from bardolph.vm.vm_io import VmIo
from bardolph.vm.vm_math import VmMath


class Registers:
    def __init__(self):
        self.blue = 0.0
        self.brightness = 0.0
        self.default = None
        self.disc_forward = False
        self.duration = 0.0
        self.first_column = None
        self.first_row = None
        self.first_zone = 0
        self.green = 0.0
        self.hue = 0.0
        self.kelvin = 0.0
        self.last_column = None
        self.last_row = None
        self.last_zone = 0
        self.matrix = None
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
        op_codes = [code for code in OpCode if code not in excluded]
        self._fn_table = {
            op_code: getattr(self, '_' + op_code.name.lower(), self._unimpl)
            for op_code in (op_codes)
        }
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
        loader.load(program)
        self._routines = loader.get_routines()
        self._program = loader.get_code()
        self._keep_running = True

        logging.debug('Starting to execute.')
        self._clock.start()
        program_len = len(self._program)
        try:
            while self._keep_running and self._reg.pc < program_len:
                inst = self._program[self._reg.pc]
                if inst.op_code == OpCode.STOP:
                    break
                fn = self._fn_table[inst.op_code]
                fn()
                if inst.op_code not in (OpCode.END, OpCode.JSR, OpCode.JUMP):
                    self._reg.pc += 1
            self._clock.stop()
            self._vm_io.flush()
            logging.debug(
                'Stopped, _keep_running = {}, _pc = {}, program_len = {}'
                .format(
                    self._keep_running, self._reg.pc, program_len))
        except Exception as ex:
            logging.error("Machine stopped due to {} at instruction {}"
                          .format(ex, self._reg.pc))

    def stop(self) -> None:
        self._keep_running = False
        self._clock.stop()

    def get_state(self) -> MachineState:
        return MachineState(self._reg, self._call_stack)

    def get_variable(self, name):
        return self._call_stack.get_variable(name)

    @property
    def current_inst(self):
        return self._program[self._reg.pc]

    def _param_value(self, value):
        if isinstance(value, Register):
            return self._reg.get_by_enum(value)
        elif isinstance(value, (str, LoopVar)):
            return self._call_stack.get_variable(value)
        return value

    def _color_to_reg(self, color) -> None:
        reg = self._reg
        if reg.unit_mode is UnitMode.RGB:
            reg.red, reg.green, reg.blue, reg.kelvin = color
        else:
            reg.hue, reg.saturation, reg.brightness, reg.kelvin = color

    def _color_from_reg(self):
        return self._reg.get_color()

    def _color(self) -> None:
        fn_map = {operand: fn for operand, fn in (
            (Operand.ALL, self._color_all),
            (Operand.DEFAULT, self._color_default),
            (Operand.LIGHT, self._color_light),
            (Operand.GROUP, self._color_group),
            (Operand.LOCATION, self._color_location),
            (Operand.MATRIX, self._color_matrix),
            (Operand.MATRIX_LIGHT, self._color_matrix_light),
            (Operand.MZ_LIGHT, self._color_mz_light))}
        fn_map[self._reg.operand]()

    @inject(LightSet)
    def _get_named_light(self, light_set) -> None:
        light = light_set.get_light(self._reg.name)
        if light is None:
            Machine._report_missing(self._reg.name)
        return light

    @inject(LightSet)
    def _color_all(self, light_set) -> None:
        color = self._as_raw_color(self._reg.get_color())
        duration = self._as_raw_time(self._reg.duration)
        light_set.set_color_all_lights(color, duration)

    def _color_light(self) -> None:
        light = self._get_named_light()
        if light is not None:
            light.set_color(
                self._as_raw_color(self._reg.get_color()),
                self._as_raw_time(self._reg.duration))

    def _color_matrix(self) -> None:
        color = self._reg.get_color()
        mat = self._reg.matrix
        rect = Rect(
            self._reg.first_row, self._reg.last_row,
            self._reg.first_column, self._reg.last_column)
        mat.overlay_color(rect, color)

    def _color_matrix_light(self) -> None:
        light = self._get_named_light()
        if light is not None:
            matrix = self._reg.matrix
            matrix = self._as_raw_matrix(matrix)
            matrix.find_replace(None, self._reg.default or [0, 0, 0, 0])
            duration = self._as_raw_time(self._reg.duration)
            light.set_matrix(matrix, duration)

    def _color_mz_light(self) -> None:
        light = self._get_named_light()
        if light is not None and self._zone_check(light):
            start_index = self._reg.first_zone
            end_index = self._reg.last_zone
            if end_index is None:
                end_index = start_index
            light.set_zone_colors(
                start_index, end_index + 1,
                self._as_raw_color(self._reg.get_color()),
                self._as_raw_time(self._reg.duration))

    @inject(LightSet)
    def _color_group(self, light_set) -> None:
        light_names = light_set.get_group_lights(self._reg.name)
        if light_names is None:
            logging.warning("Unknown group: {}".format(self._reg.name))
        else:
            self._color_multiple(
                [light_set.get_light(name) for name in light_names])

    @inject(LightSet)
    def _color_location(self, light_set) -> None:
        light_names = light_set.get_location_lights(self._reg.name)
        if light_names is None:
            logging.warning("Unknown location: {}".format(self._reg.name))
        else:
            self._color_multiple(
                [light_set.get_light(name) for name in light_names])

    def _color_multiple(self, lights) -> None:
        color = self._as_raw_color(self._reg.get_color())
        duration = self._as_raw_time(self._reg.duration)
        for light in lights:
            light.set_color(color, duration)

    def _color_default(self) -> None:
        # The "default" register must always contain raw values.
        self._reg.default = self._as_raw_color(self._reg.get_color())

    def _power(self) -> None:
        {
            Operand.ALL: self._power_all,
            Operand.LIGHT: self._power_light,
            Operand.GROUP: self._power_group,
            Operand.LOCATION: self._power_location
        }[self._reg.operand]()

    @inject(LightSet)
    def _power_all(self, light_set) -> None:
        duration = self._as_raw_time(self._reg.duration)
        light_set.set_power_all_lights(self._reg.get_power(), duration)

    @inject(LightSet)
    def _power_light(self, light_set) -> None:
        light = light_set.get_light(self._reg.name)
        if light is None:
            Machine._report_missing(self._reg.name)
        else:
            duration = self._as_raw_time(self._reg.duration)
            light.set_power(self._reg.get_power(), duration)

    @inject(LightSet)
    def _power_group(self, light_set) -> None:
        light_names = light_set.get_group_lights(self._reg.name)
        if light_names is None:
            logging.warning(
                'Power invoked for unknown group "{}"'.format(self._reg.name))
        else:
            self._power_multiple(
                [light_set.get_light(name) for name in light_names])

    @inject(LightSet)
    def _power_location(self, light_set) -> None:
        light_names = light_set.get_location_lights(self._reg.name)
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
    def _get_color(self, light_set) -> None:
        name = self._reg.name
        light = light_set.get_light(name)
        if light is None:
            Machine._report_missing(name)
        else:
            if isinstance(light, (MultizoneLight, MatrixLight)):
                fmt = 'Unable to retrieve color from multi-color light "{}".'
                logging.warning(fmt.format(name))
            else:
                color = light.get_color()
                self._color_to_reg(self._assure_units(color))

    def _ctx(self) -> None:
        self._call_stack.new_frame()

    def _end_ctx(self) -> None:
        pass

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
        self._call_stack.enter_routine()
        inst = self.current_inst
        self._call_stack.set_return(self._reg.pc + 1)
        routine_name = inst.param0
        rtn = self._routines.get(routine_name, None)
        if isinstance(rtn, RuntimeRoutine):
            self._vm_math.pushq(rtn.invoke(self._call_stack.get_top()))
            self._return()
        else:
            self._reg.pc = rtn.get_address()

    def _end(self) -> None:
        if self.current_inst.param0 is Operand.MATRIX:
            self._reg.pc += 1
        else:
            self._return()

    def _return(self) -> None:
        self._call_stack.unwind_loops()
        self._reg.pc = self._call_stack.get_return()
        self._call_stack.exit_routine()

    def _jump(self) -> None:
        inst = self.current_inst
        match inst.param0:
            case JumpCondition.INDIRECT:
                address = self._call_stack.get_variable(inst.param1)
                self._reg.pc = address
            case JumpCondition.ALWAYS:
                self._reg.pc += inst.param1
            case JumpCondition.IF_FALSE | JumpCondition.IF_TRUE:
                self._vm_math.pop(Register.RESULT)
                if (bool(self._reg.result) ^
                        (inst.param0 is JumpCondition.IF_FALSE)):
                    self._reg.pc += inst.param1
                else:
                    self._reg.pc += 1

    def _loop(self) -> None:
        self._call_stack.enter_loop()

    def _end_loop(self) -> None:
        self._call_stack.exit_loop()

    @inject(LightSet)
    def _matrix(self, light_set) -> None:
        name = self._reg.name
        light = light_set.get_light(name)
        if light is None:
            Machine._report_missing(name)
            height = width = 255
        elif not isinstance(light, MatrixLight):
            logging.error(
                'Light "{}" is not matrix type (Candle, Tube, etc.)'
                .format(name))
            height = width = 255
        else:
            height = light.get_height()
            width = light.get_width()
        self._reg.matrix = ColorMatrix.new_from_constant(height, width, None)

    def _array(self):
        array_name = self.current_inst.param0
        array_len = self._param_value(self.current_inst.param1)
        stack_top = self._call_stack.get_top()
        var = stack_top.get_variable(array_name)
        if var is None:
            self._call_stack.put_variable(array_name, Array(array_len))
        else:
            var.add_dimension(array_len)
        return True

    def _deref(self):
        # Should put the result on the top of the expression stack.
        offset = self._param_value(self.current_inst.param1)
        array_name = self.current_inst.param0
        array = self._call_stack.get_variable(array_name)
        array.deref(offset)
        return True

    def _index(self):
        # Should put the result on the top of the expression stack.
        offset = self._param_value(self.current_inst.param1)
        array_name = self.current_inst.param0
        array = self._call_stack.get_variable(array_name)
        array.index(offset)
        return True

    def _nop(self) -> bool:
        return True

    def _unimpl(self) -> bool:
        logging.debug("Machine._unimpl() called")
        return True

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

    def _as_raw_time(self, value) -> int:
        if self._reg.unit_mode in (UnitMode.LOGICAL, UnitMode.RGB):
            return units.time_raw(value)
        return value

    def _as_raw_color(self, color):
        if self._reg.unit_mode is UnitMode.RAW:
            return color
        if self._reg.unit_mode is UnitMode.RGB:
            return units.rgb_to_raw(color)
        return units.logical_to_raw(color)

    def _as_raw_matrix(self, srce):
        if self._reg.unit_mode is UnitMode.RAW:
            return srce
        xform_fn = units.convert_fn(self._reg.unit_mode, UnitMode.RAW)
        return ColorMatrix.new_from_iterable(srce.height, srce.width,
            (xform_fn(color) for color in srce.get_colors()))

    def _assure_units(self, color):
        """
        The incoming color always consists of raw values.
        """
        if self._reg.unit_mode is UnitMode.RAW:
            return color
        if self._reg.unit_mode is UnitMode.LOGICAL:
            return units.raw_to_logical(color)
        return units.raw_to_rgb(color)

    def _assure_units_matrix(self, srce):
        if self._reg.unit_mode is UnitMode.RAW:
            return srce

        xform_fn = units.convert_fn(UnitMode.RAW, self._reg.unit_mode)
        return ColorMatrix.new_from_iterable(
            (xform_fn(color) for color in srce.as_list()), 6, 5)

    def _move(self) -> None:
        # Move from variable/register to variable/register.
        inst = self.current_inst
        value, dest = inst.param0, inst.param1
        if isinstance(value, Register):
            value = self._reg.get_by_enum(value)
        elif isinstance(value, (str, LoopVar)):
            value = self._call_stack.get_variable(value)
            ### if isinstance(value, Array, ArrayBranch):
            ###    value = value.get_value()
        self._do_put_value(dest, value)

    def _moveq(self) -> None:
        # Copy a literal value within the instruction to a register or variable.
        inst = self.current_inst
        value, dest = inst.param0, inst.param1
        if dest is Register.UNIT_MODE:
            self._switch_unit_mode(value)
        else:
            self._do_put_value(dest, value)

    def _do_put_value(self, dest, value) -> None:
        if isinstance(dest, Register):
            self._reg.set_by_enum(dest, value)
        else:
            current_value = self._call_stack.get_variable(dest)
            ### if isinstance(current_value, Array):
            ###     current_value.set_value(value)
            ### else:
            self._call_stack.put_variable(dest, value) ###

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

    def _time_pattern(self) -> None:
        inst = self.current_inst
        if inst.param0 == SetOp.INIT:
            self._reg.time = inst.param1
        else:
            self._reg.time.union(inst.param1)

    def _zone_check(self, light) -> bool:
        if not isinstance(light, MultizoneLight):
            logging.warning(
                'Light "{}" is not multi-zone.'.format(light.get_name()))
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
