import logging

from bardolph.lib.job_control import Job
from bardolph.vm.machine import Machine, MachineState, Registers
from bardolph.parser.parse import Parser


class ScriptJob(Job):
    def __init__(self):
        super().__init__()
        self._program = None
        self._parser = Parser()
        self._machine = Machine()

    @staticmethod
    def from_file(file_name):
        new_instance = ScriptJob()
        new_instance.load_file(file_name)
        return new_instance

    @staticmethod
    def from_string(script):
        new_instance = ScriptJob()
        new_instance.load_string(script)
        return new_instance

    def load_file(self, file_name):
        self._program = self._parser.load(file_name)
        if self._program is None:
            logging.error(
                "{}, {}".format(file_name, self._parser.get_errors()))
        return self._program

    def load_string(self, input_string):
        self._program = self._parser.parse(input_string)
        if self._program is None:
            logging.error(self._parser.get_errors())
        return self._program

    @property
    def program(self):
        return self._program

    @property
    def compile_errors(self):
        return self._parser.get_errors()

    def get_machine_state(self) -> MachineState:
        return self._machine.get_state()

    def execute(self):
        if self._program is not None:
            self._machine.reset()
            self._machine.run(self._program)

    def request_stop(self):
        self._machine.stop()
