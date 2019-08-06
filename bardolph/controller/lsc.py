#!/usr/bin/env python

import argparse
import os
import stat

from ..lib import injection
from ..lib import settings

from . import config_values
from .script_runner import ScriptRunner

class Compiler:      
    def generate(self, file_name):
        program = ScriptRunner.from_file(file_name).program
        text = ",\n".join(map(lambda inst: inst.as_list_text(), program))
        self.generate_from(text)
        
    def generate_from(self, instruction_text):
        output = ""
        with open(os.path.join('controller', 'lsc_template.py')) as f:
            for line in f:
                if line.find("#instructions") > -1:
                    output += instruction_text
                else:
                    output += line

        output_name = '__generated__.py'
        out_file = open(output_name, 'w')
        out_file.write(output)
        out_file.close()
        os.chmod(output_name, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", help="name of the script file", nargs='+')
    args = ap.parse_args()
    
    injection.configure()   
    settings.using_base(config_values.functional).configure()
    
    compiler = Compiler()
    for file_name in args.file:
        print(file_name)
        compiler.generate(file_name)

if __name__=="__main__":
    main()

