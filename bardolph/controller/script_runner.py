import logging

from ..lib.job_control import Job
from .machine import Machine
from ..parser.parse import Parser


class ScriptRunner(Job):
    def __init__(self):
        self.program = None
        self.parser = Parser()
        self.vm = Machine()
        
    @classmethod
    def from_file(cls, file_name):
        new_instance = ScriptRunner()
        new_instance.load_file(file_name)
        return new_instance
        
    def load_file(self, file_name):
        self.program = self.parser.load(file_name)
        if self.program == None:
            logging.error(self.parser.get_errors())
        return self.program
    
    def load_string(self, input_string):
        self.program = self.parser.parse(input_string)
        if self.program == None:
            logging.error(self.parser.get_errors())
        return self.program
        
    def execute(self):
        if self.program != None:
            self.vm.run(self.program)

    def request_stop(self):
        self.vm.stop()