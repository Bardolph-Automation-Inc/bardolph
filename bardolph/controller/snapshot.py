#!/usr/bin/env python

import argparse
import re

from bardolph.controller import (arg_helper, config_values, i_controller,
                                 light_module)
from bardolph.controller.i_controller import LightSet
from bardolph.lib import injection, settings
from bardolph.parser.parse import Parser
from bardolph.vm.vm_codes import Register


class Snapshot:
    def __init__(self):
        self._text = None
        self._brief = False

    def start_snapshot(self):
        self._text = ''

    def append(self, text):
        self._text += text

    @property
    def text(self):
        return self._text

    def start_light(self, light): pass
    def setting(self, name, value): pass
    def power(self, power): pass
    def end_light(self, light): pass
    def start_multizone(self, light): pass
    def zone(self, light, number, color): pass
    def end_multizone(self, light): pass
    def matrix_cell(self, row, column, color): pass
    def end_matrix(self, light): pass

    def color(self, raw_color):
        self.setting(Register.HUE, raw_color[0])
        self.setting(Register.SATURATION, raw_color[1])
        self.setting(Register.BRIGHTNESS, raw_color[2])
        self.setting(Register.KELVIN, raw_color[3])

    def light(self, light):
        self.color(light.get_color())

    def multizone(self, light):
        for number, color in enumerate(light.get_zone_colors()):
            self.zone(light, number, color)

    def matrix(self, light):
        light_matrix = light.get_matrix()
        mat = light_matrix.matrix
        for row in range(0, light_matrix.height):
            for column in range(0, light_matrix.width):
                self.matrix_cell(row, column, mat[row][column])

    @injection.inject(LightSet)
    def generate(self, filter, light_set):
        self.start_snapshot()
        any_found = False
        for name in light_set.get_light_names():
            if filter is None:
                include = True
            elif isinstance(filter, str):
                include = name == filter
            else:
                include = filter.match(name) is not None

            if include:
                any_found = True
                light = light_set.get_light(name)
                if isinstance(light, i_controller.MultizoneLight):
                    self.start_multizone(light)
                    self.multizone(light)
                    self.end_multizone(light)
                elif isinstance(light, i_controller.MatrixLight):
                    self.start_matrix(light)
                    self.matrix(light)
                    self.end_matrix(light)
                else:
                    self.start_light(light)
                    self.light(light)
                    self.power(light)
                    self.end_light(light)

        if not any_found:
            self.append('No lights found.\n')
        return self


class ScriptSnapshot(Snapshot):
    def start_snapshot(self):
        super().start_snapshot()
        self._text += 'units raw duration 1000\n'

    def setting(self, reg, value):
        self.append('{} {:.0f} '.format(reg.name.lower(), value))

    def end_light(self, light):
        self.append('set "{}"\n'.format(light.get_name()))

    def zone(self, light, number, raw_color):
        self.color(raw_color)
        self.append('set "{}" zone {}\n'.format(light.get_name(), number))

    def start_matrix(self, light):
        self.append('set "{}" begin\n'.format(light.get_name()))

    def matrix_cell(self, row, column, raw_color):
        self.color(raw_color)
        self.append('stage row {} column {}\n'.format(row, column))

    def end_matrix(self, light):
        self.append('end\n')

    def power(self, light):
        fmt = 'on "{}"\n' if light.get_power() else 'off "{}"\n'
        self.append(fmt.format(light.get_name()))


class InstructionSnapshot(Snapshot):
    def generate(self, name):
        self.start_snapshot()
        script_snapshot = ScriptSnapshot()
        script_snapshot.generate(name)
        parser = Parser()
        if parser.parse(script_snapshot.text):
            for inst in parser.get_program():
                self.append(str(inst) + '\n')
            return self


class NameSnapshot(Snapshot):
    def start_light(self, light):
        self.append(light.get_name() + '\n')

    def start_multizone(self, light):
        self.start_light(light)

    def start_matrix(self, light):
        self.start_light(light)


class TextSnapshot(Snapshot):
    def __init__(self):
        super().__init__()
        self._field_width = 15

    def start_snapshot(self):
        super().start_snapshot()
        if not self._brief:
            self._add_field('name ')._add_field(' hue')
            self._add_field(' sat')._add_field(' brt')
            self._add_field(' kel')._add_field('power')
            self.append('\n')
            self.append('-' * ((self._field_width) * 6 - 5))
            self.append('\n')

    def _add_field(self, data):
        self.append(str(data).ljust(self._field_width))
        return self

    def _nl(self):
        self.append('\n')

    @injection.inject(LightSet)
    def _add_sets(self, filter, light_set):
        self._add_set(
            'Groups', light_set.get_group_names(),
            light_set.get_group_lights,
            filter)
        self._add_set(
            'Locations', light_set.get_location_names(),
            light_set.get_location_lights,
            filter)

    def _add_set(self, heading, set_names, get_fn, filter=None):
        self.append('\n{}\n'.format(heading))
        self.append('-' * 15)
        self._nl()
        for set_name in set_names:
            light_names = get_fn(set_name)
            if filter is None or filter in light_names:
                self.append('{}\n'.format(set_name))
                for light_name in light_names:
                    self.append('    {}\n'.format(light_name))

    def generate(self, filter):
        if super().generate(filter):
            self._add_sets(filter)
        return self

    def start_light(self, light):
        self._add_field(light.get_name())

    def setting(self, _, value):
        self._add_field('{:>4.0f}'.format(value))

    def start_multizone(self, light):
        self.start_light(light)
        layout = '{:>' + str(self._field_width * 4 + 1) + '}'
        self.append(layout.format(light.get_power()))
        self.append('\n   Zone\n')

    def zone(self, _, number, raw_color):
        self._add_field('{:>5d}'.format(number))
        self.color(raw_color)
        self._nl()

    def end_zones(self, _):
        self._nl()

    def start_matrix(self, light):
        self.start_light(light)
        for spacer in range(0, 4):
            self._add_field(' ')
        self.power(light)
        self._nl()

    def matrix(self, light):
        light_matrix = light.get_matrix()
        mat = light_matrix.matrix
        for row in range(0, light_matrix.height):
            for col in range(0, light_matrix.width):
                self._add_field('   {:1d} {:1d}'.format(row, col))
                self.color(mat[row][col])
                self._nl()

    def power(self, light):
        self._add_field('{:d}'.format(light.get_power()))

    def end_light(self, _):
        self._nl()


def _do_gen(ctor, filter):
    print(ctor().generate(filter).text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-b', '--brief', help='list names only', action='store_true')
    parser.add_argument(
        '-f', '--use-fakes', help='use fake lights', action='store_true')
    parser.add_argument(
        '-i', '--inst', help='output instruction list', action='store_true')
    parser.add_argument(
        '-r', '--regex',
        help='treat the light name as a regular expression',
        action='store_true')
    arg_helper.add_n_argument(parser)
    parser.add_argument(
        '-s', '--script', help='output script format', action='store_true')
    parser.add_argument(
        '-t', '--text', help='output text format', action='store_true')
    parser.add_argument('name',
                        help='Light name, or all lights if no name is given.',
                        nargs='?')
    args = parser.parse_args()

    do_brief = args.brief
    do_inst = args.inst
    do_script = args.script
    do_text = args.text or (not (do_script or do_inst or do_brief))

    injection.configure()
    settings_conf = settings.using(
        config_values.functional).add_overrides({'single_light_discover': True})
    settings_conf.apply_env()

    if args.use_fakes:
        settings_conf.add_overrides({'use_fakes': True})
    n_arg = arg_helper.get_overrides(args)
    if n_arg is not None:
        settings_conf.add_overrides(n_arg)
    settings_conf.configure()
    light_module.configure()

    try:
        name = args.name
        if name is not None and args.regex:
            name = re.compile(name)
        if do_brief:
            _do_gen(NameSnapshot, name)
        if do_text:
            _do_gen(TextSnapshot, name)
        if do_script:
            _do_gen(ScriptSnapshot, name)
        if do_inst:
            _do_gen(InstructionSnapshot, name)
    except re.error as ex:
        print('Regular expression error: {}'.format(ex))


if __name__ == '__main__':
    main()