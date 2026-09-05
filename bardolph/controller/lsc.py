#!/usr/bin/env python

import argparse
from pathlib import Path

from bardolph.controller import config_values
from bardolph.lib import injection, settings
from bardolph.parser.parse import Parser
from bardolph.runtime import runtime_module


def program_code(instructions):
    output = ''
    path = Path(__file__).resolve().parent / 'lsc_template.py'
    with path.open("r", encoding="utf-8") as srce:
        for line in srce:
            if line.find('#instructions') > -1:
                output += instructions
            else:
                output += line
    return output


def instruction_text(file_name):
    parser = Parser()
    if not parser.parse_file(Path(file_name)):
        print("Error compiling {}".format(file_name))
        print(parser.get_errors())
        return None

    program = parser.get_program()
    text = '    '
    text += ',\n    '.join(inst.ctor() for inst in program)
    return text


def output_python(output_text, output_name=None):
    if output_name is None:
        print(output_text)
    else:
        path = Path(output_name)
        path.write_text(output_text)
        path.chmod(0o644)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output-file', help="name of the output file")
    parser.add_argument('file', help='name of the script file')
    args = parser.parse_args()

    injection.configure()
    settings.using(config_values.functional).apply_env().configure()
    runtime_module.configure()

    input_file = args.file
    program = instruction_text(input_file)
    if program is not None:
        output_python(program_code(program), args.output_file)


if __name__ == '__main__':
    main()
