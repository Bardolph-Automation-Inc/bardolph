#!/usr/bin/env python

import argparse

from ..lib import injection
from ..lib import settings
from ..parser.token_types import TokenTypes

from . import config_values
from . import light_module
from .i_controller import LightSet
from .lsc import Compiler
from .units import Units


def _quote_if_string(param):
    return '{}'.format(param) if isinstance(param, str) else param

class Snapshot:
    def start_snapshot(self): pass
    def start_light(self, light): pass
    def handle_setting(self, name, value): pass
    def handle_power(self, power): pass
    def end_light(self): pass
    def end_snapshot(self): pass

    def handle_color(self, color):
        self.handle_setting('hue', color[0])
        self.handle_setting('saturation', color[1])
        self.handle_setting('brightness', color[2])
        self.handle_setting('kelvin', color[3])

    @injection.inject(LightSet)
    def generate(self, light_set):
        self.start_snapshot()
        for name in light_set.light_names:
            light = light_set.get_light(name)
            self.start_light(light)
            self.handle_color(light.get_color())
            self.handle_power(light.get_power())
            self.end_light()
        self.end_snapshot()
        return self


class ScriptSnapshot(Snapshot):
    """ Generate a .ls _script. Ignore _power on/off. """
    def __init__(self):
        self._light_name = ''
        self._power = True
        self._script = ''

    def start_snapshot(self):
        self._script = 'duration 1500\n'

    def start_light(self, light):
        self._light_name = light.get_label()

    def handle_setting(self, name, value):
        self._script += '{} {} '.format(name, value)

    def handle_color(self, color):
        params = zip([
            TokenTypes.HUE, TokenTypes.SATURATION, TokenTypes.BRIGHTNESS,
            TokenTypes.KELVIN
            ], color)
        units = Units()
        for param in params:
            reg, value = param
            fmt = '{} {:.2f} ' if units.requires_conversion(reg) else '{} {} '
            self._script += fmt.format(
                reg.name.lower(), units.as_logical(reg, value))

    def handle_power(self, power):
        self._power = power

    def end_light(self):
        self._script += 'set "{}"\n'.format(self._light_name)
        fmt = 'on "{}"\n' if self._power else 'off "{}"\n'
        self._script += fmt.format(self._light_name)

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
        self._light_name = light.get_label()

    def handle_setting(self, name, value):
        self._snapshot += 'OpCode.set_reg, "{}", {},\n'.format(
            name, _quote_if_string(value))

    def handle_power(self, power):
        self._power = power

    def end_light(self):
        self._snapshot += 'OpCode.set_reg, "_name", "{}",\n'.format(
            self._light_name)
        self._snapshot += 'OpCode.set_reg, "operand", Operand.light,\n'
        self._snapshot += 'OpCode.color,\n'
        self._snapshot += 'OpCode.set_reg, "power", {},\n'.format(self._power)
        self._snapshot += 'OpCode.power,\n'

    @property
    def text(self):
        return self._snapshot[:-2]


class TextSnapshot(Snapshot):
    """ Generate plain text. """
    def __init__(self):
        self._field_width = len('saturation  ')
        self._text = ''
        self._add_field('name')._add_field('hue')
        self._add_field('saturation')._add_field('brightness')
        self._add_field('kelvin')._add_field('power')
        self._text += '\n'
        self._text += '-' * ((self._field_width - 1) * 6)
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
        self._text += '-' * 17
        self._text += '\n'
        for name in names:
            self._text += '{}\n'.format(name)
            for light in get_fn(name):
                self._text += '   {}\n'.format(light.get_label())

    def generate(self):
        super().generate()
        self._add_sets()
        return self

    def start_light(self, light):
        self._add_field(light.get_label())

    def handle_color(self, color):
        params = zip([
            TokenTypes.HUE, TokenTypes.SATURATION, TokenTypes.BRIGHTNESS,
            TokenTypes.KELVIN
            ], color)
        units = Units()
        for param in params:
            self._add_field(
                '{:>6.2f}'.format(units.as_logical(param[0], param[1])))

    def handle_power(self, power):
        self._add_field('{:>5d}'.format(power))

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
        self._current_dict = {'_name': light.get_label()}

    def handle_setting(self, name, value):
        self._current_dict[name] = value

    def end_light(self):
        self._snapshot.append(self._current_dict)

    @property
    def text(self):
        return str(self.list)

    @property
    def list(self):
        return self._snapshot


def _do_gen(ctor):
    print(ctor().generate().text + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-l', '--list', help='output instruction list', action='store_true')
    parser.add_argument(
        '-d', '--dict', help='output dictionary format', action='store_true')
    parser.add_argument(
        '-p', '--py', help='output Python file', action='store_true')
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
    settings.using_base(config_values.functional).and_override(
        {'single_light_discover': True}).configure()
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
        text = InstructionSnapshot().generate().text
        Compiler().generate_from(text)


if __name__ == '__main__':
    main()
