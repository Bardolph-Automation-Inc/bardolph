#!/usr/bin/env python

import argparse
import os
import stat

from . import arg_helper
from ..lib import injection
from ..lib import settings
from ..parser.parse import Parser

from . import config_values

def program_code(instructions):
    output = ''
    with open(os.path.join(
            'bardolph', 'controller', 'lsc_template.py')) as srce:
        for line in srce:
            if line.find('#instructions') > -1:
                output += instructions
            else:
                output += line
    return output
    
def instruction_text(file_name):
    program = Parser().load(file_name)
    if program is None:
        return None
    return ',\n'.join(map(lambda inst: inst.as_list_text(), program))

def output_python(output_text, output_name=None):
    if output_name is None:
        print(output_text)
    else:
        out_file = open(output_name, 'w')
        out_file.write(output_text)
        out_file.close()
        os.chmod(output_name, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='name of the script file')
    arg_helper.add_o_argument(parser)
    args = parser.parse_args()

    injection.configure()
    settings.use_base(config_values.functional).configure()

    input_file = args.file
    print(input_file) 
    program = instruction_text(input_file)
    if program is not None:
        output_python(program_code(program), arg_helper.get_output_file(args))

if __name__ == '__main__':
    main()
