#!/usr/bin/env python

import argparse
from numbers import Number

from bardolph.lib import injection
from bardolph.lib import settings
from bardolph.vm.vm_codes import Register

from . import arg_helper
from . import config_values
from . import light_module
from .i_controller import LightSet
from . import lsc
from . import units


def _quote_if_string(param):
    return ('{}' if isinstance(param, str) else "{:0.0f}").format(param)

class Snapshot:
    def start_snapshot(self): pass
    def start_light(self, light): pass
    def record_setting(self, name, value): pass
    def handle_power(self, power): pass
    def end_light(self): pass
    def end_snapshot(self): pass
    def start_multizone(self, light): pass
    def handle_zone(self, light, number, color): pass
    def end_multizone(self, light): pass

    def handle_color(self, color):
        self.record_setting(Register.HUE, color[0])
        self.record_setting(Register.SATURATION, color[1])
        self.record_setting(Register.BRIGHTNESS, color[2])
        self.record_setting(Register.KELVIN, color[3])

    def handle_zones(self, light):
        for number, color in enumerate(light.get_color_zones()):
            self.handle_zone(light, number, color)

    @injection.inject(LightSet)
    def generate(self, light_set):
        self.start_snapshot()
        for name in light_set.light_names:
            light = light_set.get_light(name)
            if light.multizone:
                self.start_multizone(light)
                self.handle_zones(light)
                self.end_multizone(light)
            else:
                self.start_light(light)
                self.handle_color(light.get_color())
                self.handle_power(light.get_power())
                self.end_light()
        self.end_snapshot()
        return self


class ScriptSnapshot(Snapshot):
    """ Generate a .ls _script. """
    def __init__(self):
        self._light_name = ''
        self._power = True
        self._script = ''

    def start_snapshot(self):
        self._script = 'time 0 duration 1.5\n'

    def start_light(self, light):
        self._light_name = light.name

    def record_setting(self, reg, value):
        self._script += '{} {} '.format(reg, value)

    def handle_color(self, raw_color):
        # Output is always logical units.
        logical_color = units.raw_to_logical(raw_color)
        params = zip([
            Register.HUE, Register.SATURATION, Register.BRIGHTNESS,
            Register.KELVIN], logical_color)
        for param in params:
            reg, value = param[0], param[1]
            fmt = '{} {:.0f} ' if isinstance(value, Number) else '{} {} '
            self._script += fmt.format(reg.name.lower(), value)

    def handle_power(self, power):
        self._power = power

    def end_light(self):
        self._script += 'set "{}"\n'.format(self._light_name)
        fmt = 'on "{}"\n' if self._power else 'off "{}"\n'
        self._script += fmt.format(self._light_name)

    def start_multizone(self, light):
        self._light_name = light.name
        self._power = light.get_power()

    def handle_zone(self, light, number, color):
        self.handle_color(color)
        self._script += 'set "{}" zone {}\n'.format(light.name, number)

    @property
    def text(self):
        return '{}\n'.format(self._script)


class InstructionSnapshot(Snapshot):
    """ Generate a list of lists, one for each light. """
    def __init__(self):
        self._light_name = ''
        self._snapshot = ''
        self._power = ''

    def start_snapshot(self):
        self._snapshot = ''

    def start_light(self, light):
        self._light_name = light.name

    def record_setting(self, reg, value):
        self._snapshot += '    OpCode.MOVEQ, {}, {},\n'.format(
            _quote_if_string(value), reg)

    def handle_power(self, power):
        self._power = power

    def end_light(self):
        self._snapshot += '    OpCode.MOVEQ, "{}", Register.NAME,\n'.format(
            self._light_name)
        self._snapshot += '    OpCode.MOVEQ, Operand.LIGHT, Register.OPERAND,\n'
        self._snapshot += '    OpCode.COLOR,\n'
        self._snapshot += '    OpCode.MOVEQ, {}, Register.POWER,\n'.format(
                            self._power)
        self._snapshot += '    OpCode.POWER,\n'

    @property
    def text(self):
        return self._snapshot[:-2]


class TextSnapshot(Snapshot):
    """ Generate plain text. """
    def __init__(self):
        self._field_width = 10
        self._text = ''
        self._add_field('name ')._add_field(' hue')
        self._add_field(' sat')._add_field(' brt')
        self._add_field(' kel')._add_field('power')
        self._text += '\n'
        self._text += '-' * ((self._field_width) * 6 - 5)
        self._text += '\n'

    def _add_field(self, data):
        self._text += str(data).ljust(self._field_width)
        return self

    @injection.inject(LightSet)
    def _add_sets(self, lights):
        self._add_set('Groups', lights.group_names, lights.get_group)
        self._add_set(
            'Locations', lights.location_names, lights.get_location)

    def _add_set(self, heading, names, get_fn):
        self._text += '\n{}\n'.format(heading)
        self._text += '-' * 15
        self._text += '\n'
        for name in names:
            self._text += '{}\n'.format(name)
            for light in get_fn(name):
                self._text += '   {}\n'.format(light)

    def generate(self):
        super().generate()
        self._add_sets()
        return self

    def start_light(self, light):
        self._add_field(light.name)

    def start_multizone(self, light):
        self.start_light(light)
        self._text += '{:>45}'.format(light.get_power())
        self._text += '\n   Zone\n'

    def handle_zone(self, _, number, color):
        self._add_field('{:>5d}'.format(number))
        self.handle_color(color)
        self._text += '\n'

    def end_zones(self, _):
        self._text += '\n'

    def handle_color(self, raw_color):
        logical_color = units.raw_to_logical(raw_color)
        for value in logical_color:
            self._add_field('{:>4.0f}'.format(value))

    def handle_power(self, power):
        self._add_field('{:d}'.format(power))

    def end_light(self):
        self._text += '\n'

    @property
    def text(self):
        return self._text


class DictSnapshot(Snapshot):
    """ Generate a list of dictionaries, one for each light. """
    def __init__(self):
        self._snapshot = None
        self._current_dict = None

    def start_snapshot(self):
        self._snapshot = []
        self._current_dict = {}

    def start_light(self, light):
        self._current_dict = {'_name': light.name}

    def record_setting(self, name, value):
        self._current_dict[name] = value

    def end_light(self):
        self._snapshot.append(self._current_dict)

    @property
    def snapshot(self):
        return self._snapshot

    @property
    def text(self):
        return str(self._current_dict)


def _do_gen(ctor):
    print(ctor().generate().text + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-l', '--list', help='output instruction list', action='store_true')
    parser.add_argument(
        '-d', '--dict', help='output dictionary format', action='store_true')
    parser.add_argument(
        '-f', '--use-fakes', help='use fake lights', action='store_true')
    arg_helper.add_n_argument(parser)
    parser.add_argument(
        '-p', '--py', help='output Python code', action='store_true')
    parser.add_argument(
        '-s', '--script', help='output script format', action='store_true')
    parser.add_argument(
        '-t', '--text', help='output text format', action='store_true')
    args = parser.parse_args()
    do_script = args.script
    do_dict = args.dict
    do_list = args.list
    do_py = args.py
    do_text = args.text or (not (do_py or do_script or do_dict or do_list))

    injection.configure()
    settings_init = settings.using(
        config_values.functional).add_overrides({'single_light_discover': True})
    settings_init.apply_env()

    if args.use_fakes:
        settings_init.add_overrides({'use_fakes': True})
    n_arg = arg_helper.get_overrides(args)
    if n_arg is not None:
        settings_init.add_overrides(n_arg)
    settings_init.configure()
    light_module.configure()

    if do_dict:
        _do_gen(DictSnapshot)
    if do_list:
        _do_gen(InstructionSnapshot)
    if do_script:
        _do_gen(ScriptSnapshot)
    if do_text:
        _do_gen(TextSnapshot)
    if do_py:
        snap = InstructionSnapshot()
        text = '    OpCode.MOVEQ, UnitMode.RAW, Register.UNIT_MODE,\n'
        text += snap.generate().text
        lsc.output_python(lsc.program_code(text))


if __name__ == '__main__':
    main()
